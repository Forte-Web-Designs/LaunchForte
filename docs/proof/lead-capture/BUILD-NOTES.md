# LF Demo - Lead Capture — Build Notes (Card A)

## Portal confirmed
HubSpot portal **51819426** ("Launch Forte", user Seth Forte). Every URL visited during
this build carried `51819426` in the path — confirmed before and after each navigation
via `browser_snapshot` page URL and via the "Launch Forte" account label in the top-right
nav. No portal switcher was used.

## Form
- **Name:** `LF Demo - Lead Capture`
- **Location:** HubSpot Marketing > Forms, portal 51819426
  (`app.hubspot.com/forms/51819426/new-editor/38d46dcb-f6f8-4991-9973-c995b6510ac9`)
- **Editor used:** New Form Editor (drag-and-drop), started from the "Start from blank" template.
- **Status after save:** Draft/auto-saved by HubSpot's form editor ("Saved with unpublished
  changes" shown in the editor header at every step). The form list shows it with the same
  "Published" system status and "Appears on: No HubSpot places" / 0 submissions as the two
  pre-existing SAMPLE forms in this portal — that is HubSpot's default state for a form that
  exists but has not been embedded anywhere. It was never placed on a page, never connected
  to a list, workflow, or email, and the "Review and update" action (which pushes live embed
  changes) was deliberately never clicked.

## Fields created
| Label | Field type | CRM property | Required |
|---|---|---|---|
| First Name | Single-line text (built-in "Email" template default) | Contact: `firstname` | No |
| Last Name | Single-line text (built-in template default) | Contact: `lastname` | No |
| Email | Email | Contact: `email` | **Yes** |
| What do you need help with? | Single-line text | Contact: new custom property `what_do_you_need_help_with` (created during this build) | No |
| Company Name | Single-line text | Contact: `company` (existing standard property) | No |

Email's required toggle was already ON by default in HubSpot's blank template; verified and
screenshotted explicitly (see `03-email-field-required.png`).

## Submit button / thank-you message
- Submit button label changed from default "Submit" to **"Get My Free Consultation"**.
- "On submission" behavior left on **"Show thank you message"** (not redirect).
- Thank-you message rich text changed from the default "Form submitted / Thank you, we'll be
  in touch soon." to: **"Thanks! We received your info and will follow up shortly."**

## Click path / selectors worth reusing
1. `https://app.hubspot.com/forms/51819426` → Forms list → `[data-test-id="form-creation-button"]` (Create form)
2. Form type screen → Form Editor pre-selected → `[data-test-id="next-form-type"]` (Next)
3. Template screen → "Start from blank" card → `[data-test-id="choose-template-button"]` (first one)
4. In editor: `[data-test-id="header-name-input"]` — form title field
5. Left toolbar "+" icon (add field) opens a field-type picker panel; each type tile is a
   text-only clickable row (no stable data-test-id per type) — matched by visible text via
   `getByText(...)`. Caution: the tiles render with obfuscated `············` placeholder text
   around the real label until hover/paint settles, so a text-based click matched the wrong
   tile once (added "Multi-line text" instead of "Single-line text" for the help-with field) —
   corrected via the field's own "Field type" dropdown
   (`[data-test-id="field-type-dropdown-select"]`) rather than re-adding the field.
6. Property connect panel: `[data-test-id="property-search-input"]` to search, then either pick
   an existing property checkbox (e.g. `[data-test-id="property-list-item--0-1/company"]` for
   Company Name) or `[data-test-id="create-new-property-button"]` → fill
   `[data-test-id="property-label-input"]` → `[data-test-id="modal-save-button"]` for a new one.
7. Field panel close: `[data-test-id="sidepanel-close-button"]`.
8. Submit button edit: click the canvas Submit button (`[data-test-id="submit-button"]`) →
   `[data-test-id="label-text-input"]` for the label text, radio group for on-submit behavior.
9. Thank-you message edit: click the "Form submitted" text block in the right-hand success
   panel → "Edit in expanded view" button → click into the rich-text iframe
   (`iframe[title="Rich Text Area"]`, `getByLabel('Rich Text Area. Press ALT-0...')`) →
   select-all + type replacement copy → "Back to form".

No click-catcher/overlay interception was hit in this build — every element resolved via a
normal `browser_click` with a `data-test-id` or accessible-name locator. The documented
fallback rung (screenshot + coordinate click) was not needed at any step.

## Screenshots (in order, under docs/proof/lead-capture/)
1. `01-form-editor-initial.png` — form renamed to "LF Demo - Lead Capture", default First
   Name/Last Name/Email fields visible.
2. `02-all-fields-added.png` — all five fields present: First Name, Last Name, Email, What do
   you need help with?, Company Name.
3. `03-email-field-required.png` — Email field settings panel, "Required field" toggle shown ON.
4. `04-submit-and-thankyou.png` — Submit button relabeled "Get My Free Consultation" and the
   updated thank-you message visible in the right-hand success-state preview.
5. `05-form-saved-in-list.png` — Forms list showing "LF Demo - Lead Capture" saved, 0
   submissions, "Appears on: No HubSpot places" (not embedded/connected anywhere).

No screenshot includes the contacts list or any real-person record — only the form editor
canvas and the forms management list (which shows form names and "Seth Forte" as
creator/updater, no contact data).

## Time taken
Roughly 40–45 minutes of tool-call time in-session (build + verification + screenshots + notes).

## What the plan didn't let me do (by design, not a limitation hit)
- Did not embed the form on any page or asset.
- Did not connect it to a list, workflow, or email (that is Card B's job).
- Did not click "Review and update" / any explicit "publish" action beyond HubSpot's own
  editor auto-save.
- Used only invented/no sample data — no text was typed into the form's own input fields
  (labels/placeholders only), so no example.com or fake-name data was needed for this card.
