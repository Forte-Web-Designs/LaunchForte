/* ============================================================
   Ask Forte v2 — a drawing that happens to talk.
   Spec of record: ASK FORTE v2: PAGE REBUILD SPEC (2026-08-25).
   Supersedes v1.

   One component, two mounts. Script is a no-op on pages without
   #askf-chat.

   Endpoints:
     POST /forte-ask    - streaming; body: {session_id?, message, meta}
     POST /forte-draw   - drawing; body: {session_id}
                          returns {sketch_svg, proof, unchanged?, scar?}
     POST /gate-request - packet request; body: {tool_key:"bot", email, session_id}
   (v1's /forte-shape fetch is retired; PRODUCTS map is client-side.)
   ============================================================ */
(function () {
    /* -------------------- config -------------------- */
    var LIVE = true;
    var API_BASE = "https://launchforte.app.n8n.cloud/webhook";
    var ASK = API_BASE + "/forte-ask";
    var DRAW = API_BASE + "/forte-draw";
    var GATE = API_BASE + "/gate-request";

    var ALLOWANCE_MESSAGES = 10;      // 10 edits to the drawing
    var KEEP_UNLOCK_AT = 3;           // remaining when the keep moment unlocks
    var CHAR_CAP = 1000;
    var CHAR_DELAY_MS = 28;
    var PUNCT_EXTRA_MS = 140;

    // Pen animation schedule (v1's schedule, verbatim). Each pair is
    // [beatIndex, msBeforeNextBeatStarts]. Total run about 4.4 seconds.
    // Do not speed it up.
    var BEATS = [[0, 400], [1, 900], [2, 500], [3, 700], [4, 500], [5, 600], [6, 900]];
    var BEAT_STROKE_MS = 620;         // per-path draw duration
    var BEAT_STAGGER_MS = 60;         // between paths inside one beat
    var LABEL_FADE_MS = 260;
    var LABEL_DELAY_MS = 120;         // after its path begins
    var GROWTH_STROKE_MS = 220;
    var GROWTH_STAGGER_MS = 140;
    var REMOVE_FADE_MS = 300;

    // Rotation of sample drawings on load (until first user message)
    var ROTATION_HOLD_MS = 2200;
    var ROTATION_FADE_MS = 700;
    // Each sample: [file path, product name for the caption]
    var ROTATION_SAMPLES = [
        ["/samples/lead-routing.svg",         "The Lead Router"],
        ["/samples/books-reconciliation.svg", "The Reconciliation Build"],
        ["/samples/scheduling.svg",           "The Booking System"],
        ["/samples/reporting.svg",            "The Numbers Board"],
        ["/samples/system-sync.svg",          "The Bridge"]
    ];

    /* -------------------- COPY of record --------------------
       Every visitor-readable string in one block. Voice-scanned.
       Banned: em dashes, rule-of-three lists, contrast framing,
       Latin abbreviations, "napkin", "sketch", any dollar sign. */
    var COPY = {
        opener: "What is going on in your business right now? Explain it your way and I will map out how it would work.",
        placeholder_long: "Type here.",
        placeholder_med: "Type here.",
        placeholder_short: "Type here.",
        capped_placeholder: "That is my free brain for today.",
        canvas_heading: "How it would work",
        canvas_footer_note: "This is me thinking out loud. The audit is me measuring.",
        allowance_label: function (n) { return n === 1 ? "1 change left" : n + " changes left"; },
        keep_prompt_default: "Drop your email and I will map it out for you.",
        keep_prompt_close: "That is my free brain for today. The audit is the unlimited version, or drop your email and I will map it out for you.",
        gate_button: "Send it to me",
        gate_email_placeholder: "you@company.com",
        gate_ok: "Got it. Drawing your map now.",
        gate_err_email: "That does not look like an email address.",
        gate_err_send: "Something on my side is off. Try again in a minute.",
        gate_sending: "Sending.",
        ask_err: "Something on my side is off. Try again in a minute, or email seth@launchforte.com and I will answer it myself.",
        draw_stalled_status: "the pen slipped. one more try.",
        draw_stalled_final: "The drawing stalled on my end. Leave your email and I will send it once it is back.",
        cap_hit_html: 'Shoot me an email at <a href="mailto:seth@launchforte.com">seth@launchforte.com</a> or <a href="https://calendly.com/seth-launchforte/30min" target="_blank" rel="noopener">book a call</a> to keep this going.',
        parts_intro: function (n) { return n === 1 ? "1 part." : n + " parts."; },
        role_words: {
            connection: "getting two systems talking",
            config: "setup inside a tool you already have",
            decision: "something that has to decide",
            surface: "a dashboard or a report",
            risk: "anything that moves money or records"
        },
        proof_cta: "See it live"
    };

    /* -------------------- PRODUCTS map (v2 sentinel grammar) --------------------
       Model emits [[SHAPE|slug]]. The page holds the canonical product name so the
       model can never mistype it. If a slug arrives that is not mapped, the reply
       still streams as normal text; the SHAPE marker is dropped silently and a
       console warning is logged for diagnostics. */
    var PRODUCTS = {
        "storefront-upsell": "The Upsell Engine",
        "books-reconciliation": "The Reconciliation Build",
        "scheduling": "The Booking System",
        "reporting": "The Numbers Board",
        "system-sync": "The Bridge",
        "lead-routing": "The Lead Router",
        "data-collection": "The Intake Build",
        "client-onboarding": "The First Week",
        "alerting": "The Watch",
        "voice-agent-intake": "The After Hours Line",
        "platform-migration": "The Migration Build",
        "approval-routing": "The Sign Off",
        "production-takeover": "The Takeover",
        "document-assembly": "The Paperwork Run"
    };

    /* -------------------- helpers -------------------- */
    var $ = function (id) { return document.getElementById(id); };
    function el(tag, cls) { var n = document.createElement(tag); if (cls) n.className = cls; return n; }
    function scrollLog() { var log = $("askf-log"); if (log) log.scrollTop = log.scrollHeight; }
    function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

    /* -------------------- state -------------------- */
    function mintSessionId() {
        var rand = Math.floor(Math.random() * 1e12).toString(36);
        return 'bot-' + rand + '-' + Date.now().toString(36).slice(-4);
    }
    var session = {
        id: null,
        changeCount: 0,
        closed: false,
        keepUnlocked: false,
        currentShape: null,
        currentTrade: null,
        emailCaptured: false,   // gate-before-draw: draw only fires after this is true
        pendingDraw: false      // an unfulfilled [[DRAW]] is waiting for email
    };
    var busy = false;

    // Canvas node registry for the diff engine. Keys are data-node-id;
    // values are { role, groupClone } so we can honor keep-position semantics.
    var canvasNodes = {};

    /* -------------------- init -------------------- */
    function init() {
        if (!$("askf-chat")) return;
        if (!LIVE) {
            var holding = $("askf-holding");
            if (holding) holding.classList.remove("askf-hide");
            var log = $("askf-log"); if (log) log.classList.add("askf-hide");
            var composer = $("askf-composer"); if (composer) composer.classList.add("askf-hide");
            return;
        }
        prefill();
        wireInput();
        wireMic();
        wireGate();

        var pre = new URLSearchParams(location.search).get("q");
        if (pre) {
            sendMessage(pre.slice(0, CHAR_CAP), { prefill: true });
        } else {
            renderBotBubble(COPY.opener, { instant: true });
            // Start the rotation on the empty canvas so it teaches the
            // catalog while the visitor decides what to say. The rotation
            // stops permanently the moment they send their first message.
            startRotation();
        }
        updateAllowance();
    }

    function prefill() {
        var q = new URLSearchParams(location.search).get("q");
        if (q && $("askf-input")) $("askf-input").value = q.slice(0, CHAR_CAP);
        updateCharCount();
    }

    /* -------------------- input UX -------------------- */
    function applyPlaceholder() {
        var input = $("askf-input"); if (!input) return;
        var w = window.innerWidth;
        input.setAttribute("placeholder", w < 480 ? COPY.placeholder_short : w < 640 ? COPY.placeholder_med : COPY.placeholder_long);
    }
    function wireInput() {
        var input = $("askf-input");
        var send = $("askf-send");
        if (!input || !send) return;
        applyPlaceholder();
        var pht;
        window.addEventListener("resize", function () {
            clearTimeout(pht);
            pht = setTimeout(applyPlaceholder, 100);
        }, { passive: true });
        input.addEventListener("input", function () {
            autoGrow(input);
            updateCharCount();
        });
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey && !send.disabled) { e.preventDefault(); trySend(); }
        });
        send.addEventListener("click", trySend);
    }
    function autoGrow(t) {
        t.style.height = 'auto';
        var natural = t.scrollHeight;
        var target = natural <= 48 ? 44 : Math.min(140, natural);
        t.style.height = target + 'px';
    }
    function updateCharCount() {
        var input = $("askf-input"); if (!input) return;
        var v = input.value;
        var cel = $("askf-charcount");
        if (cel) {
            cel.textContent = v.length + " / " + CHAR_CAP;
            cel.classList.toggle("warn", v.length >= CHAR_CAP);
        }
        var send = $("askf-send");
        if (send) send.disabled = v.trim().length < 3 || busy || session.closed;
    }
    function trySend() {
        var input = $("askf-input"); if (!input) return;
        var v = input.value.trim();
        if (v.length < 3 || busy || session.closed) return;
        input.value = "";
        autoGrow(input);
        updateCharCount();
        sendMessage(v);
    }

    /* -------------------- voice input -------------------- */
    function wireMic() {
        var Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
        var mic = $("askf-mic");
        if (!Rec || !mic) return;
        mic.classList.add("available");
        var recognizer = new Rec();
        recognizer.continuous = true;
        recognizer.interimResults = true;
        recognizer.lang = "en-US";
        var recording = false;
        var baseText = "";
        mic.addEventListener("click", function () {
            if (recording) { recognizer.stop(); return; }
            baseText = $("askf-input").value;
            try { recognizer.start(); } catch (_) { return; }
        });
        recognizer.onstart = function () { recording = true; mic.classList.add("recording"); mic.setAttribute("aria-label", "Stop recording"); };
        recognizer.onend = function () { recording = false; mic.classList.remove("recording"); mic.setAttribute("aria-label", "Speak your message"); };
        recognizer.onerror = function () { recording = false; mic.classList.remove("recording"); };
        recognizer.onresult = function (e) {
            var chunk = "";
            for (var i = e.resultIndex; i < e.results.length; i++) chunk += e.results[i][0].transcript;
            var input = $("askf-input");
            input.value = (baseText ? baseText + " " : "") + chunk;
            input.value = input.value.slice(0, CHAR_CAP);
            autoGrow(input);
            updateCharCount();
        };
    }

    /* -------------------- render bubbles -------------------- */
    function renderUserBubble(text) {
        var t = el("div", "askf-turn user");
        var b = el("div", "askf-bubble");
        b.textContent = text;
        t.appendChild(b);
        $("askf-log").appendChild(t);
        scrollLog();
    }
    function renderBotBubble(text, opts) {
        opts = opts || {};
        var t = el("div", "askf-turn bot");
        var b = el("div", "askf-bubble");
        if (opts.html) b.innerHTML = text;
        else if (opts.instant) b.textContent = text;
        t.appendChild(b);
        $("askf-log").appendChild(t);
        scrollLog();
        return { turn: t, bubble: b };
    }
    function renderTypingIndicator() {
        var t = el("div", "askf-turn bot");
        var b = el("div", "askf-typing");
        b.appendChild(el("span")); b.appendChild(el("span")); b.appendChild(el("span"));
        t.appendChild(b);
        $("askf-log").appendChild(t);
        scrollLog();
        return t;
    }

    /* -------------------- allowance / close -------------------- */
    function remainingChanges() { return Math.max(0, ALLOWANCE_MESSAGES - session.changeCount); }
    function updateAllowance() {
        var el = $("askf-allowance"); if (!el) return;
        el.textContent = COPY.allowance_label(remainingChanges());
    }
    function closeSession() {
        session.closed = true;
        var send = $("askf-send"); if (send) send.disabled = true;
        var input = $("askf-input");
        if (input) { input.disabled = true; input.placeholder = COPY.capped_placeholder; }
        renderBotBubble(COPY.cap_hit_html, { html: true });
        openKeepMoment(true);
        updateAllowance();
    }

    /* -------------------- keep moment / gate -------------------- */
    function openKeepMoment(atCap) {
        var gate = $("askf-gate");
        var msg = $("askf-gate-msg");
        if (!gate) return;
        if (gate.classList.contains("open") && !atCap) return;
        gate.classList.add("open");
        if (msg) {
            msg.textContent = atCap ? COPY.keep_prompt_close : COPY.keep_prompt_default;
            msg.classList.add("askf-gate-prompt");
        }
        session.keepUnlocked = true;
        var email = $("askf-gate-email");
        if (email && !atCap) { try { email.focus({ preventScroll: false }); } catch (_) { } }
    }
    function wireGate() {
        var btn = $("askf-gate-send"); if (!btn) return;
        btn.textContent = COPY.gate_button;
        var emailInput = $("askf-gate-email");
        if (emailInput) emailInput.placeholder = COPY.gate_email_placeholder;
        btn.addEventListener("click", function () {
            var email = emailInput ? emailInput.value.trim() : "";
            var msg = $("askf-gate-msg");
            if (msg) msg.classList.remove("ok", "err");
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                if (msg) { msg.classList.add("err"); msg.textContent = COPY.gate_err_email; }
                return;
            }
            btn.disabled = true;
            if (msg) msg.textContent = COPY.gate_sending;
            fetch(GATE, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tool_key: "bot", email: email, session_id: session.id })
            }).then(function (r) {
                if (!r.ok) throw new Error("gate " + r.status);
                if (msg) { msg.classList.add("ok"); msg.textContent = COPY.gate_ok; }
                if (window.dataLayer) window.dataLayer.push({ event: "fortebot_email_sent" });
                session.emailCaptured = true;
                // If a draw was waiting on the gate, fire it now. Close the
                // gate visually after a short beat so the "on its way" message
                // gets a moment to read.
                if (session.pendingDraw) {
                    session.pendingDraw = false;
                    setTimeout(function () {
                        var gate = $("askf-gate");
                        if (gate) gate.classList.remove("open");
                        drawCanvas();
                    }, 900);
                }
            }).catch(function () {
                if (msg) { msg.classList.add("err"); msg.textContent = COPY.gate_err_send; }
                btn.disabled = false;
            });
        });
    }

    /* -------------------- sentinel adapter --------------------
       Grammar v2:
         [[SHAPE|<slug>]]  → look up PRODUCTS map; set current shape
         [[TRADE|<slug>]]  → set current trade (proof pref)
         [[DRAW]]          → after stream ends, POST /forte-draw
         [[CLOSE]]         → unlock the keep moment (does not open by itself)
         [[DEFLECT]]       → wipe bubble, render served refusal, block remaining tokens
       Split-across-chunks handled via `carry`. */
    function parseSentinels(chunkText, carry) {
        var buf = (carry || "") + chunkText;
        var frames = [];
        var re = /\[\[([^\[\]]+)\]\]/g;
        var lastIndex = 0;
        var m;
        while ((m = re.exec(buf)) !== null) {
            var pre = buf.slice(lastIndex, m.index);
            if (pre) frames.push({ type: "token", text: pre });
            var body = m[1].trim();
            if (body.indexOf("SHAPE|") === 0) {
                var s = body.slice(6).trim();
                if (s) frames.push({ type: "shape", slug: s });
            } else if (body.indexOf("TRADE|") === 0) {
                var t = body.slice(6).trim();
                if (t) frames.push({ type: "trade", slug: t });
            } else if (body === "DRAW") {
                frames.push({ type: "draw" });
            } else if (body === "CLOSE") {
                frames.push({ type: "close" });
            } else if (body === "DEFLECT") {
                frames.push({ type: "deflect" });
            }
            lastIndex = re.lastIndex;
        }
        var tail = buf.slice(lastIndex);
        var openIdx = tail.lastIndexOf("[[");
        var carryOut = "";
        var emitTail = tail;
        if (openIdx !== -1 && tail.indexOf("]]", openIdx) === -1) {
            emitTail = tail.slice(0, openIdx);
            carryOut = tail.slice(openIdx);
        }
        if (!carryOut && emitTail.charAt(emitTail.length - 1) === "[") {
            carryOut = "[";
            emitTail = emitTail.slice(0, -1);
        }
        if (emitTail) frames.push({ type: "token", text: emitTail });
        return { frames: frames, carry: carryOut };
    }

    /* -------------------- streaming send -------------------- */
    function sendMessage(text, opts) {
        opts = opts || {};
        if (session.closed || busy) return;
        // First message ever: stop the rotation and clear the canvas so the
        // live surface takes over from an empty slate. Their drawing must
        // never appear to start from somebody else's.
        stopRotation({ clearCanvas: true });
        busy = true;
        var send = $("askf-send"); if (send) send.disabled = true;
        renderUserBubble(text);
        // Decrement the allowance right when the visitor spends a message.
        // 10 = messages, visible from the first send. (Overrides an earlier
        // ruling that decremented only on visible drawing change.)
        session.changeCount += 1;
        updateAllowance();

        var typing = renderTypingIndicator();
        var botHolder = null;
        var accumulated = "";
        var wasDeflected = false;
        var wantDraw = false;

        if (!session.id) session.id = mintSessionId();
        var payload = { session_id: session.id, message: text, meta: { referrer: document.referrer, prefill: !!opts.prefill } };

        fetch(ASK, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        }).then(function (resp) {
            if (!resp.ok) throw new Error("ask " + resp.status);
            var newId = resp.headers.get("X-Forte-Session") || resp.headers.get("x-forte-session");
            if (newId && !session.id) session.id = newId;

            var reader = resp.body.getReader();
            var decoder = new TextDecoder();
            var lineBuf = "";
            var carry = "";
            var streamEnded = false;
            var sawAnyContent = false;

            function pump() {
                return reader.read().then(function (res) {
                    if (res.done) {
                        if (lineBuf) { processLine(lineBuf); lineBuf = ""; }
                        if (carry) { handleFrame({ type: "token", text: carry }); carry = ""; }
                        finish();
                        return;
                    }
                    if (streamEnded) { finish(); return; }
                    lineBuf += decoder.decode(res.value, { stream: true });
                    var lines = lineBuf.split("\n");
                    lineBuf = lines.pop();
                    var textOut = "";
                    for (var i = 0; i < lines.length; i++) {
                        var contentPart = processLine(lines[i]);
                        if (contentPart) textOut += contentPart;
                    }
                    if (textOut) {
                        sawAnyContent = true;
                        var out = parseSentinels(textOut, carry);
                        carry = out.carry;
                        for (var j = 0; j < out.frames.length; j++) handleFrame(out.frames[j]);
                    }
                    return pump();
                });
            }

            function processLine(line) {
                var trimmed = line.replace(/^data:\s*/, "").trim();
                if (!trimmed) return "";
                if (trimmed.charAt(0) === "{") {
                    try {
                        var obj = JSON.parse(trimmed);
                        if (obj.type === "begin") return "";
                        if (obj.type === "end") { streamEnded = true; return ""; }
                        if (obj.type === "item") return typeof obj.content === "string" ? obj.content : "";
                        if (typeof obj.content === "string") return obj.content;
                        if (typeof obj.text === "string") return obj.text;
                        if (typeof obj.token === "string") return obj.token;
                        if (typeof obj.delta === "string") return obj.delta;
                        return "";
                    } catch (_) { return trimmed; }
                }
                return trimmed;
            }

            /* Token pacer — n8n emits in bursts, we render at ~35 chars/sec so
               it reads as natural typing. Do not touch these constants. */
            var pendingChars = [];
            var streamDone = false;
            var pacing = false;

            function ensureBotBubble() {
                if (!botHolder) {
                    if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
                    typing = null;
                    botHolder = renderBotBubble("", {});
                }
            }
            function startPacer() { if (pacing) return; pacing = true; pace(); }
            function pace() {
                if (!botHolder) { pacing = false; return; }
                if (pendingChars.length) {
                    var ch = pendingChars.shift();
                    accumulated += ch;
                    botHolder.bubble.textContent = accumulated;
                    scrollLog();
                    var extra = (ch === '.' || ch === '?' || ch === '!' || ch === '\n') ? PUNCT_EXTRA_MS : 0;
                    setTimeout(pace, CHAR_DELAY_MS + extra);
                    return;
                }
                if (streamDone) { pacing = false; finalizeReply(); }
                else { pacing = false; }
            }
            function pushToken(text) {
                for (var i = 0; i < text.length; i++) pendingChars.push(text.charAt(i));
                startPacer();
            }

            function handleFrame(f) {
                if (f.type === "token") {
                    if (wasDeflected) return;
                    ensureBotBubble();
                    pushToken(f.text);
                }
                else if (f.type === "shape") {
                    var name = PRODUCTS[f.slug];
                    if (name) { session.currentShape = f.slug; }
                    else { if (window.console) console.warn("[askf] unmapped SHAPE slug:", f.slug); }
                }
                else if (f.type === "trade") { session.currentTrade = f.slug; }
                else if (f.type === "draw") { wantDraw = true; }
                else if (f.type === "close") { openKeepMoment(false); }
                else if (f.type === "deflect") {
                    ensureBotBubble();
                    pendingChars.length = 0;
                    accumulated = "";
                    botHolder.bubble.textContent = "";
                    wasDeflected = true;
                    // Model streams the served refusal AFTER the sentinel.
                    scrollLog();
                }
            }
            function finish() {
                if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
                if (!sawAnyContent) {
                    if (window.console) console.info("[askf] empty 200 — treating as daily limit");
                    renderBotBubble(COPY.cap_hit_html, { html: true });
                    closeSession();
                    busy = false;
                    updateCharCount();
                    return;
                }
                streamDone = true;
                if (pendingChars.length > 0) startPacer();
                else finalizeReply();
            }
            function finalizeReply() {
                busy = false;
                updateCharCount();
                if (wantDraw) {
                    // Gate-before-draw: only the model can decide the drawing is
                    // ready. When it is, we either draw immediately (email
                    // already captured earlier in the session) or open the gate
                    // and let the visitor decide. If they refuse, the
                    // conversation continues freely; the next [[DRAW]] on a
                    // later turn will re-open the gate.
                    if (session.emailCaptured) {
                        drawCanvas();
                    } else {
                        session.pendingDraw = true;
                        openKeepMoment(false);
                    }
                }
                else if (session.changeCount >= ALLOWANCE_MESSAGES) closeSession();
            }
            return pump();
        }).catch(function () {
            if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
            renderBotBubble(COPY.ask_err, { instant: true });
            busy = false;
            updateCharCount();
        });
    }

    /* -------------------- pen animation primitives --------------------
       Contract from the flows side, already emitted today:
         - every path carries pathLength="1"
         - every <g> carries data-beat (0..6) and data-role
       When data-node-id lands, all three attributes coexist.
       Reduced motion is handled at CSS + the primitives via prefersReduced(). */

    function prefersReduced() {
        return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    }

    // Prime every path in the given root: dasharray/dashoffset ready to be
    // released. Labels (text/tspan) get opacity 0, ready to fade in.
    function primePenPaths(root) {
        var paths = root.querySelectorAll("path[pathLength], path");
        Array.prototype.forEach.call(paths, function (p) {
            // Rects and circles that carry stroke also get the dashoffset trick
            // via CSS; we prime path specifically since that is the majority case.
            p.style.strokeDasharray = "1";
            p.style.strokeDashoffset = "1";
            p.style.transition = "none";
        });
        var labels = root.querySelectorAll("text, tspan");
        Array.prototype.forEach.call(labels, function (t) {
            t.style.opacity = "0";
            t.style.transition = "none";
        });
    }

    // Release one path with the pen effect at a scheduled delay.
    function penReveal(pathEl, delayMs, durationMs) {
        setTimeout(function () {
            pathEl.style.transition = "stroke-dashoffset " + durationMs + "ms cubic-bezier(.4, 0, .2, 1)";
            pathEl.style.strokeDashoffset = "0";
        }, delayMs);
    }
    // Release one label with fade.
    function labelReveal(textEl, delayMs, durationMs) {
        setTimeout(function () {
            textEl.style.transition = "opacity " + durationMs + "ms ease-out";
            textEl.style.opacity = "1";
        }, delayMs);
    }

    // Play one beat: stagger paths inside its <g> by BEAT_STAGGER_MS,
    // stagger labels among themselves at BEAT_STAGGER_MS. Per the sample SVG
    // spec (2026-08-25 correction): boxes and labels live in SEPARATE beat
    // groups, so labels do NOT wait behind a path in their own group. A
    // label-only beat animates its labels head-on.
    function playBeat(groupEl, startAtMs, durationMs) {
        var paths = groupEl.querySelectorAll("path");
        var labels = groupEl.querySelectorAll("text");
        Array.prototype.forEach.call(paths, function (p, i) {
            penReveal(p, startAtMs + i * BEAT_STAGGER_MS, durationMs || BEAT_STROKE_MS);
        });
        Array.prototype.forEach.call(labels, function (t, i) {
            labelReveal(t, startAtMs + i * BEAT_STAGGER_MS, LABEL_FADE_MS);
        });
    }

    // Play the full BEATS schedule against a mounted SVG.
    // For reduced motion, snap every path/label to final state immediately.
    function playBeatsAgainst(svgRoot) {
        var beatGroups = {};
        svgRoot.querySelectorAll("g[data-beat]").forEach(function (g) {
            var idx = parseInt(g.getAttribute("data-beat"), 10);
            if (isNaN(idx)) return;
            (beatGroups[idx] = beatGroups[idx] || []).push(g);
        });

        if (prefersReduced()) {
            svgRoot.querySelectorAll("path").forEach(function (p) {
                p.style.transition = "none";
                p.style.strokeDashoffset = "0";
            });
            svgRoot.querySelectorAll("text, tspan").forEach(function (t) {
                t.style.transition = "none";
                t.style.opacity = "1";
            });
            return BEATS.reduce(function (acc, pair) { return acc + pair[1]; }, 0);
        }

        var elapsed = 0;
        BEATS.forEach(function (pair) {
            var idx = pair[0], nextGap = pair[1];
            var groups = beatGroups[idx] || [];
            groups.forEach(function (g) {
                playBeat(g, elapsed, BEAT_STROKE_MS);
            });
            elapsed += nextGap;
        });
        return elapsed;
    }

    // GROWTH: fade in / draw a single new node with the pen effect on a
    // compressed schedule (220ms per node, staggered 140ms apart).
    function growNode(groupEl, orderIndex) {
        primePenPaths(groupEl);
        var startAt = orderIndex * GROWTH_STAGGER_MS;
        if (prefersReduced()) {
            groupEl.querySelectorAll("path").forEach(function (p) {
                p.style.transition = "none";
                p.style.strokeDashoffset = "0";
            });
            groupEl.querySelectorAll("text, tspan").forEach(function (t) {
                t.style.transition = "none";
                t.style.opacity = "1";
            });
            return;
        }
        var paths = groupEl.querySelectorAll("path");
        var labels = groupEl.querySelectorAll("text");
        Array.prototype.forEach.call(paths, function (p, i) {
            penReveal(p, startAt + i * 40, GROWTH_STROKE_MS);
        });
        Array.prototype.forEach.call(labels, function (t, i) {
            labelReveal(t, startAt + LABEL_DELAY_MS + i * 40, LABEL_FADE_MS);
        });
    }

    /* -------------------- THINKING loop (during /forte-draw fetch) --------------------
       A single gentle bezier wander, ink color, opacity .4, stroke-width 1.5.
       Draws 900ms, holds 200ms, erases 600ms, loops until the SVG mounts.
       Removed instantly on mount (no crossfade). Never renders under reduced
       motion; the canvas simply stays empty during the fetch. */
    var thinkingHandle = { svg: null, timer: null };
    function startThinking(canvasMount) {
        stopThinking(canvasMount);
        if (prefersReduced()) return;
        var NS = "http://www.w3.org/2000/svg";
        var svg = document.createElementNS(NS, "svg");
        svg.setAttribute("viewBox", "0 0 340 240");
        svg.setAttribute("class", "askf-thinking");
        svg.setAttribute("aria-hidden", "true");
        var p = document.createElementNS(NS, "path");
        p.setAttribute("d", "M60 130 C 100 90, 160 170, 200 120 S 280 140, 300 110");
        p.setAttribute("fill", "none");
        p.setAttribute("stroke", "currentColor");
        p.setAttribute("stroke-width", "1.5");
        p.setAttribute("stroke-linecap", "round");
        p.setAttribute("pathLength", "1");
        p.style.opacity = "0.4";
        p.style.color = "currentColor";
        p.style.strokeDasharray = "1";
        p.style.strokeDashoffset = "1";
        svg.appendChild(p);
        canvasMount.appendChild(svg);
        thinkingHandle.svg = svg;

        function draw() {
            p.style.transition = "stroke-dashoffset 900ms ease-out";
            p.style.strokeDashoffset = "0";
            thinkingHandle.timer = setTimeout(hold, 900);
        }
        function hold() {
            thinkingHandle.timer = setTimeout(erase, 200);
        }
        function erase() {
            p.style.transition = "stroke-dashoffset 600ms ease-in";
            p.style.strokeDashoffset = "1";
            thinkingHandle.timer = setTimeout(function () {
                if (thinkingHandle.svg === svg) draw();
            }, 600);
        }
        requestAnimationFrame(draw);
    }
    function stopThinking(canvasMount) {
        if (thinkingHandle.timer) { clearTimeout(thinkingHandle.timer); thinkingHandle.timer = null; }
        if (thinkingHandle.svg && thinkingHandle.svg.parentNode) {
            thinkingHandle.svg.parentNode.removeChild(thinkingHandle.svg);
        }
        thinkingHandle.svg = null;
    }

    /* -------------------- Homepage ROTATION --------------------
       On load the homepage canvas cycles through ROTATION_SAMPLES so the
       visitor sees the catalog while they decide what to say. Real renderer
       output, five files, no cross-fade, product caption per sample.

       Stops permanently the first time the visitor sends a message (in
       sendMessage). Pauses when the section leaves the viewport or the tab
       is hidden, resumes at the start of the current sample so no half-drawn
       frame appears. Under reduced motion, plays ONE completed sample chosen
       at random and does not cycle. */
    var rotation = {
        active: false,
        paused: false,
        canceled: false,
        mount: null,
        caption: null,
        canvasPane: null,
        cache: {},           // slug -> preloaded SVG text
        idx: 0,
        timers: [],
        observer: null,
        currentSvg: null
    };

    function startRotation() {
        var canvas = $("askf-canvas"); if (!canvas) return;
        var mount = canvas.querySelector(".askf-canvas-mount"); if (!mount) return;
        rotation.canvasPane = canvas;
        rotation.mount = mount;
        rotation.canceled = false;
        rotation.active = true;

        // Random start index so the same sample doesn't do all the work.
        rotation.idx = Math.floor((Date.now() >>> 0) % ROTATION_SAMPLES.length);

        // Caption element under the canvas, above the parts footer.
        rotation.caption = document.createElement("div");
        rotation.caption.className = "askf-rotation-caption";
        rotation.caption.setAttribute("aria-live", "polite");
        var status = $("askf-canvas-status");
        if (status && status.parentNode) status.parentNode.insertBefore(rotation.caption, status);
        else canvas.appendChild(rotation.caption);

        // Pause when the section leaves the viewport, resume when it returns.
        if (typeof IntersectionObserver === "function") {
            rotation.observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    if (e.isIntersecting) resumeRotation();
                    else pauseRotation();
                });
            }, { threshold: 0.15 });
            rotation.observer.observe(canvas);
        }
        document.addEventListener("visibilitychange", onVisibility);

        // Preload the SVGs in parallel, then start the cycle.
        var loads = ROTATION_SAMPLES.map(function (pair) {
            return fetch(pair[0], { cache: "force-cache" })
                .then(function (r) { return r.ok ? r.text() : null; })
                .then(function (text) { if (text) rotation.cache[pair[0]] = text; })
                .catch(function () { });
        });
        Promise.all(loads).then(function () {
            if (rotation.canceled) return;
            playNextSample();
        });
    }

    function onVisibility() {
        if (document.hidden) pauseRotation(); else resumeRotation();
    }
    function pauseRotation() { rotation.paused = true; }
    function resumeRotation() {
        if (rotation.canceled || rotation.paused === false) return;
        rotation.paused = false;
        // If no sample is currently on canvas (paused between beats), play
        // the current one now.
        if (!rotation.currentSvg) playNextSample();
    }

    function playNextSample() {
        if (rotation.canceled || !rotation.mount) return;
        if (rotation.paused) return;

        var pair = ROTATION_SAMPLES[rotation.idx];
        rotation.idx = (rotation.idx + 1) % ROTATION_SAMPLES.length;
        var text = rotation.cache[pair[0]];
        if (!text) { scheduleNext(500); return; }

        var parser = new DOMParser();
        var doc = parser.parseFromString(text, "image/svg+xml");
        var svg = doc.documentElement;
        if (!svg || svg.tagName.toLowerCase() !== "svg") { scheduleNext(500); return; }

        rotation.mount.innerHTML = "";
        rotation.mount.appendChild(svg);
        rotation.currentSvg = svg;
        primePenPaths(svg);

        // Caption naming the product this sample belongs to.
        if (rotation.caption) rotation.caption.textContent = pair[1];

        var reduced = prefersReduced();
        var drawMs = playBeatsAgainst(svg);

        if (reduced) {
            // Play one completed sample, hold it, do not cycle.
            rotation.active = false;
            return;
        }

        var t1 = setTimeout(function () {
            if (rotation.canceled) return;
            svg.style.transition = "opacity " + ROTATION_FADE_MS + "ms ease-in";
            svg.style.opacity = "0";
            var t2 = setTimeout(function () {
                if (rotation.canceled) return;
                if (svg.parentNode) svg.parentNode.removeChild(svg);
                rotation.currentSvg = null;
                if (rotation.caption) rotation.caption.textContent = "";
                // Canvas is genuinely empty for one frame before the next
                // sample begins, per the "nothing is ever pre placed" law.
                requestAnimationFrame(function () {
                    if (rotation.canceled || rotation.paused) return;
                    playNextSample();
                });
            }, ROTATION_FADE_MS + 20);
            rotation.timers.push(t2);
        }, drawMs + ROTATION_HOLD_MS);
        rotation.timers.push(t1);
    }

    function scheduleNext(ms) {
        var t = setTimeout(playNextSample, ms);
        rotation.timers.push(t);
    }

    function stopRotation(opts) {
        opts = opts || {};
        rotation.canceled = true;
        rotation.active = false;
        rotation.timers.forEach(function (t) { clearTimeout(t); });
        rotation.timers = [];
        if (rotation.observer) { rotation.observer.disconnect(); rotation.observer = null; }
        document.removeEventListener("visibilitychange", onVisibility);
        if (opts.clearCanvas && rotation.mount) rotation.mount.innerHTML = "";
        if (rotation.caption && rotation.caption.parentNode) {
            rotation.caption.parentNode.removeChild(rotation.caption);
        }
        rotation.caption = null;
        rotation.currentSvg = null;
    }

    /* -------------------- canvas diff engine --------------------
       Contract with flows: every <g> in returned SVG carries data-node-id
       stable across redraws for the same logical node, and data-role for
       parts-footer counting. If either is missing on a redraw, we fall
       back to full replace and log for diagnostics. */
    function drawCanvas(attempt) {
        if (!LIVE) return;
        attempt = attempt || 0;
        var canvas = $("askf-canvas"); if (!canvas) return;
        var mount = canvas.querySelector(".askf-canvas-mount");
        var status = $("askf-canvas-status");
        if (status) status.textContent = "";
        if (mount) startThinking(mount);

        fetch(DRAW, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: session.id })
        }).then(function (r) {
            if (!r.ok) throw new Error("draw " + r.status);
            return r.json();
        }).then(function (data) {
            if (mount) stopThinking(mount);
            if (!data) throw new Error("no payload");
            if (data.unchanged) { /* silent no-op; no change budget decrement */ return; }
            if (!data.sketch_svg) throw new Error("no svg");

            var visibleChanged = applyDiff(canvas, data.sketch_svg);
            // Allowance counts messages, not drawing edits. The message counter
            // decremented in sendMessage(). Draws only fire GTM here.
            if (visibleChanged && window.dataLayer) {
                window.dataLayer.push({ event: "fortebot_draw_updated" });
            }
            updatePartsFooter(canvas);
            updateProofStrip(data.proof);
            if (remainingChanges() <= KEEP_UNLOCK_AT && !session.keepUnlocked) openKeepMoment(false);
            if (session.changeCount >= ALLOWANCE_MESSAGES) closeSession();
        }).catch(function () {
            if (mount) stopThinking(mount);
            if (attempt < 1) {
                if (status) status.textContent = COPY.draw_stalled_status;
                setTimeout(function () { drawCanvas(attempt + 1); }, 800);
                return;
            }
            if (status) status.textContent = "";
            renderBotBubble(COPY.draw_stalled_final, { instant: true });
            openKeepMoment(false);
        });
    }

    /* Parse incoming SVG string, honor data-node-id keep-position semantics.
       Returns true if the canvas visibly changed. First-mount plays the full
       BEATS schedule against the incoming SVG (the wow beat). Subsequent
       redraws only touch changed nodes and never re-animate kept ones. */
    function applyDiff(canvas, svgString) {
        var mount = canvas.querySelector(".askf-canvas-mount");
        if (!mount) return false;

        var parser = new DOMParser();
        var doc = parser.parseFromString(svgString, "image/svg+xml");
        var newSvg = doc.documentElement;
        if (!newSvg || newSvg.tagName.toLowerCase() !== "svg") return false;

        // Check contract: every <g> in the incoming SVG should carry data-node-id.
        var incomingGroups = Array.prototype.slice.call(newSvg.querySelectorAll("g[data-node-id]"));
        var allGroups = newSvg.querySelectorAll("g");
        var contractHonored = incomingGroups.length > 0 && incomingGroups.length === allGroups.length;

        var existingSvg = mount.querySelector("svg");

        if (!contractHonored) {
            // Fallback path: page ships correct today; the pen effect still
            // plays via data-beat groups. Diff engine lights up when flows
            // patch lands and every <g> carries data-node-id.
            if (window.console) console.warn("[askf] SVG missing stable data-node-id on all <g>; using data-beat replay without diff");
            mount.innerHTML = "";
            mount.appendChild(newSvg);
            primePenPaths(newSvg);
            playBeatsAgainst(newSvg);
            canvasNodes = {};
            newSvg.querySelectorAll("g[data-node-id]").forEach(function (g) {
                canvasNodes[g.getAttribute("data-node-id")] = { role: g.getAttribute("data-role") || "" };
            });
            return true;
        }

        // FIRST MOUNT: paper is empty. Install the SVG, prime paths, play the
        // full BEATS schedule. This is the wow beat.
        if (!existingSvg) {
            mount.innerHTML = "";
            mount.appendChild(newSvg);
            primePenPaths(newSvg);
            playBeatsAgainst(newSvg);
            incomingGroups.forEach(function (g) {
                canvasNodes[g.getAttribute("data-node-id")] = { role: g.getAttribute("data-role") || "" };
            });
            return incomingGroups.length > 0;
        }

        // GROWTH: index existing groups by node id.
        var existingGroups = Array.prototype.slice.call(existingSvg.querySelectorAll("g[data-node-id]"));
        var existingById = {};
        existingGroups.forEach(function (g) { existingById[g.getAttribute("data-node-id")] = g; });

        var incomingIds = {};
        incomingGroups.forEach(function (g) { incomingIds[g.getAttribute("data-node-id")] = true; });

        var visiblyChanged = false;

        // 1. Remove groups that disappeared. Fade over REMOVE_FADE_MS then unmount.
        Object.keys(existingById).forEach(function (id) {
            if (!incomingIds[id]) {
                var g = existingById[id];
                g.style.transition = "opacity " + REMOVE_FADE_MS + "ms ease-out";
                g.style.opacity = "0";
                setTimeout(function () { if (g.parentNode) g.parentNode.removeChild(g); }, REMOVE_FADE_MS + 20);
                delete canvasNodes[id];
                visiblyChanged = true;
            }
        });

        // 2. Update / add. Refresh viewBox on the mounted SVG if it changed.
        var viewBox = newSvg.getAttribute("viewBox");
        if (viewBox && existingSvg.getAttribute("viewBox") !== viewBox) existingSvg.setAttribute("viewBox", viewBox);

        // Separate edges (data-role="edge" or elements ONLY referencing endpoints)
        // from nodes. Per spec: an edge animates only once BOTH its endpoints
        // exist and are drawn. We identify edges heuristically by data-role or
        // presence of data-from + data-to attributes.
        var newNodes = [];
        var newEdges = [];
        incomingGroups.forEach(function (g) {
            var id = g.getAttribute("data-node-id");
            if (existingById[id]) return;    // handled below in the update pass
            var role = g.getAttribute("data-role") || "";
            var from = g.getAttribute("data-from");
            var to = g.getAttribute("data-to");
            if (role === "edge" || (from && to)) newEdges.push(g);
            else newNodes.push(g);
        });

        // Update kept nodes: refresh contents in place, no re-animation.
        incomingGroups.forEach(function (g) {
            var id = g.getAttribute("data-node-id");
            var role = g.getAttribute("data-role") || "";
            var prev = existingById[id];
            if (!prev) return;
            var prevRole = prev.getAttribute("data-role") || "";
            if (prev.innerHTML !== g.innerHTML || prevRole !== role) {
                prev.innerHTML = g.innerHTML;
                prev.setAttribute("data-role", role);
                canvasNodes[id] = { role: role };
                visiblyChanged = true;
            }
        });

        // Add new nodes with GROWTH pen effect, staggered by GROWTH_STAGGER_MS.
        newNodes.forEach(function (g, i) {
            var clone = g.cloneNode(true);
            existingSvg.appendChild(clone);
            growNode(clone, i);
            canvasNodes[g.getAttribute("data-node-id")] = { role: g.getAttribute("data-role") || "" };
            visiblyChanged = true;
        });

        // Add new edges only when BOTH endpoints are on canvas (kept or freshly grown).
        // The node draw runs newNodes.length * GROWTH_STAGGER_MS + GROWTH_STROKE_MS,
        // so we delay edges until after the last node completes drawing.
        var edgeDelayBase = newNodes.length * GROWTH_STAGGER_MS + GROWTH_STROKE_MS;
        newEdges.forEach(function (g, i) {
            var from = g.getAttribute("data-from");
            var to = g.getAttribute("data-to");
            var endpointsExist = (!from || canvasNodes[from] || incomingIds[from]) &&
                                 (!to || canvasNodes[to] || incomingIds[to]);
            if (!endpointsExist) return;    // silently skip; server should not have emitted this
            var clone = g.cloneNode(true);
            existingSvg.appendChild(clone);
            setTimeout(function () { growNode(clone, i); }, edgeDelayBase);
            canvasNodes[g.getAttribute("data-node-id")] = { role: g.getAttribute("data-role") || "" };
            visiblyChanged = true;
        });

        return visiblyChanged;
    }

    function updatePartsFooter(canvas) {
        var footer = $("askf-parts"); if (!footer) return;
        var mount = canvas.querySelector(".askf-canvas-mount");
        var svg = mount ? mount.querySelector("svg") : null;
        var groups = svg ? svg.querySelectorAll("g[data-node-id]") : [];
        var n = groups.length;
        if (n === 0) { footer.textContent = ""; return; }

        var roleCounts = {};
        Array.prototype.forEach.call(groups, function (g) {
            var r = g.getAttribute("data-role");
            if (!r) return;
            roleCounts[r] = (roleCounts[r] || 0) + 1;
        });
        var pieces = [COPY.parts_intro(n)];
        Object.keys(roleCounts).forEach(function (role) {
            var word = COPY.role_words[role];
            if (!word) return;
            var count = roleCounts[role];
            var phrase = count > 1 ? count + " of " + word : word;
            // Sentence-case each fragment
            pieces.push(phrase.charAt(0).toUpperCase() + phrase.slice(1) + ".");
        });
        footer.textContent = pieces.join("  ");
    }

    function updateProofStrip(proof) {
        var strip = $("askf-proof"); if (!strip) return;
        if (!proof) { strip.innerHTML = ""; strip.classList.remove("has-proof"); return; }
        // Every field must be present and non-empty to render.
        if (!proof.label || !proof.line || !proof.image_url || !proof.href) {
            strip.innerHTML = ""; strip.classList.remove("has-proof");
            return;
        }
        var safe = {
            label: esc(proof.label),
            line: esc(proof.line),
            image_url: esc(proof.image_url),
            href: esc(proof.href),
            cta: esc(COPY.proof_cta)
        };
        strip.innerHTML =
            '<a class="askf-proof-inner" href="' + safe.href + '" data-gtm-event="fortebot_proof_shown">' +
              '<img class="askf-proof-img" src="' + safe.image_url + '" alt="" loading="lazy">' +
              '<div class="askf-proof-body">' +
                '<div class="askf-proof-label">' + safe.label + '</div>' +
                '<div class="askf-proof-line">' + safe.line + '</div>' +
                '<span class="askf-proof-cta">' + safe.cta + ' &rsaquo;</span>' +
              '</div>' +
            '</a>';
        strip.classList.add("has-proof");
        if (window.dataLayer) window.dataLayer.push({ event: "fortebot_proof_shown" });
    }

    /* -------------------- boot -------------------- */
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
})();
