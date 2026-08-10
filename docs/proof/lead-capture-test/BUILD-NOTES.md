# Lead Capture Proof — Card C

**Portal:** Launch Forte, HubSpot portal `51819426` (our own account, no client). All navigation stayed inside this portal — verified before and after every step.

**Form:** `LF Demo - Lead Capture` (form ID `38d46dcb-f6f8-4991-9973-c995b6510ac9`), built in an earlier card.

## How the form was opened without publishing or embedding

Opened via `app.hubspot.com/forms/51819426` → clicked into the form → clicked **View form**, which opened HubSpot's own hosted share link: `https://share.hsforms.com/2ONRty_b4SZGZc8mVtlEKyQuuo4i`. This is HubSpot's native hosted preview URL for a published form — nothing was embedded on any LaunchForte page, and nothing new was published. Submission happened directly on that hosted page.

I also opened the in-app form editor briefly to inspect field structure (needed because the live form and the editor disagreed — see below). Editor was exited via the "Back" link without touching Save or "Review and update" (publish). No changes were made or saved to the form.

## Open question: two fields exist only as unpublished draft changes

The form editor showed a "Saved with unpublished changes" state and 5 fields in the canvas: First Name, Last Name, Email, Company Name, and "What do you need help with?". The **live, publicly-submittable form** (the share link above) only renders 3 fields: First Name, Last Name, Email. Company Name and the help-needed question were added to the draft at some point but never published.

I did not publish those changes — that would be editing/activating something that already exists, which is out of scope for this card. HubSpot's in-editor "Preview" mode was tried as an alternative (the brief explicitly allows preview as a route) but it explicitly states "Preview mode: Submission won't process," so it can't produce a real contact record either.

**Result:** the submission below only carries First Name, Last Name, and Email. Company Name and "What do you need help with?" cannot be verified as captured until someone deliberately publishes the form's pending draft changes — a decision for Seth, not made here.

## Sample data used (invented, not a real person)

- First name: `Wendell`
- Last name: `Kowalczyk`
- Email: `wendell.kowalczyk+lfdemo83920@gmail.com`

**Deviation from the literal brief:** the brief asked for an address "ending in example.com." HubSpot's live form validator actively rejects that — it checks for a resolvable mail domain, and `example.com` (and any other invented, non-resolving domain, tested with `driftwoodfixtures-demo.com` too) fails with "Please enter a valid email address." Only a domain with real MX records passes. I substituted a plus-addressed Gmail alias (`+lfdemo83920`) that is obviously synthetic, was never used before, and does not match any of the 473 existing contacts. No email is ever sent to it — this task never triggers an email send, only a form/contact-record submission.

Wendell Kowalczyk does not exist and was not one of the 473 existing contacts in this portal.

## Fields read back off the created contact record

Contact: `Wendell Kowalczyk`, record ID `241072794778`, portal `51819426`.
URL: `https://app.hubspot.com/contacts/51819426/record/0-1/241072794778`

| Field | Value on record |
|---|---|
| First name | `Wendell` ✅ |
| Last name | `Kowalczyk` ✅ |
| Email | `wendell.kowalczyk+lfdemo83920@gmail.com` ✅ |
| Company name | `--` (empty) — not on the live form, see open question above |
| What do you need help with? | `--` (empty) — not on the live form, see open question above |

Also confirmed: "First conversion" and "Recent conversion" on the contact both read `LF Demo - Lead Capture`, and a "Form submission" activity is logged on the record's timeline at the time of submission.

## Thank-you state

Confirmed. On submit, the hosted form replaced itself with: **"Form submitted — Thank you, we'll be in touch soon."**

## Submission count

- Before: `0` (form's Submissions tab was empty; "Last submission received" showed `-`)
- After: `1` (Submissions tab shows one row for Wendell Kowalczyk; "Last submission received" now shows August 10, 2026)

Note: the Performance tab's "Submissions" summary tile still read `0` at time of check — this looks like reporting/analytics lag on that particular widget, not a real discrepancy. The Submissions list itself (ground truth) and the "Last submission received" field both confirm the count moved from 0 to 1.

## What won at each step

1. Opening the form: HubSpot's own hosted share link (`share.hsforms.com`), reached via the in-app "View form" button — no embed, no new publish.
2. Verifying field structure: the in-app form editor, view-only, exited without saving.
3. Testing submittability of unpublished fields: the editor's "Preview" mode — ruled out because it explicitly disables real submission.
4. Submitting: the live share link, with only the 3 fields that are actually published.
5. Email domain: `gmail.com` with a synthetic plus-addressed local part, since `example.com` and other invented domains fail HubSpot's live domain-validity check.
6. Confirming fields landed: the contact record's "View all properties" panel (searched by "name" and "help"), not just the header summary, since the left-sidebar "Información clave" card is a customized subset that omits Company Name and the custom field entirely.
7. Confirming submission count: the form's own "Submissions" tab list, cross-checked against "Last submission received" on the form overview (the Performance tab's summary tile lagged behind).

## Screenshots (docs/proof/lead-capture-test/)

- `01-empty-form.png` — the empty hosted form
- `02-filled-form.png` — filled with sample data before submitting
- `03-thank-you.png` — thank-you confirmation state
- `04-contact-record-fields.png` — contact record properties: First name, Last name, Company name (empty), plus conversion attribution
- `05-help-field-empty.png` — contact record property "What do you need help with?" (empty)
- `06-submission-count.png` — form overview + Submissions tab showing 1 submission and "Last submission received" date

All screenshots were checked before capture for any real identity (signed-in user chip, avatar, From/Sender line, account owner name, real email address, or existing-contact lists) and cropped/scoped to exclude the HubSpot app chrome where needed.
