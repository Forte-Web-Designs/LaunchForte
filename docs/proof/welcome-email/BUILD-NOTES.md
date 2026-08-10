# Welcome Email — Build Notes (Card B, Lead Capture job)

## Portal confirmed
- Portal: **51819426** (Launch Forte's own HubSpot portal)
- Entry URL: `https://app.hubspot.com/email/51819426` — landed directly on the Marketing Email tool for portal 51819426, no account-picker bounce, no sign-in wall.
- Every subsequent URL visited carried `51819426` in the path. Confirmed before/after each navigation. No portal-switcher use.

## What was built
- **Email name:** `LF Demo - Welcome Email`
- **Type:** Regular marketing email (the "Automated" sending method was locked on this plan — see finding below — so Regular was the only usable option to build a draft in the email tool)
- **Template used:** "Welcome" (one of the unlocked default templates; several other templates on the picker screen were marked "This feature is locked")
- **Subject line:** `Thanks for reaching out, we will be in touch shortly`
- **Body (final):**
  > Thanks for reaching out to Launch Forte. We have received your enquiry and someone from our team will reply within one business day. In the meantime, feel free to reply to this email with any extra details about your project. We look forward to connecting with you soon.
  >
  > The Launch Forte Team
- All content is invented sample copy. No real person, no real company, no claim about a real result. From address shown in the editor is the portal's own connected sender (seth@launchforte.com), not a client identity.
- Email record ID: `219105955942` (from the edit URL `/email/51819426/edit/219105955942/content`)

## Click path (reusable selectors)
1. `https://app.hubspot.com/email/51819426` → Marketing Email manage view (`/manage/state/all`)
2. Click **Create email** → `[data-test-id="email-create-button"]`
3. "Create email" dialog → sending-method picker. **Automated** option showed a locked-feature badge; selected **Regular** → `[data-test-id="email-type-REGULAR"]`
4. Template picker → clicked **Use template** on the "Welcome" card (several other templates showed "This feature is locked" badges on their Use-template buttons)
5. Editor loads at `/email/51819426/edit/219105955942/content`
6. Renamed email: clicked the title textbox → `[data-test-id="email-name"]` → typed `LF Demo - Welcome Email`
7. Subject line: clicked the "Subject line:" summary row → `[data-test-id="subject-info"]` opens the "Edit inbox content" side panel. The actual input is a nested TinyMCE contenteditable div, not exposed as a plain textbox in the accessibility tree — targeted directly via `#react-tinymce-1` (the subject field's TinyMCE container) and typed the subject text into it.
8. Body copy: clicked directly into the body text module inside the canvas iframe (`iframe[name="contentEditor-inpage"]` → the module's `commentable-area` wrapper). This opened the module's own TinyMCE toolbar for in-place editing.

## Where a rung fallback was needed
- The brief warned about a click-catcher overlay intercepting canvas clicks ("element intercepts pointer events"). That specific failure did not occur here — the frame-locator click on the body module landed on the first attempt (rung 1).
- The real obstacle was different: the body module is one TinyMCE rich-text region containing a paragraph + a numbered list + a closing paragraph, all as sibling blocks in one `contenteditable`. Keyboard-driven select-all (`Control+a` then `Delete`) did **not** clear the whole region as expected — it only merged two lines inside one list item, because the simulated key events landed inside a nested block rather than the outer editable root. That change was undone immediately with `Control+z` before it could be saved.
- **Fallback used:** rather than continuing to fight keyboard selection across nested rich-text blocks, the module's `contenteditable` DOM node was located (`#react-tinymce-1` inside the canvas iframe) and its `innerHTML` was set directly via `browser_evaluate` scoped to that element (which runs in the element's own frame), followed by dispatching `input` and `change` events so the editor's React state picked up the change. This is same-origin DOM manipulation within the page HubSpot itself served, not a bypass of any application logic — the editor's own autosave picked up the change immediately afterward and a full page reload from the server confirmed the new body text persisted.
- This DOM-write fallback is the "screenshot plus coordinate"-style fallback in spirit: when the normal interaction path (simulated keystrokes into a nested rich-text editor) didn't behave predictably, the next reliable rung (direct, scoped DOM update + native events) was used instead, and every step was verified with a screenshot and a server-side reload before moving on.

## Draft state as the interface reports it
- After editing, the email was explicitly saved via the **Save** button (`[data-test-id="save-button"]`) in the editor header.
- Navigated to `https://app.hubspot.com/email/51819426/manage/state/draft` (Drafts tab) and confirmed **LF Demo - Welcome Email** is listed there with **Delivered: 0**, **Open rate: 0%**, **Click rate: 0%** — i.e., never sent, never scheduled.
- At no point was **Review and send** clicked through to completion, no recipient list was chosen, and no automation/workflow connection was made. The "Automated" sending method was never selected (it was locked anyway).

## Finding: can this plan auto-send on form submission?
**No — not as a native, no-purchase HubSpot capability on this portal.**

When creating the email, HubSpot's "Create email" dialog offers three sending methods:
- **Regular** — send to a list, immediately or scheduled (used here to build the draft)
- **Automated** — "Send through an automation. These emails can be added to workflows." — shown with a **"This feature is locked"** badge (screenshot: `02-create-email-dialog-automated-locked.png`)
- **Blog** — automatic emails tied to new blog posts (not relevant to form submissions)

The **Automated** email type is what would let a marketing email fire from a workflow triggered by "Form submitted." Because that option is locked on this portal's current plan, there is no way in this account, today, to have HubSpot itself watch the 'LF Demo - Lead Capture' form and automatically send a marketing email in response, without a plan upgrade that unlocks Workflows/Automated email. The template picker also showed multiple templates and the "Create new template" and "Saved templates" options locked, consistent with a Starter/free-tier plan that gates Marketing Hub automation features.

**What is possible on this plan without upgrading:** a team member can be notified of new form submissions (HubSpot's free/starter form notification emails are separate from marketing email and were not touched by this card), and someone can then manually send this drafted welcome email or a similar one from the Regular email tool. True "submit form → welcome email fires automatically, no human step" requires unlocking Automated marketing emails (Workflows), which is a plan upgrade — not attempted or purchased here per instructions.

## Screenshots (docs/proof/welcome-email/)
1. `01-marketing-email-list.png` — Marketing Email list before creating the new email, portal 51819426, showing the pre-existing "SAMPLE - New Lead Welcome Email (draft, do not send)" left untouched.
2. `02-create-email-dialog-automated-locked.png` — Create-email dialog; Automated sending method shown locked, direct evidence for the automation finding.
3. `03-editor-loaded.png` — Fresh "Welcome" template loaded in the editor, before any edits.
4. `04-subject-line-set.png` — Subject-line panel with the subject typed in.
5. `05-subject-confirmed-panel-closed.png` — Panel closed, subject line visible in the summary header ("Thanks for reaching out, we will be in touch shortly").
6. `06-body-content-set.png` — New body copy in place in the canvas, module still selected.
7. `07-draft-final-persisted.png` — Fresh reload of the editor from the server (not cached client state), confirming name/subject/body all persisted.
8. `08-drafts-list-unsent.png` — Drafts tab listing "LF Demo - Welcome Email" with Delivered: 0, proving the unsent state.

No screenshot includes any contact list, recipient list, or panel showing a real person — the "Send to" field was left empty throughout and was never opened into a list picker.
