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

    /* -------------------- COPY of record --------------------
       Every visitor-readable string in one block. Voice-scanned.
       Banned: em dashes, rule-of-three lists, contrast framing,
       Latin abbreviations, "napkin", "sketch", any dollar sign. */
    var COPY = {
        opener: "What is going on in your business right now. Explain it your way and I will draw how it would work.",
        placeholder_long: "Start anywhere. Rambling is fine.",
        placeholder_med: "Start anywhere.",
        placeholder_short: "Start anywhere.",
        capped_placeholder: "That is my free brain for today.",
        canvas_heading: "How it would work",
        canvas_footer_note: "This is me thinking out loud. The audit is me measuring.",
        allowance_label: function (n) { return n === 1 ? "1 change left" : n + " changes left"; },
        keep_prompt_default: "Want it as a packet with the drawing and the parts. Drop your email.",
        keep_prompt_close: "That is my free brain for today. The audit is the unlimited version, or drop your email and take the drawing with you.",
        gate_button: "Email me the packet",
        gate_email_placeholder: "you@company.com",
        gate_ok: "On its way. Check your inbox in a minute.",
        gate_err_email: "That does not look like an email address.",
        gate_err_send: "I cannot email it just yet, but the drawing is yours on screen.",
        gate_sending: "Sending.",
        ask_err: "Something on my side is off. Try again in a minute, or email seth@launchforte.com and I will answer it myself.",
        draw_stalled_status: "the pen slipped. one more try.",
        draw_stalled_final: "The drawing stalled on my end. Leave your email and I will send it once it is back.",
        cap_hit_bubble: "That is my free brain for today. The audit is the unlimited version, or drop your email and take the drawing with you.",
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
    var session = { id: null, changeCount: 0, closed: false, keepUnlocked: false, currentShape: null, currentTrade: null };
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

        // Homepage bar-only surface: if there is no canvas mount on this page,
        // the first keystroke routes to /ask?q= carrying the typed text.
        if (!$("askf-canvas")) {
            wireHomepageHandoff();
            return;
        }

        var pre = new URLSearchParams(location.search).get("q");
        if (pre) {
            sendMessage(pre.slice(0, CHAR_CAP), { prefill: true });
        } else {
            renderBotBubble(COPY.opener, { instant: true });
        }
        updateAllowance();
    }

    function prefill() {
        var q = new URLSearchParams(location.search).get("q");
        if (q && $("askf-input")) $("askf-input").value = q.slice(0, CHAR_CAP);
        updateCharCount();
    }

    /* Homepage keystroke handoff. Any keystroke inside the bar sends the visitor
       to /ask?q=<typed> so the full surface takes over. Empty typing does not
       redirect; the user has to type something first. */
    function wireHomepageHandoff() {
        var input = $("askf-input"); if (!input) return;
        applyPlaceholder();
        window.addEventListener("resize", applyPlaceholder, { passive: true });
        function go() {
            var v = input.value.trim();
            if (!v) return;
            var url = "/ask/?q=" + encodeURIComponent(v.slice(0, CHAR_CAP));
            location.href = url;
        }
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); go(); }
        });
        var send = $("askf-send");
        if (send) { send.disabled = false; send.addEventListener("click", go); }
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
        b.textContent = opts.instant ? text : "";
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
        renderBotBubble(COPY.cap_hit_bubble, { instant: true });
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
        busy = true;
        var send = $("askf-send"); if (send) send.disabled = true;
        renderUserBubble(text);

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
                    renderBotBubble(COPY.cap_hit_bubble, { instant: true });
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
                if (wantDraw) drawCanvas();
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

    /* -------------------- canvas diff engine --------------------
       Contract with flows: every <g> in returned SVG carries data-node-id
       stable across redraws for the same logical node, and data-role for
       parts-footer counting. If either is missing on a redraw, we fall
       back to full replace and log for diagnostics. */
    function drawCanvas(attempt) {
        if (!LIVE) return;
        attempt = attempt || 0;
        var canvas = $("askf-canvas"); if (!canvas) return;
        var status = $("askf-canvas-status");
        if (status) status.textContent = "";

        fetch(DRAW, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: session.id })
        }).then(function (r) {
            if (!r.ok) throw new Error("draw " + r.status);
            return r.json();
        }).then(function (data) {
            if (!data) throw new Error("no payload");
            if (data.unchanged) { /* silent no-op; no change budget decrement */ return; }
            if (!data.sketch_svg) throw new Error("no svg");

            var visibleChanged = applyDiff(canvas, data.sketch_svg);
            if (visibleChanged) {
                session.changeCount += 1;
                updateAllowance();
                if (window.dataLayer) window.dataLayer.push({ event: "fortebot_draw_updated" });
            }
            updatePartsFooter(canvas);
            updateProofStrip(data.proof);
            if (remainingChanges() <= KEEP_UNLOCK_AT && !session.keepUnlocked) openKeepMoment(false);
            if (session.changeCount >= ALLOWANCE_MESSAGES) closeSession();
        }).catch(function () {
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
       Returns true if the canvas visibly changed. */
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

        if (!contractHonored) {
            if (window.console) console.warn("[askf] SVG missing stable data-node-id on all <g>; falling back to full replace");
            mount.innerHTML = "";
            mount.appendChild(newSvg);
            canvasNodes = {};
            incomingGroups.forEach(function (g) {
                var id = g.getAttribute("data-node-id");
                canvasNodes[id] = { role: g.getAttribute("data-role") || "" };
            });
            return true;
        }

        // Diff path: preserve existing <g data-node-id> positions, fade in new,
        // fade out gone. Edges are children of an outer <g> or top-level — we
        // treat any element with data-node-id as a node candidate.
        var existingSvg = mount.querySelector("svg");
        var visiblyChanged = false;

        if (!existingSvg) {
            mount.innerHTML = "";
            mount.appendChild(newSvg);
            var installed = Array.prototype.slice.call(newSvg.querySelectorAll("g[data-node-id]"));
            installed.forEach(function (g) {
                g.style.opacity = "0";
                requestAnimationFrame(function () {
                    g.style.transition = "opacity 500ms ease-out";
                    g.style.opacity = "1";
                });
                canvasNodes[g.getAttribute("data-node-id")] = { role: g.getAttribute("data-role") || "" };
            });
            return installed.length > 0;
        }

        // Diff: index existing groups by node id
        var existingGroups = Array.prototype.slice.call(existingSvg.querySelectorAll("g[data-node-id]"));
        var existingById = {};
        existingGroups.forEach(function (g) { existingById[g.getAttribute("data-node-id")] = g; });

        var incomingIds = {};
        incomingGroups.forEach(function (g) { incomingIds[g.getAttribute("data-node-id")] = true; });

        // 1. Remove groups that disappeared
        Object.keys(existingById).forEach(function (id) {
            if (!incomingIds[id]) {
                var g = existingById[id];
                g.style.transition = "opacity 300ms ease-out";
                g.style.opacity = "0";
                setTimeout(function () { if (g.parentNode) g.parentNode.removeChild(g); }, 320);
                delete canvasNodes[id];
                visiblyChanged = true;
            }
        });

        // 2. Update / add. Replace SVG root attributes (viewBox etc) to match new.
        var viewBox = newSvg.getAttribute("viewBox");
        if (viewBox && existingSvg.getAttribute("viewBox") !== viewBox) existingSvg.setAttribute("viewBox", viewBox);

        incomingGroups.forEach(function (g) {
            var id = g.getAttribute("data-node-id");
            var role = g.getAttribute("data-role") || "";
            if (existingById[id]) {
                // Keep position: only refresh label content, do not re-animate.
                // If content diff is non-trivial (role changed or child count differs),
                // we still keep its position but swap its inner markup.
                var prev = existingById[id];
                var prevRole = prev.getAttribute("data-role") || "";
                if (prev.innerHTML !== g.innerHTML || prevRole !== role) {
                    prev.innerHTML = g.innerHTML;
                    prev.setAttribute("data-role", role);
                    canvasNodes[id] = { role: role };
                    visiblyChanged = true;
                }
            } else {
                // New node: append with a fade-in beat.
                var clone = g.cloneNode(true);
                clone.style.opacity = "0";
                existingSvg.appendChild(clone);
                requestAnimationFrame(function () {
                    clone.style.transition = "opacity 500ms ease-out";
                    clone.style.opacity = "1";
                });
                canvasNodes[id] = { role: role };
                visiblyChanged = true;
            }
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
