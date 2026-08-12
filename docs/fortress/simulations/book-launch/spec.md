# Book Launch Funnel — One-Page Build Spec

Simulation. Derived from the Upwork posting for the October 6 book launch build. Six pieces, one page each: what triggers it, what it reads, what it is allowed to write, what happens when it fails.

## 1. Webflow — book landing page + campaign pages

- **Trigger:** manual publish action by the operator once copy and assets are placed in the Webflow Designer.
- **Reads:** supplied copy, brand palette/type system, existing Webflow site styles and symbols, CMS collection data for any dynamic sections.
- **Writes:** new static pages on the existing Webflow site (book one-pager, LinkedIn campaign landing page, email campaign landing page), each in Webflow's own page/CMS store — no writes outside Webflow.
- **On failure:** posting is silent on a failure path here (e.g. broken embed, failed publish); no requirement invented.

## 2. ActiveCampaign — nurture sequence + form capture

- **Trigger:** a visitor submits the native AC form embedded on a Webflow page; sequence start trigger is the form submission or, for the third stage, arrival at the thank-you page.
- **Reads:** submitted form fields, hidden/source fields for routing, existing tag/list/segmentation rules, suppression and consent state for the contact.
- **Writes:** contact record fields, tags, list membership in ActiveCampaign; queues the three-email sequence; does not write to Webflow or any CRM directly (native form-to-AC wiring only, no third-party middleware per the posting).
- **On failure:** posting is silent on what happens if a send fails or a contact is suppressed; no requirement invented.

## 3. Typeform — two scored assessments

- **Trigger:** a respondent opens and completes one of the two Typeform assessments (15–20 questions, branching logic).
- **Reads:** respondent's answers, calculator variables/weights configured per question, hidden fields carrying source/UTM data passed in on load.
- **Writes:** a numeric score and resulting tier on the response; routes the respondent to a tier-specific result page and follow-up sequence; hands the response off into the CRM and email platform (Attio and ActiveCampaign) via each tool's native handoff.
- **On failure:** posting is silent on what happens if the CRM/email handoff fails partway; no requirement invented.

## 4. Canva or Figma — launch asset pack

- **Trigger:** manual production run by the operator ahead of launch week, working from the supplied brand guidelines.
- **Reads:** brand palette, type system, and brand guidelines already supplied by the client.
- **Writes:** social cards, email headers, quote graphics, and landing page assets, delivered as an organized, consistently named file pack — writes only to the design file/export pack, not to any live system.
- **On failure:** posting is silent on a failure/rejection path (e.g. assets don't match brand guidelines); no requirement invented.

## 5. Attio — CRM routing

- **Trigger:** a new or updated record arrives from a form submission (Webflow, Typeform) or another connected tool.
- **Reads:** incoming submission's identifying fields (email and any matching keys) against existing Attio objects to check for an existing record.
- **Writes:** maps the submission into the correct Attio object and attributes, updating an existing record instead of creating a duplicate; Attio is the single source of truth other tools read from and write to.
- **On failure:** posting is silent on what happens on a duplicate-match conflict or failed write; no requirement invented.

## 6. GA4 — event tracking and UTM tagging

- **Trigger:** a page view or on-page interaction on a UTM-tagged campaign URL across the funnel's pages.
- **Reads:** UTM parameters and page/event context from the visitor's session.
- **Writes:** campaign events into GA4; does not write to Webflow, ActiveCampaign, Typeform, or Attio.
- **On failure:** posting is silent on a failure path (e.g. missed UTM tag, dropped event); no requirement invented.
