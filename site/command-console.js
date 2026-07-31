/* ============================================================
   /command/ console (job 4 of 4) -- the private Forte.
   Same visual chrome as the public Ask Forte partial (.askf-* rules from
   ask-forte.css: log, turn bubbles, composer), but this is a FULLY SEPARATE
   containment context:
     - its own script, own session id, own in-memory state
     - never touches ask-forte.js's session, and is never touched by it
     - points at POST /webhook/console-turn (private slice: client packs,
       tasks, work orders, latest reports), not /forte-ask (public slice)
   Auth: sends the dashboard's X-Dashboard-Token header, reading the token
   and API base from window.CMD_CONFIG / window.CMD_TOKEN -- the single
   constants location set up in job 1's script, not a second copy.

   Streaming contract (locked, same shape as Ask Forte's /forte-ask):
   NDJSON envelopes -- {"type":"begin"} / {"type":"item","content":"..."} /
   {"type":"end"} -- content concatenated across lines/chunks.

   ASSUMPTION (open question, see final message): the exact in-band marker
   the model uses for "READ" / "DO" / done-checkmark / red-confirm lines
   isn't given verbatim in prose, only the rendered result ("READ/DO/
   checkmark turns... compact lines"). This renderer recognizes a plain
   line-prefix convention (READ:, DO:, a leading checkmark, CONFIRM:) and
   the house bracket convention for an unset price ([BAND] etc., already
   used elsewhere on this page for price placeholders). Any line that
   doesn't match one of those still renders as normal paragraph text, so a
   plain-prose reply is never dropped or garbled while that convention is
   confirmed against the live endpoint.
   ============================================================ */
(function () {
    if (!document.getElementById('cc-chat')) return; // no-op off /command/

    var CONFIG = window.CMD_CONFIG || {
        API_BASE: 'https://launchforte.app.n8n.cloud',
        CONSOLE_TURN_PATH: '/webhook/console-turn'
    };
    var TOKEN = window.CMD_TOKEN || '';
    var TURN_URL = CONFIG.API_BASE + (CONFIG.CONSOLE_TURN_PATH || '/webhook/console-turn');

    var CHAR_CAP = 4000;
    var MAX_IMAGE_BYTES = 6 * 1024 * 1024;

    var $ = function (id) { return document.getElementById(id); };
    function el(tag, cls, txt) {
        var n = document.createElement(tag);
        if (cls) n.className = cls;
        if (txt !== undefined && txt !== null) n.textContent = txt;
        return n;
    }
    function scrollLog() { var log = $('cc-log'); if (log) log.scrollTop = log.scrollHeight; }

    /* -------------------- state --------------------
       Session id is minted client-side, entirely independent of the public
       Ask Forte session. Nothing here reads or writes that session. */
    function mintSessionId() {
        var rand = Math.floor(Math.random() * 1e12).toString(36);
        return 'console-' + rand + '-' + Date.now().toString(36).slice(-4);
    }
    var session = { id: null };
    var busy = false;
    var pendingImage = null; // { dataUrl, mime }

    /* -------------------- composer -------------------- */
    function autoGrow(t) {
        t.style.height = 'auto';
        var natural = t.scrollHeight;
        var target = natural <= 48 ? 44 : Math.min(160, natural);
        t.style.height = target + 'px';
    }
    function updateCharCount() {
        var v = $('cc-input').value;
        var counter = $('cc-charcount');
        counter.textContent = v.length + ' / ' + CHAR_CAP;
        counter.classList.toggle('warn', v.length >= CHAR_CAP);
        var hasText = v.trim().length > 0 || !!pendingImage;
        $('cc-send').disabled = !hasText || busy;
    }
    function trySend() {
        var v = $('cc-input').value.trim();
        if ((v.length < 1 && !pendingImage) || busy) return;
        $('cc-input').value = '';
        autoGrow($('cc-input'));
        var image = pendingImage;
        clearAttachment();
        updateCharCount();
        sendMessage(v, image);
    }
    function wireInput() {
        var input = $('cc-input');
        var send = $('cc-send');
        input.addEventListener('input', function () { autoGrow(input); updateCharCount(); });
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey && !send.disabled) { e.preventDefault(); trySend(); }
        });
        input.addEventListener('paste', handlePaste);
        send.addEventListener('click', trySend);
        $('cc-attach-remove').addEventListener('click', clearAttachment);
    }

    /* -------------------- image paste -------------------- */
    function handlePaste(e) {
        var items = (e.clipboardData && e.clipboardData.items) || [];
        for (var i = 0; i < items.length; i++) {
            if (items[i].type && items[i].type.indexOf('image/') === 0) {
                var file = items[i].getAsFile();
                if (!file) continue;
                if (file.size > MAX_IMAGE_BYTES) return; // silently ignore oversize paste
                e.preventDefault();
                readImage(file);
                return;
            }
        }
    }
    function readImage(file) {
        var reader = new FileReader();
        reader.onload = function () {
            pendingImage = { dataUrl: reader.result, mime: file.type };
            $('cc-attach-thumb').src = reader.result;
            $('cc-attach-preview').hidden = false;
            updateCharCount();
        };
        reader.readAsDataURL(file);
    }
    function clearAttachment() {
        pendingImage = null;
        $('cc-attach-preview').hidden = true;
        $('cc-attach-thumb').src = '';
        updateCharCount();
    }

    /* -------------------- turn rendering -------------------- */
    function renderUserBubble(text, image) {
        var t = el('div', 'askf-turn user');
        var b = el('div', 'askf-bubble');
        if (image) {
            var img = document.createElement('img');
            img.src = image.dataUrl;
            img.alt = 'Pasted image';
            img.style.display = 'block';
            img.style.maxWidth = '220px';
            img.style.borderRadius = '10px';
            img.style.marginBottom = text ? '0.5rem' : '0';
            b.appendChild(img);
        }
        if (text) b.appendChild(document.createTextNode(text));
        t.appendChild(b);
        $('cc-log').appendChild(t);
        scrollLog();
    }
    function renderTypingIndicator() {
        var t = el('div', 'askf-turn bot');
        var b = el('div', 'askf-typing');
        b.appendChild(el('span')); b.appendChild(el('span')); b.appendChild(el('span'));
        t.appendChild(b);
        $('cc-log').appendChild(t);
        scrollLog();
        return t;
    }
    function renderBotBubble() {
        var t = el('div', 'askf-turn bot');
        var b = el('div', 'askf-bubble');
        t.appendChild(b);
        $('cc-log').appendChild(t);
        scrollLog();
        return { turn: t, bubble: b };
    }

    var BLANK_RE = /\[[A-Z][A-Z0-9 _-]{1,24}\]/g;
    function appendTextWithBlanks(host, text) {
        var lastIndex = 0, m;
        BLANK_RE.lastIndex = 0;
        while ((m = BLANK_RE.exec(text)) !== null) {
            if (m.index > lastIndex) host.appendChild(document.createTextNode(text.slice(lastIndex, m.index)));
            host.appendChild(el('span', 'cc-blank', m[0]));
            lastIndex = BLANK_RE.lastIndex;
        }
        if (lastIndex < text.length) host.appendChild(document.createTextNode(text.slice(lastIndex)));
    }

    /* Re-render the whole reply from the accumulated raw text on every
       chunk. Replies are chat-sized, so rebuilding is cheap and it keeps
       the READ/DO/checkmark/confirm parsing correct even as lines complete
       mid-stream. Never uses innerHTML on model output -- DOM nodes only. */
    function renderReplyBody(bubble, text) {
        bubble.innerHTML = '';
        var lines = text.split('\n');
        var para = null;
        function flushPara() { para = null; }
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            var trimmed = line.replace(/^\s+/, '');
            var readMatch = /^READ:\s*/i.exec(trimmed);
            var doMatch = /^DO:\s*/i.exec(trimmed);
            var confirmMatch = /^CONFIRM:\s*/i.exec(trimmed);
            var checkMatch = /^(?:✓|\[x\]|- \[x\])\s*/i.exec(trimmed);

            if (readMatch || doMatch) {
                flushPara();
                var row = el('div', 'cc-line');
                row.appendChild(el('span', 'cc-line-tag', readMatch ? 'READ' : 'DO'));
                var body = el('span', 'cc-line-body');
                appendTextWithBlanks(body, trimmed.slice((readMatch || doMatch)[0].length));
                row.appendChild(body);
                bubble.appendChild(row);
            } else if (checkMatch) {
                flushPara();
                var crow = el('div', 'cc-line');
                crow.appendChild(el('span', 'cc-line-tag is-check', '✓'));
                var cbody = el('span', 'cc-line-body');
                appendTextWithBlanks(cbody, trimmed.slice(checkMatch[0].length));
                crow.appendChild(cbody);
                bubble.appendChild(crow);
            } else if (confirmMatch) {
                flushPara();
                var conf = el('div', 'cc-confirm');
                appendTextWithBlanks(conf, trimmed.slice(confirmMatch[0].length));
                bubble.appendChild(conf);
            } else if (trimmed === '') {
                flushPara();
            } else {
                if (!para) { para = el('div', 'cc-para'); bubble.appendChild(para); }
                else para.appendChild(document.createTextNode(' '));
                appendTextWithBlanks(para, line);
            }
        }
        // Trailing streaming cursor while still receiving tokens.
        if (text.length && !text.endsWith('\n')) {
            var cursor = el('span', 'cursor');
            (bubble.lastChild && bubble.lastChild.classList && bubble.lastChild.classList.contains('cc-line-body')
                ? bubble.lastChild : bubble).appendChild(cursor);
        }
    }

    /* -------------------- streaming send --------------------
       Same NDJSON envelope contract as Ask Forte's /forte-ask: lines of
       {"type":"begin"|"item"|"end"}; "item" carries {"content":"..."}. */
    function sendMessage(text, image) {
        if (busy) return;
        busy = true; $('cc-send').disabled = true;
        renderUserBubble(text, image);

        var typing = renderTypingIndicator();
        var botHolder = null;
        var accumulated = '';

        if (!session.id) session.id = mintSessionId();
        var payload = { session_id: session.id, message: text };
        if (image) payload.image = { data: image.dataUrl, mime: image.mime };

        fetch(TURN_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Dashboard-Token': TOKEN },
            body: JSON.stringify(payload)
        }).then(function (resp) {
            if (!resp.ok) throw new Error('console-turn ' + resp.status);
            var reader = resp.body.getReader();
            var decoder = new TextDecoder();
            var lineBuf = '';
            var streamEnded = false;

            function ensureBotBubble() {
                if (!botHolder) {
                    if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
                    typing = null;
                    botHolder = renderBotBubble();
                }
            }
            function processLine(line) {
                var trimmed = line.replace(/^data:\s*/, '').trim();
                if (!trimmed) return '';
                if (trimmed.charAt(0) === '{') {
                    try {
                        var obj = JSON.parse(trimmed);
                        if (obj.type === 'begin') return '';
                        if (obj.type === 'end') { streamEnded = true; return ''; }
                        if (obj.type === 'item') return typeof obj.content === 'string' ? obj.content : '';
                        if (typeof obj.content === 'string') return obj.content;
                        if (typeof obj.text === 'string') return obj.text;
                        if (typeof obj.token === 'string') return obj.token;
                        if (typeof obj.delta === 'string') return obj.delta;
                        return '';
                    } catch (_) { return trimmed; }
                }
                return trimmed;
            }
            function pump() {
                return reader.read().then(function (res) {
                    if (res.done) {
                        if (lineBuf) { var last = processLine(lineBuf); if (last) { ensureBotBubble(); accumulated += last; renderReplyBody(botHolder.bubble, accumulated); scrollLog(); } lineBuf = ''; }
                        finish();
                        return;
                    }
                    if (streamEnded) { finish(); return; }
                    lineBuf += decoder.decode(res.value, { stream: true });
                    var lines = lineBuf.split('\n');
                    lineBuf = lines.pop();
                    var textOut = '';
                    for (var i = 0; i < lines.length; i++) textOut += processLine(lines[i]);
                    if (textOut) {
                        ensureBotBubble();
                        accumulated += textOut;
                        renderReplyBody(botHolder.bubble, accumulated);
                        scrollLog();
                    }
                    return pump();
                });
            }
            function finish() {
                if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
                if (botHolder) renderReplyBody(botHolder.bubble, accumulated); // drop trailing cursor
                busy = false;
                updateCharCount();
            }
            return pump();
        }).catch(function () {
            if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
            var holder = renderBotBubble();
            holder.bubble.textContent = "Couldn't reach the console endpoint just now. Nothing executed -- try again in a moment.";
            busy = false;
            updateCharCount();
        });
    }

    /* -------------------- boot -------------------- */
    function init() {
        wireInput();
        updateCharCount();
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
