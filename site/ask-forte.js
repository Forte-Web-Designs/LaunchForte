/* ============================================================
   Ask Forte — shared component. One mount, two pages.
   Runbook: forte_bot_runbook.md § "ASK FORTE, OPEN"
   Section 16 (page runbook): one component, two mounts — the DOM
   is the partial. This script is a no-op on pages without #askf-chat.
   ============================================================
   Contract v2 (per flows-session handoff): n8n streams newline-delimited
   JSON envelopes; the model splits content anywhere. The adapter unwraps
   {"type":"item","content":"..."} lines, concatenates content, then scans
   for [[SENTINELS]]. See processLine + parseSentinels below.

   Endpoints:
     POST /forte-ask    - streaming; body: {session_id?, message, meta}
     POST /forte-shape  - shape lookup; body: {session_id, shape}
     POST /forte-draw   - napkin (SVG); body: {session_id}
     POST /gate-request - email close; body: {tool_key:"bot", email, session_id}
*/
(function(){
    /* -------------------- config -------------------- */
    var LIVE = true;                                // LIVE 2026-07-29: n8n verified end-to-end. /forte-ask streams first token at 1,753ms, emits [[SHAPE|slug]] and [[NAPKIN]] correctly. /forte-shape + /forte-draw up. Caps at prod values. /gate-request has no Capture workflow yet — errors handled honestly below.
    var API_BASE  = "https://launchforte.app.n8n.cloud/webhook";
    var ASK       = API_BASE + "/forte-ask";
    var SHAPE     = API_BASE + "/forte-shape";
    var DRAW      = API_BASE + "/forte-draw";
    var GATE      = API_BASE + "/gate-request";

    var ALLOWANCE_MESSAGES = 10;
    var DOOR_HINT_AT       = 7;
    var CHAR_CAP           = 1000;
    var DEFLECT            = "I only sketch business systems... describe yours and I'll draw it.";

    var BEATS = [[0,400],[1,900],[2,500],[3,700],[4,500],[5,600],[6,900]];
    var PAUSE_BEFORE_SCAR = 400;

    /* -------------------- helpers -------------------- */
    var $ = function(id){ return document.getElementById(id); };
    function el(tag, cls){ var n = document.createElement(tag); if (cls) n.className = cls; return n; }
    function scrollLog(){ var log = $("askf-log"); if (log) log.scrollTop = log.scrollHeight; }
    function esc(s){ return String(s).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }

    /* -------------------- state --------------------
       session.id is minted CLIENT-SIDE on the first message (streaming mode
       returns no session id, so we can't rely on the server for continuity).
       The flows validator accepts bot-<random>. Once minted, we send it on
       every subsequent turn so the model remembers the conversation. */
    function mintSessionId(){
        var rand = Math.floor(Math.random() * 1e12).toString(36);
        return 'bot-' + rand + '-' + Date.now().toString(36).slice(-4);
    }
    var session = { id: null, messageCount: 0, closed: false };
    var busy = false;
    var cardsSeen = { SHAPE: false, SEEN: false, GOTCHA: false, NEXT: false };

    /* -------------------- init -------------------- */
    function init(){
        // No-op on pages without the partial DOM
        if (!$("askf-chat")) return;
        if (!LIVE){
            var holding = $("askf-holding");
            if (holding) holding.classList.remove("askf-hide");
            var log = $("askf-log"); if (log) log.classList.add("askf-hide");
            var composer = $("askf-composer"); if (composer) composer.classList.add("askf-hide");
            var cards = $("askf-cards"); if (cards) cards.classList.add("askf-hide");
            return;
        }
        prefill();
        wireInput();
        wireMic();
        wireGate();
        // Opener bubble per Seth: exactly this and nothing more.
        // No introduction, no name, no capabilities list — just the question.
        var pre = new URLSearchParams(location.search).get("q");
        if (pre) {
            sendMessage(pre.slice(0, CHAR_CAP), { prefill: true });
        } else {
            renderBotBubble("What's eating your week? Explain what's going on and I'll draw it.", { instant: true });
        }
        updateAllowance();
    }

    function prefill(){
        var q = new URLSearchParams(location.search).get("q");
        if (q) $("askf-input").value = q.slice(0, CHAR_CAP);
        updateCharCount();
    }

    /* -------------------- input UX -------------------- */
    /* Responsive placeholder: the long form is fine on desktop but gets
       clipped on phones. Three tiers so it never truncates:
         >= 640px : full "Got an automation idea or a pain point? Ask Forte."
         480–639  : "What's broken? Ask Forte."
         < 480    : "Ask Forte." */
    var PH_LONG = "Got an automation idea or a pain point? Ask Forte.";
    var PH_MED  = "What's broken? Ask Forte.";
    var PH_SHORT = "Ask Forte.";
    function applyPlaceholder(){
        var input = $("askf-input"); if (!input) return;
        var w = window.innerWidth;
        input.setAttribute("placeholder", w < 480 ? PH_SHORT : w < 640 ? PH_MED : PH_LONG);
    }
    function wireInput(){
        var input = $("askf-input");
        var send = $("askf-send");
        applyPlaceholder();
        var ph_t;
        window.addEventListener("resize", function(){
            clearTimeout(ph_t);
            ph_t = setTimeout(applyPlaceholder, 100);
        }, { passive: true });
        input.addEventListener("input", function(){
            autoGrow(input);
            updateCharCount();
        });
        input.addEventListener("keydown", function(e){
            if (e.key === "Enter" && !e.shiftKey && !send.disabled){ e.preventDefault(); trySend(); }
        });
        send.addEventListener("click", trySend);
    }
    /* Single-line by default. Only grow past 44px when text actually wraps
       so the composer never shows a scrollbar for a one-line message. */
    function autoGrow(t){
        t.style.height = 'auto';
        var natural = t.scrollHeight;
        // 44px is the single-line height; if content fits, stay there.
        var target = natural <= 48 ? 44 : Math.min(140, natural);
        t.style.height = target + 'px';
    }
    function updateCharCount(){
        var v = $("askf-input").value;
        var el = $("askf-charcount");
        el.textContent = v.length + " / " + CHAR_CAP;
        el.classList.toggle("warn", v.length >= CHAR_CAP);
        $("askf-send").disabled = v.trim().length < 3 || busy || session.closed;
    }
    function trySend(){
        var v = $("askf-input").value.trim();
        if (v.length < 3 || busy || session.closed) return;
        $("askf-input").value = "";
        autoGrow($("askf-input"));
        updateCharCount();
        sendMessage(v);
    }

    /* -------------------- voice input (Web Speech API) -------------------- */
    function wireMic(){
        var Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!Rec) return;
        var mic = $("askf-mic");
        mic.classList.add("available");
        var recognizer = new Rec();
        recognizer.continuous = true;
        recognizer.interimResults = true;
        recognizer.lang = "en-US";
        var recording = false;
        var baseText = "";
        mic.addEventListener("click", function(){
            if (recording) { recognizer.stop(); return; }
            baseText = $("askf-input").value;
            try { recognizer.start(); } catch(_){ return; }
        });
        recognizer.onstart = function(){ recording = true; mic.classList.add("recording"); mic.setAttribute("aria-label","Stop recording"); };
        recognizer.onend   = function(){ recording = false; mic.classList.remove("recording"); mic.setAttribute("aria-label","Speak your message"); };
        recognizer.onerror = function(){ recording = false; mic.classList.remove("recording"); };
        recognizer.onresult = function(e){
            var chunk = "";
            for (var i = e.resultIndex; i < e.results.length; i++) chunk += e.results[i][0].transcript;
            var input = $("askf-input");
            input.value = (baseText ? baseText + " " : "") + chunk;
            input.value = input.value.slice(0, CHAR_CAP);
            autoGrow(input);
            updateCharCount();
        };
    }

    /* -------------------- render bubbles / cards / napkin -------------------- */
    function renderUserBubble(text){
        var t = el("div","askf-turn user");
        var b = el("div","askf-bubble");
        b.textContent = text;
        t.appendChild(b);
        $("askf-log").appendChild(t);
        scrollLog();
    }
    function renderBotBubble(text, opts){
        opts = opts || {};
        var t = el("div","askf-turn bot");
        var b = el("div","askf-bubble");
        b.textContent = opts.instant ? text : "";
        t.appendChild(b);
        $("askf-log").appendChild(t);
        scrollLog();
        return { turn: t, bubble: b };
    }
    function renderTypingIndicator(){
        var t = el("div","askf-turn bot");
        var b = el("div","askf-typing");
        b.appendChild(el("span"));
        b.appendChild(el("span"));
        b.appendChild(el("span"));
        t.appendChild(b);
        $("askf-log").appendChild(t);
        scrollLog();
        return t;
    }
    /* Runbook: when [[NAPKIN]] arrives, render the napkin container. The
       blur-ghost placeholder fades IN at draw start — not sitting there
       before. Real strokes draw over it in strict order as they land, blur
       lifts as strokes complete. Draw is fired automatically — no button.

       Every ghost edge terminates in a drawn node at BOTH ends (renderer
       rule from Seth's ruling). Shape below: three-node pipeline in a row,
       one decision circle below the middle, book-out box under it. No
       dangling connectors. */
    function renderNapkinGhost(){
        var t = el("div","askf-turn bot");
        var b = el("div","askf-bubble napkin askf-napkin-loading");
        var frame = el("div","askf-napkin-frame askf-napkin-frame-ghost");
        // The ghost SVG is inserted with opacity:0; JS fades it in on next
        // frame so the container appears BEFORE the ghost blooms into it.
        frame.innerHTML =
            '<svg viewBox="0 0 340 240" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
              '<g stroke="#4A4A4F" stroke-width="1.6" fill="none" stroke-linecap="round">' +
                // Three nodes across the top
                '<rect x="18"  y="30" width="80" height="46" rx="8"/>' +
                '<rect x="130" y="30" width="80" height="46" rx="8"/>' +
                '<rect x="242" y="30" width="80" height="46" rx="8"/>' +
                // Book-out node, centered below the middle
                '<rect x="130" y="150" width="80" height="46" rx="8"/>' +
                // Edges — every endpoint touches a node bound
                '<path d="M98 53 L130 53"/>' +      // top-left -> middle
                '<path d="M210 53 L242 53"/>' +     // middle -> top-right
                '<path d="M170 76 L170 150"/>' +    // middle down to book-out
                // Blue decision ring around the middle node
                '<rect x="130" y="30" width="80" height="46" rx="8" stroke="#0088DB" stroke-width="2"/>' +
              '</g>' +
            '</svg>';
        b.appendChild(frame);
        var status = el("div","askf-napkin-caption askf-napkin-status");
        status.textContent = "sketching your napkin…";
        b.appendChild(status);
        t.appendChild(b);
        $("askf-log").appendChild(t);
        scrollLog();
        // Fade the ghost in AT draw start rather than having it visible
        // the instant the container mounts. Container appears first (paper
        // only), then blur-ghost blooms.
        frame.style.opacity = '0';
        requestAnimationFrame(function(){
            frame.style.transition = 'opacity 400ms ease-out';
            frame.style.opacity = '1';
        });
        return { turn: t, bubble: b, frame: frame, status: status };
    }
    function renderCard(kind, body){
        if (cardsSeen[kind]) return;
        cardsSeen[kind] = true;
        var empty = $("askf-cards-empty"); if (empty) empty.remove();
        var cards = $("askf-cards"); if (!cards) return;
        var card = el("div","askf-card");
        var label = el("div","askf-card-label");
        label.textContent = kind;
        var b = el("div","askf-card-body");
        b.textContent = body;
        card.appendChild(label);
        card.appendChild(b);
        cards.appendChild(card);
        requestAnimationFrame(function(){ card.classList.add("appear"); });
    }
    /* Take an existing ghost bubble (if present) and REPLACE its ghost SVG
       with the real one, so the strokes appear to draw over the ghost. The
       ghost fades as the real strokes land. If no ghost exists (shouldn't
       happen post-runbook), create a fresh bubble. */
    /* Renders the real napkin over the ghost. Per runbook "see free, keep
       by email": napkin draws inline FREE end-to-end (all 7 beats including
       scar). AFTER scar lands + one beat of stillness, the keep-moment
       gate opens with the locked copy asking for email. */
    function renderNapkin(svg, scar, mappedDemo, mappedLabel, ghost){
        var bubble, frame;
        if (ghost && ghost.bubble && ghost.frame){
            bubble = ghost.bubble;
            frame = ghost.frame;
            bubble.classList.remove("askf-napkin-loading");
            frame.classList.remove("askf-napkin-frame-ghost");
            frame.innerHTML = svg;
            if (ghost.status && ghost.status.parentNode) ghost.status.parentNode.removeChild(ghost.status);
        } else {
            var t = el("div","askf-turn bot");
            bubble = el("div","askf-bubble napkin");
            frame = el("div","askf-napkin-frame");
            frame.innerHTML = svg;
            bubble.appendChild(frame);
            t.appendChild(bubble);
            $("askf-log").appendChild(t);
        }
        if (scar){
            var cap = el("div","askf-napkin-caption");
            cap.textContent = scar;
            bubble.appendChild(cap);
        }
        if (mappedDemo){
            var link = el("div","askf-napkin-caption");
            link.innerHTML = 'Live demo of this shape: <a href="' + esc(mappedDemo) + '">' + esc(mappedLabel || "See it running") + '</a>';
            bubble.appendChild(link);
        }
        scrollLog();
        // Play ALL beats including scar. Gate opens after scar + stillness.
        playNapkinChoreography(frame.querySelector("svg"), /* stopBeforeScar */ false, function onScarLanded(){
            setTimeout(openKeepMoment, 500);
        });
    }

    /* Keep-moment prompt: opens AFTER the whole napkin has drawn (per
       runbook "see free, keep by email"). Locked copy from the runbook.
       On capture: /gate-request fires (which triggers Capture server-side:
       PDF send + Twenty write + [ASK FORTE] notify). */
    function openKeepMoment(){
        var gate = $("askf-gate");
        var msg = $("askf-gate-msg");
        if (!gate || gate.classList.contains("open")) return;
        gate.classList.add("open");
        if (msg){
            msg.textContent = "Want it as a PDF, plus which live demo matches your build? Drop your email.";
            msg.classList.add("askf-gate-prompt");
        }
        var email = $("askf-gate-email");
        if (email) { try { email.focus({ preventScroll: false }); } catch(_){} }
    }

    /* Draw the napkin one beat at a time. If stopBeforeScar=true, we play
       beats 0..5 only and fire the callback when beat 5 lands (gate opens).
       Beat 6 (scar) is revealed later via revealBeatSix() after email capture. */
    function playNapkinChoreography(svg, stopBeforeScar, onLastBeat){
        if (!svg) return;
        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        var groups = {};
        svg.querySelectorAll('g[data-beat]').forEach(function(g){
            var idx = parseInt(g.getAttribute('data-beat'), 10);
            if (isNaN(idx)) return;
            (groups[idx] = groups[idx] || []).push(g);
        });
        // Prime every group hidden
        Object.keys(groups).forEach(function(k){
            groups[k].forEach(function(g){
                g.style.opacity = '0';
                g.querySelectorAll('path').forEach(function(p){
                    p.style.strokeDasharray = '1';
                    p.style.strokeDashoffset = '1';
                });
            });
        });
        if (reduce){
            // Show all beats immediately EXCEPT scar if withheld
            Object.keys(groups).forEach(function(k){
                var beatIdx = parseInt(k, 10);
                if (stopBeforeScar && beatIdx === 6) return;
                groups[k].forEach(function(g){
                    g.style.opacity = '1';
                    g.querySelectorAll('path').forEach(function(p){ p.style.strokeDashoffset = '0'; });
                });
            });
            if (typeof onLastBeat === "function") onLastBeat();
            return;
        }
        var elapsed = 0;
        BEATS.forEach(function(pair){
            var beatIdx = pair[0], durMs = pair[1];
            if (stopBeforeScar && beatIdx === 6) return;   // withhold scar
            setTimeout(function(){
                var gs = groups[beatIdx] || [];
                gs.forEach(function(g){
                    g.style.transition = 'opacity ' + Math.min(durMs, 500) + 'ms ease-out';
                    g.style.opacity = '1';
                    g.querySelectorAll('path').forEach(function(p){
                        p.style.transition = 'stroke-dashoffset ' + durMs + 'ms ease-out';
                        p.style.strokeDashoffset = '0';
                    });
                });
                // Fire callback when the LAST played beat lands
                var isLast = stopBeforeScar ? (beatIdx === 5) : (beatIdx === 6);
                if (isLast && typeof onLastBeat === "function"){
                    setTimeout(onLastBeat, durMs);
                }
            }, elapsed);
            elapsed += durMs;
        });
    }

    /* -------------------- allowance / close -------------------- */
    function updateAllowance(){
        var remaining = Math.max(0, ALLOWANCE_MESSAGES - session.messageCount);
        var el = $("askf-allowance"); if (!el) return;
        el.textContent = (remaining <= 3) ? (remaining + " left in this session") : "";
    }
    function closeSession(){
        session.closed = true;
        $("askf-send").disabled = true;
        $("askf-input").disabled = true;
        // Locked runbook copy for the allowance cap
        $("askf-input").placeholder = "That's my free brain for today.";
        // Warm cap message shown in the log as one last bot bubble
        var capMsg = "That's my free brain for today. The audit is the unlimited version. Or drop your email and take the napkin with you.";
        var b = renderBotBubble(capMsg, { instant: true });
        // Open the gate with the same locked copy the keep-moment uses
        var gate = $("askf-gate");
        var msg = $("askf-gate-msg");
        if (gate && !gate.classList.contains("open")){
            gate.classList.add("open");
            if (msg){
                msg.textContent = "Want it as a PDF, plus which live demo matches your build? Drop your email.";
                msg.classList.add("askf-gate-prompt");
            }
        }
        updateAllowance();
    }

    /* -------------------- gate -------------------- */
    function wireGate(){
        var btn = $("askf-gate-send"); if (!btn) return;
        btn.addEventListener("click", function(){
            var email = $("askf-gate-email").value.trim();
            var msg = $("askf-gate-msg");
            msg.classList.remove("ok","err");
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)){
                msg.classList.add("err");
                msg.textContent = "That doesn't look like an email address.";
                return;
            }
            btn.disabled = true;
            msg.textContent = "Sending...";
            fetch(GATE, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tool_key: "bot", email: email, session_id: session.id })
            }).then(function(r){
                if (!r.ok) throw new Error("gate " + r.status);
                msg.classList.add("ok");
                msg.textContent = "On its way. Check your inbox in a minute.";
                if (window.dataLayer) window.dataLayer.push({ event: "fortebot_email_sent" });
            }).catch(function(){
                msg.classList.add("err");
                // Capture workflow isn't built yet — honest fallback, no false promise of email.
                msg.textContent = "I can't email it just yet, but the napkin is yours on screen.";
                btn.disabled = false;
            });
        });
    }

    /* -------------------- sentinel adapter --------------------
       Sentinels ride inside the token stream as bracketed markers.
       Since the model splits text anywhere, sentinels can arrive across
       chunks. We buffer partial tails so [[NAP ... KIN]] never flashes. */
    function parseSentinels(chunkText, carry){
        var buf = (carry || "") + chunkText;
        var frames = [];
        var re = /\[\[([^\[\]]+)\]\]/g;
        var lastIndex = 0;
        var m;
        while ((m = re.exec(buf)) !== null){
            var pre = buf.slice(lastIndex, m.index);
            if (pre) frames.push({ type: "token", text: pre });
            var body = m[1].trim();
            if (body.indexOf("SHAPE|") === 0){
                var slug = body.slice(6).trim();
                if (slug) frames.push({ type: "shape", name: slug });
            } else if (body === "NAPKIN"){
                frames.push({ type: "offer_napkin" });
            } else if (body === "CLOSE"){
                frames.push({ type: "suggest_close" });
            } else if (body === "DEFLECT"){
                frames.push({ type: "deflect" });
            }
            lastIndex = re.lastIndex;
        }
        var tail = buf.slice(lastIndex);
        var openIdx = tail.lastIndexOf("[[");
        var carryOut = "";
        var emitTail = tail;
        if (openIdx !== -1 && tail.indexOf("]]", openIdx) === -1){
            emitTail = tail.slice(0, openIdx);
            carryOut = tail.slice(openIdx);
        }
        if (!carryOut && emitTail.charAt(emitTail.length - 1) === "["){
            carryOut = "[";
            emitTail = emitTail.slice(0, -1);
        }
        if (emitTail) frames.push({ type: "token", text: emitTail });
        return { frames: frames, carry: carryOut };
    }

    /* -------------------- streaming send -------------------- */
    function sendMessage(text, opts){
        opts = opts || {};
        if (session.closed || busy) return;
        busy = true; $("askf-send").disabled = true;
        renderUserBubble(text);
        session.messageCount += 1;
        updateAllowance();

        var typing = renderTypingIndicator();
        var botHolder = null;
        var accumulated = "";
        var wasDeflected = false;

        // Mint the session id on the first message. Every subsequent turn
        // carries it so the model remembers turn 1 by turn 3.
        if (!session.id) session.id = mintSessionId();
        var payload = { session_id: session.id, message: text, meta: { referrer: document.referrer, prefill: !!opts.prefill } };

        fetch(ASK, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        }).then(function(resp){
            if (!resp.ok) throw new Error("ask " + resp.status);
            var newId = resp.headers.get("X-Forte-Session") || resp.headers.get("x-forte-session");
            if (newId && !session.id) session.id = newId;

            var reader = resp.body.getReader();
            var decoder = new TextDecoder();
            // TWO BUFFERS per flows-session PAGE-HANDOFF.md §0:
            //   lineBuf: bytes-side, partial JSON line across chunk boundaries
            //   carry:   text-side, partial sentinel across concatenated content
            // Envelope grammar from n8n:
            //   {"type":"begin",...}                 -> ignore
            //   {"type":"item","content":"..."}      -> concatenate content
            //   {"type":"end",...}                   -> stream complete
            var lineBuf = "";
            var carry = "";
            var streamEnded = false;

            function pump(){
                return reader.read().then(function(res){
                    if (res.done){
                        if (lineBuf){ processLine(lineBuf); lineBuf = ""; }
                        if (carry){ handleFrame({ type: "token", text: carry }); carry = ""; }
                        finish();
                        return;
                    }
                    if (streamEnded){ finish(); return; }
                    lineBuf += decoder.decode(res.value, { stream: true });
                    var lines = lineBuf.split("\n");
                    lineBuf = lines.pop();
                    var textOut = "";
                    for (var i = 0; i < lines.length; i++){
                        var contentPart = processLine(lines[i]);
                        if (contentPart) textOut += contentPart;
                    }
                    if (textOut){
                        var out = parseSentinels(textOut, carry);
                        carry = out.carry;
                        for (var j = 0; j < out.frames.length; j++) handleFrame(out.frames[j]);
                    }
                    return pump();
                });
            }

            function processLine(line){
                var trimmed = line.replace(/^data:\s*/, "").trim();
                if (!trimmed) return "";
                if (trimmed.charAt(0) === "{"){
                    try {
                        var obj = JSON.parse(trimmed);
                        if (obj.type === "begin") return "";
                        if (obj.type === "end"){ streamEnded = true; return ""; }
                        if (obj.type === "item") return typeof obj.content === "string" ? obj.content : "";
                        if (typeof obj.content === "string") return obj.content;
                        if (typeof obj.text === "string") return obj.text;
                        if (typeof obj.token === "string") return obj.token;
                        if (typeof obj.delta === "string") return obj.delta;
                        return "";
                    } catch(_){ return trimmed; }
                }
                return trimmed;
            }

            /* ---- Token pacer ----
               n8n streams tokens in bursts (sometimes many words in a single
               chunk). Appending each burst instantly reads as jerky. Instead,
               push incoming characters into a queue and let a rAF-driven pump
               reveal them at a smooth cadence. When the stream ends, the pump
               keeps draining until the queue is empty. */
            var pendingChars = [];   // characters waiting to render
            var streamDone = false;  // set true when server closes
            var pacing = false;      // rAF loop running?
            var lastTick = 0;
            // Characters per second — tune for readable pace. n8n often emits
            // tokens at ~40-80 char/s; we render at ~90 so we drain the queue
            // without stalling, but each char has a visible per-frame beat.
            var CHARS_PER_SEC = 90;

            function ensureBotBubble(){
                if (!botHolder){
                    if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
                    typing = null;
                    botHolder = renderBotBubble("", {});
                }
            }
            function startPacer(){
                if (pacing) return;
                pacing = true;
                lastTick = performance.now();
                requestAnimationFrame(pace);
            }
            function pace(now){
                if (!botHolder){ pacing = false; return; }
                var dt = Math.min(now - lastTick, 100);  // clamp to avoid huge dumps on tab-switch
                lastTick = now;
                var target = Math.max(1, Math.round((dt / 1000) * CHARS_PER_SEC));
                if (pendingChars.length){
                    var take = Math.min(target, pendingChars.length);
                    accumulated += pendingChars.splice(0, take).join('');
                    botHolder.bubble.textContent = accumulated;
                    scrollLog();
                }
                if (pendingChars.length > 0){
                    requestAnimationFrame(pace);
                } else if (streamDone){
                    pacing = false;
                    finalizeReply();
                } else {
                    // Empty queue but stream still open — wait for more bytes
                    pacing = false;
                }
            }
            function pushToken(text){
                for (var i = 0; i < text.length; i++) pendingChars.push(text.charAt(i));
                startPacer();
            }

            function handleFrame(f){
                if (f.type === "token"){
                    if (wasDeflected) return;
                    ensureBotBubble();
                    pushToken(f.text);
                }
                else if (f.type === "shape"){
                    if (f.name){ renderCard("SHAPE", f.name); lookupShape(f.name); }
                }
                else if (f.type === "offer_napkin"){
                    if (!$("askf-napkin-mount")){
                        var ghost = renderNapkinGhost();
                        ghost.turn.id = "askf-napkin-mount";
                        drawNapkin(ghost);
                    }
                }
                else if (f.type === "suggest_close"){
                    renderCard("NEXT", "The audit is how a real one gets scoped.");
                }
                else if (f.type === "deflect"){
                    ensureBotBubble();
                    // Deflection replaces whatever bubble content is queuing/rendered
                    pendingChars.length = 0;
                    accumulated = DEFLECT;
                    botHolder.bubble.textContent = accumulated;
                    wasDeflected = true;
                    scrollLog();
                }
            }
            function finish(){
                if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
                // Signal the pacer that no more bytes will arrive. If it's still
                // draining, finalizeReply() runs when it hits an empty queue.
                streamDone = true;
                if (pendingChars.length > 0){
                    startPacer();
                } else {
                    finalizeReply();
                }
            }
            function finalizeReply(){
                busy = false;
                updateCharCount();
                if (session.messageCount >= DOOR_HINT_AT) renderCard("NEXT", "The audit is how a real one gets scoped.");
                if (session.messageCount >= ALLOWANCE_MESSAGES) closeSession();
            }
            return pump();
        }).catch(function(){
            if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
            renderBotBubble("Something on my side is off. Try again in a moment, or email seth@launchforte.com.", { instant: true });
            busy = false;
            updateCharCount();
        });
    }

    function lookupShape(slug){
        if (!LIVE || !session.id) return;
        fetch(SHAPE, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: session.id, shape: slug })
        }).then(function(r){ return r.json(); })
          .then(function(data){
              if (!data) return;
              if (data.plain) renderCard("SHAPE", data.plain);
              if (data.seen) renderCard("SEEN", data.seen);
          })
          .catch(function(){});
    }

    /* Runbook: on a failed draw after retry, show Forte's honest line plus
       the email offer. So we retry once, then fall through to the honest failure. */
    function drawNapkin(ghost, attempt){
        if (!LIVE) return;
        attempt = attempt || 0;
        fetch(DRAW, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: session.id })
        }).then(function(r){
            if (!r.ok) throw new Error("draw " + r.status);
            return r.json();
        })
          .then(function(data){
              if (!data || !data.sketch_svg) throw new Error("no svg");
              renderNapkin(data.sketch_svg, data.scar, data.mapped_demo, data.mapped_demo_label, ghost);
              if (data.scar) renderCard("GOTCHA", data.scar);
              if (window.dataLayer) window.dataLayer.push({ event: "fortebot_napkin_drawn" });
          })
          .catch(function(){
              if (attempt < 1){
                  // Per flows-session #3: on a failed draw, show the in-voice
                  // line and retry once. Keep the ghost visible so the visitor
                  // sees the sketch is still coming.
                  if (ghost && ghost.status){
                      ghost.status.textContent = "my pen slipped... one more shot.";
                  } else {
                      renderBotBubble("My pen slipped. One more shot.", { instant: true });
                  }
                  setTimeout(function(){ drawNapkin(ghost, attempt + 1); }, 800);
                  return;
              }
              // Failed even after retry — remove the ghost, honest line + keep-moment
              if (ghost && ghost.turn && ghost.turn.parentNode) ghost.turn.parentNode.removeChild(ghost.turn);
              renderBotBubble("The sketch isn't coming through on my side. Drop your email and I'll send the napkin once it's back, plus the demo that matches your build.", { instant: true });
              openKeepMoment();
          });
    }

    /* -------------------- boot -------------------- */
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
})();
