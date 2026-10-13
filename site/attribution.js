/* First-party attribution for launchforte.com.
 *
 * 1. Remembers how a visitor first arrived (utm_*, gclid, referrer, landing page) for 90 days.
 * 2. Copies it into hidden fields on the contact form, so every Netlify Forms submission says where the lead came from.
 * 3. Adds the same utm_* values to every Calendly link, so Calendly records the source on the booking.
 * 4. Pushes dataLayer events GTM can turn into GA4 key events:
 *      calendly_click   - a Calendly link was opened
 *      calendly_booked  - Calendly's embed reported a scheduled meeting
 *    (contact_sent is pushed by contact.html after the form is accepted.)
 *
 * No cookies, no third-party calls. Storage can be unavailable (private mode); everything degrades to "unknown".
 */
(function () {
  var KEY = "lf_attr_v1";
  var DAYS = 90;
  var FIELDS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"];

  function read() {
    try {
      var raw = window.localStorage.getItem(KEY);
      if (!raw) return null;
      var v = JSON.parse(raw);
      if (!v || !v.at || Date.now() - v.at > DAYS * 864e5) return null;
      return v;
    } catch (e) { return null; }
  }
  function write(v) { try { window.localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }

  var params;
  try { params = new URLSearchParams(window.location.search); } catch (e) { params = null; }
  var now = {};
  var hasCampaign = false;
  for (var i = 0; i < FIELDS.length; i++) {
    var val = params ? params.get(FIELDS[i]) : null;
    if (val) { now[FIELDS[i]] = val.slice(0, 200); hasCampaign = true; }
  }
  var ref = document.referrer && document.referrer.indexOf(window.location.host) === -1 ? document.referrer.slice(0, 300) : "";

  var first = read();
  // A new campaign click replaces the stored touch; plain internal navigation never does.
  if (!first || hasCampaign) {
    first = { at: Date.now(), landing: window.location.pathname.slice(0, 200), referrer: ref };
    for (var k in now) first[k] = now[k];
    if (!hasCampaign && !first.utm_source && ref) {
      try { first.utm_source = new URL(ref).hostname; first.utm_medium = "referral"; } catch (e) {}
    }
    write(first);
  }
  var attr = first || {};

  // 2. Contact form hidden fields (declared in contact.html so Netlify Forms keeps them).
  function fillForm() {
    var form = document.getElementById("contact-form");
    if (!form) return;
    var names = FIELDS.concat(["landing", "referrer"]);
    for (var j = 0; j < names.length; j++) {
      var input = form.querySelector('input[name="' + names[j] + '"]');
      if (input && !input.value) input.value = attr[names[j]] || "";
    }
  }

  // 3. Calendly links carry the source.
  function tagCalendly() {
    var links = document.querySelectorAll('a[href*="calendly.com"]');
    for (var j = 0; j < links.length; j++) {
      try {
        var u = new URL(links[j].href);
        for (var f = 0; f < FIELDS.length; f++) {
          var name = FIELDS[f];
          if (name === "gclid") continue; // Calendly only passes utm_*
          if (attr[name] && !u.searchParams.get(name)) u.searchParams.set(name, attr[name]);
        }
        if (!u.searchParams.get("utm_content")) u.searchParams.set("utm_content", window.location.pathname.slice(0, 80));
        links[j].href = u.toString();
        links[j].addEventListener("click", function () {
          window.dataLayer = window.dataLayer || [];
          window.dataLayer.push({ event: "calendly_click", page: window.location.pathname, source: attr.utm_source || "direct" });
        });
      } catch (e) {}
    }
  }

  // 4. Calendly embed reports a booking through postMessage.
  window.addEventListener("message", function (e) {
    if (!e || typeof e.origin !== "string" || e.origin.indexOf("calendly.com") === -1) return;
    var d = e.data;
    if (d && d.event === "calendly.event_scheduled") {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: "calendly_booked", page: window.location.pathname, source: attr.utm_source || "direct" });
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { fillForm(); tagCalendly(); });
  } else { fillForm(); tagCalendly(); }
})();
