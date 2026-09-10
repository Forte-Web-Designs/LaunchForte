/* Contact form validator.
 *
 * The form on /contact.html posts here instead of directly to Netlify Forms.
 * This function checks that name, email, and message are actually filled in
 * (Netlify does not enforce HTML5 required attributes server side), then
 * forwards the submission to Netlify Forms so it lands in the dashboard and
 * the email notification. Empty and malformed submissions get a 400 and never
 * reach the inbox.
 *
 * The form on /contact.html still carries data-netlify="true" so Netlify
 * registers the "contact" form schema at build time. This function submits
 * to that form server-to-server, which is a documented pattern.
 *
 * Bots that skip client validation (they submit raw POSTs to fingerprint
 * endpoints) now get a 400 and, if they retry, keep getting 400s. Real
 * visitors submit the same form with the same fields; the only difference
 * is the intermediate hop through this function.
 */

const MIN_NAME_LEN    = 2;
const MIN_MESSAGE_LEN = 10;
const EMAIL_PATTERN   = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Netlify Forms submissions are captured when a POST hits any URL on the
// site with the right form-name field. Root is the safest target since it
// definitely exists and is not a redirect.
const FORWARD_URL = "https://launchforte.com/";

function parseFormBody(body, contentType) {
    // Native <form> submits are application/x-www-form-urlencoded.
    // Accept application/json too in case someone wires a JS submit later.
    if (contentType && contentType.indexOf("application/json") !== -1) {
        try { return JSON.parse(body || "{}"); } catch (e) { return {}; }
    }
    const out = {};
    const params = new URLSearchParams(body || "");
    for (const [k, v] of params.entries()) out[k] = v;
    return out;
}

function bad(reason) {
    return {
        statusCode: 400,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
        body: reason,
    };
}

exports.handler = async (event) => {
    if (event.httpMethod !== "POST") {
        return { statusCode: 405, body: "Method Not Allowed" };
    }

    const fields = parseFormBody(event.body, event.headers["content-type"] || event.headers["Content-Type"]);

    // Honeypot: bot-field must be empty. Real humans never see this field.
    if (fields["bot-field"]) return bad("Rejected.");

    // Required fields
    const name    = (fields.name || "").trim();
    const email   = (fields.email || "").trim();
    const message = (fields.message || "").trim();

    if (name.length < MIN_NAME_LEN)         return bad("Name is required.");
    if (!EMAIL_PATTERN.test(email))         return bad("Email is required.");
    if (message.length < MIN_MESSAGE_LEN)   return bad("Message is required.");

    // Rebuild the payload for Netlify Forms. form-name is the trigger that
    // tells Netlify Forms this POST is a submission for the "contact" form.
    // Everything else is forwarded as-is so the dashboard shows every field.
    const forwarded = new URLSearchParams();
    forwarded.set("form-name", "contact");
    for (const [k, v] of Object.entries(fields)) {
        if (k === "bot-field") continue;   // do not forward the honeypot
        forwarded.set(k, v);
    }

    try {
        const clientIp = event.headers["x-nf-client-connection-ip"]
                      || event.headers["x-forwarded-for"]
                      || "";
        const userAgent = event.headers["user-agent"] || "";

        const resp = await fetch(FORWARD_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                // Forward the real client's identity so Netlify Forms captures
                // it on the submission record instead of the function's own IP.
                "X-Forwarded-For": clientIp,
                "User-Agent":      userAgent,
            },
            body: forwarded.toString(),
        });

        if (!resp.ok && resp.status !== 200 && resp.status !== 302) {
            return {
                statusCode: 502,
                headers: { "Content-Type": "text/plain; charset=utf-8" },
                body: "Upstream form submission failed.",
            };
        }
    } catch (err) {
        return {
            statusCode: 502,
            headers: { "Content-Type": "text/plain; charset=utf-8" },
            body: "Could not reach the form endpoint.",
        };
    }

    // Success. Redirect the visitor to a thank-you view. Matches the
    // conventional Netlify Forms success behavior.
    return {
        statusCode: 303,
        headers: { Location: "/contact.html?sent=1" },
        body: "",
    };
};
