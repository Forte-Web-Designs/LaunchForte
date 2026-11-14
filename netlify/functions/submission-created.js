/* Branded lead email.
 *
 * Netlify runs a function named "submission-created" automatically after
 * every verified (non-spam) Netlify Forms submission, from any form on the
 * site. This one turns the submission into a readable HTML email for Seth,
 * with Reply-To set to the lead so hitting Reply answers them directly.
 *
 * Sending goes through Resend (https://resend.com). Environment variables,
 * set in Netlify > Site configuration > Environment variables:
 *   RESEND_API_KEY   required. Without it this function does nothing and
 *                    Netlify's own plain notification still arrives.
 *   LEAD_EMAIL_TO    optional, default seth@launchforte.com
 *   LEAD_EMAIL_FROM  optional, default "Launch Forte Leads <onboarding@resend.dev>".
 *                    The resend.dev sender only delivers to the Resend account's
 *                    own address; once launchforte.com is verified in Resend,
 *                    set this to e.g. "Launch Forte Leads <leads@launchforte.com>".
 *
 * Only lead forms are emailed (LEAD_FORMS below). A failure here never
 * affects the visitor: the submission is already stored by the time this runs.
 */

const LEAD_FORMS = { "contact": "Contact page", "quick-contact": "Homepage quote form" };
const SKIP = new Set(["form-name", "subject", "bot-field", "qc-bot", "came_from", "ip", "user_agent", "referrer"]);
const ORDER = ["name", "email", "company", "phone", "topic", "message"];
const LABELS = { name: "Name", email: "Email", company: "Company", phone: "Phone", topic: "Looking for", message: "Message", website: "Website" };

function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function str(v) { return v == null ? "" : String(v).trim(); }
function labelFor(k) { return LABELS[k] || k.replace(/[_-]+/g, " ").replace(/^\w/, (c) => c.toUpperCase()); }

// Netlify file fields arrive as {url, filename} or an array of them.
function files(v) {
    const list = Array.isArray(v) ? v : (v && typeof v === "object" ? [v] : []);
    return list.filter((f) => f && f.url).map((f) => ({ url: String(f.url), name: String(f.filename || f.name || "attachment") }));
}

function buildEmail(form, data, createdAt) {
    const name = str(data.name) || "Someone";
    const first = name.split(/\s+/)[0];
    const email = str(data.email);
    const company = str(data.company);
    const phone = str(data.phone);
    const topic = str(data.topic);
    const message = str(data.message);
    const cameFrom = str(data.came_from);
    const attachments = files(data.attachments);
    const when = (() => {
        try { return new Date(createdAt || Date.now()).toLocaleString("en-US", { timeZone: "America/Chicago", weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) + " CT"; }
        catch (e) { return ""; }
    })();

    // Any other field the form sends (future fields) still shows up.
    const extra = Object.keys(data).filter((k) => !SKIP.has(k) && !ORDER.includes(k) && k !== "attachments" && str(data[k]) && typeof data[k] !== "object");

    const subject = "New quote request: " + name + (company ? " (" + company + ")" : "");
    const replyHref = "mailto:" + encodeURIComponent(email) + "?subject=" + encodeURIComponent("Re: your request to Launch Forte");
    const telHref = "tel:" + phone.replace(/[^\d+]/g, "");

    const row = (label, value) => value ? `
      <tr><td style="padding:10px 0;border-top:1px solid #eef1f4;width:110px;vertical-align:top;font:600 12px/1.5 -apple-system,Segoe UI,Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#6b7480;">${esc(label)}</td>
          <td style="padding:10px 0;border-top:1px solid #eef1f4;font:400 15px/1.5 -apple-system,Segoe UI,Arial,sans-serif;color:#14181f;">${value}</td></tr>` : "";

    const button = (href, text, primary) => `<a href="${esc(href)}" style="display:inline-block;margin:0 8px 8px 0;padding:12px 20px;border-radius:8px;text-decoration:none;font:600 15px/1 -apple-system,Segoe UI,Arial,sans-serif;${primary ? "background:#0088DB;color:#ffffff;" : "background:#ffffff;color:#14181f;border:1px solid #d5dbe3;"}">${esc(text)}</a>`;

    const html = `<!doctype html><html><body style="margin:0;padding:0;background:#f4f6f8;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:24px 12px;"><tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e4e7ec;">
  <tr><td style="background:#0A0A0A;padding:18px 28px;font:600 12px/1.4 -apple-system,Segoe UI,Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#4ab5ed;">New quote request${when ? `<span style="float:right;color:#8a93a0;letter-spacing:.04em;text-transform:none;font-weight:400;">${esc(when)}</span>` : ""}</td></tr>
  <tr><td style="padding:28px 28px 8px;">
    <div style="font:700 26px/1.2 -apple-system,Segoe UI,Arial,sans-serif;color:#14181f;">${esc(name)}</div>
    ${company ? `<div style="margin-top:4px;font:400 16px/1.4 -apple-system,Segoe UI,Arial,sans-serif;color:#515154;">${esc(company)}</div>` : ""}
    ${topic ? `<div style="margin-top:12px;"><span style="display:inline-block;padding:5px 10px;border-radius:999px;background:#e6f2fa;color:#075a8f;font:600 13px/1.2 -apple-system,Segoe UI,Arial,sans-serif;">${esc(topic)}</span></div>` : ""}
    <div style="margin-top:20px;">
      ${email ? button(replyHref, "Reply to " + first, true) : ""}
      ${phone ? button(telHref, "Call " + phone, false) : ""}
    </div>
  </td></tr>
  ${message ? `<tr><td style="padding:12px 28px 4px;">
    <div style="font:600 12px/1.5 -apple-system,Segoe UI,Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#6b7480;margin-bottom:8px;">What they need</div>
    <div style="background:#f6f8fa;border-left:3px solid #0088DB;border-radius:6px;padding:16px 18px;font:400 15px/1.65 -apple-system,Segoe UI,Arial,sans-serif;color:#14181f;">${esc(message).replace(/\r?\n/g, "<br>")}</div>
  </td></tr>` : ""}
  <tr><td style="padding:16px 28px 8px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      ${row("Email", email ? `<a href="mailto:${esc(email)}" style="color:#0088DB;text-decoration:none;">${esc(email)}</a>` : "")}
      ${row("Phone", phone ? `<a href="${esc(telHref)}" style="color:#0088DB;text-decoration:none;">${esc(phone)}</a>` : "")}
      ${row("Company", esc(company))}
      ${extra.map((k) => row(labelFor(k), esc(data[k]))).join("")}
      ${row("Files", attachments.map((f) => `<a href="${esc(f.url)}" style="color:#0088DB;">${esc(f.name)}</a>`).join("<br>"))}
    </table>
  </td></tr>
  <tr><td style="padding:16px 28px 24px;font:400 13px/1.6 -apple-system,Segoe UI,Arial,sans-serif;color:#86868b;border-top:1px solid #eef1f4;">
    <strong style="color:#6b7480;">Came from:</strong> ${esc(cameFrom || "Not recorded")}<br>
    <strong style="color:#6b7480;">Form:</strong> ${esc(LEAD_FORMS[form] || form)} on launchforte.com
  </td></tr>
</table>
</td></tr></table></body></html>`;

    const text = [
        "NEW QUOTE REQUEST" + (when ? " - " + when : ""),
        "",
        name + (company ? " (" + company + ")" : ""),
        email ? "Email: " + email : null,
        phone ? "Phone: " + phone : null,
        topic ? "Looking for: " + topic : null,
        ...extra.map((k) => labelFor(k) + ": " + str(data[k])),
        message ? "\nWhat they need:\n" + message : null,
        attachments.length ? "\nFiles:\n" + attachments.map((f) => f.name + ": " + f.url).join("\n") : null,
        "",
        "Came from: " + (cameFrom || "Not recorded"),
        "Form: " + (LEAD_FORMS[form] || form),
    ].filter((l) => l != null).join("\n");

    return { subject, html, text, replyTo: email };
}

exports.buildEmail = buildEmail;

exports.handler = async (event) => {
    let payload;
    try { payload = JSON.parse(event.body || "{}").payload || {}; } catch (e) { return { statusCode: 200, body: "bad payload" }; }
    const form = payload.form_name || (payload.data && payload.data["form-name"]) || "";
    if (!LEAD_FORMS[form]) return { statusCode: 200, body: "not a lead form" };

    const key = process.env.RESEND_API_KEY;
    if (!key) {
        console.log("submission-created: RESEND_API_KEY not set, branded email skipped (" + form + ")");
        return { statusCode: 200, body: "no key" };
    }

    const mail = buildEmail(form, payload.data || {}, payload.created_at);
    const body = {
        from: process.env.LEAD_EMAIL_FROM || "Launch Forte Leads <onboarding@resend.dev>",
        to: [process.env.LEAD_EMAIL_TO || "seth@launchforte.com"],
        subject: mail.subject,
        html: mail.html,
        text: mail.text,
    };
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail.replyTo)) body.reply_to = mail.replyTo;

    try {
        const resp = await fetch("https://api.resend.com/emails", {
            method: "POST",
            headers: { "Authorization": "Bearer " + key, "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        if (!resp.ok) console.error("submission-created: Resend returned " + resp.status + " " + (await resp.text()).slice(0, 300));
    } catch (err) {
        console.error("submission-created: send failed", err && err.message);
    }
    return { statusCode: 200, body: "ok" };
};
