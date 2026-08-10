# Card B — Welcome Email (LF Demo - Lead Capture) — BLOCKED at login

## Status: STOPPED — setup needed, no portal work performed

## What happened
1. Attempted to open the marketing email tool directly in portal 51819426:
   - `https://app.hubspot.com/marketing-email/51819426/edit` → 404 HubSpot Error
   - `https://app.hubspot.com/marketing/51819426/email/list` → 404 HubSpot Error
   (Both likely 404 because the session was never authenticated — HubSpot redirects
   unauthenticated deep-links to an error page rather than to login.)
2. Navigated to `https://app.hubspot.com/login` to establish a session.
3. HubSpot presented its sign-in screen for account `seth@launchforte.com`, offering
   "Sign in with passkey" or "Sign in with password". No stored session/cookie was
   present in this browser context, and no credential or passkey can be supplied by
   an unattended agent.
4. Per standing instructions, this is exactly the case to stop at rather than
   attempt to push through, wait out, or retry.

## No portal actions were taken
- No navigation past the login screen.
- No email created, no draft saved, nothing sent.
- Only file added: this notes file and one screenshot of the login screen
  (`00-login-required.png`) — it shows only the account email
  `seth@launchforte.com` (the Launch Forte house account owner, not a client or
  third party), no contact/recipient data.

## Portal confirmed
Target portal ID per the brief: **51819426**. Every URL attempted above contains
51819426. No other portal ID was seen or used.

## Automatic-send-on-submission question — NOT ANSWERED
Could not be checked — this requires being inside the portal's Automation /
Workflows area (Marketing Hub plan tier gates this feature, typically Professional+
for full workflow automation, with a limited "simple workflow" tier sometimes on
Starter). Since the portal could not be reached, this cannot be confirmed for
51819426 specifically. This must be re-checked once access is available.

## SETUP NEEDED
SETUP NEEDED: HubSpot login | https://app.hubspot.com/login | A human must sign in to the Launch Forte HubSpot account (seth@launchforte.com) in this browser session — via passkey or password — so the automated session is authenticated for portal 51819426. | A code sent to a phone is likely if 2FA/passkey confirmation is required on this device.

## Next steps once access is granted
1. Confirm portal ID 51819426 appears in the URL immediately after login.
2. Navigate to Marketing > Email, create new marketing email, name it
   `LF Demo - Welcome Email`.
3. Set subject: "Thanks for reaching out, we will be in touch shortly" (or close
   variant).
4. Write 4–5 sentence body per the brief using invented sample content only.
5. Save as draft — do not send, schedule, pick recipients, or connect to any list
   or automation. If any dialog offers send/schedule, Cancel/Escape out.
6. Screenshot: editor with subject set, body in place, and the finished draft
   showing unsent state — save under docs/proof/welcome-email/ numbered 01-, 02-, etc.
   (renumber from the login screenshot once real work resumes, or keep it as 00-
   and continue from 01-).
7. Check Automation/Workflows for this portal to answer whether auto-send-on-form-
   submission is available on this plan, and record the finding here.
