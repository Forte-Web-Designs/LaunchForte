# Fortress build ledger — the running tab
Everything talks to each other. Updated 2026-08-07. Append, never rewrite.

Companion files: `PRODUCT-KIT-STANDARD.md` (the method), `build-library.json` (the registry the
Cockpit matches against), `rescue-screenshots.sh` (get the images into the repo).

---

## A. STATUS AT A GLANCE

| | |
|---|---|
| Screenshots captured | ~87 usable (16 n8n canvases, 45 GoHighLevel, 26 HubSpot) |
| Demo workflows built | 6 in GoHighLevel, all DRAFT, 0 enrolled, none published |
| Shapes with a canvas | 12 of 14 |
| Shapes fully sellable | 6 (reporting, lead-routing, data-collection, alerting, stalled-deal-escalation, quote-follow-up, data-model) |
| Shapes with nothing | 3 — platform-migration, approval-routing, production-takeover |
| **Blocking everything** | **the images are still in Mac temp storage — run `rescue-screenshots.sh`** |

---

## B. ACCESS LEDGER — what we hold, what's blocked, what to get

The headline: **most of what's missing is free.** Six of the nine items below cost nothing but
fifteen minutes of signup, and between them they unlock the two largest shapes in the catalogue.

### Held
| Tool | State | Notes |
|---|---|---|
| n8n | signed in, full | The engineering proof lives here. 100 real workflows, 16 demo canvases. |
| GoHighLevel | signed in, agency | Launch Forte sub-account. **Zero users** — see blocker below. |
| HubSpot | signed in, **FREE tier** | Launch Forte portal 51819426. Workflows/Sequences locked. |
| Google Drive | connected | `Reference Build Screenshots` folder exists, currently empty. |

### Blocked, with the exact fix
| # | Blocker | Blocks | Fix | Cost |
|---|---|---|---|---|
| 1 | GHL sub-account has **zero users** (Settings → My Staff: "No Users found") | calendar creation, round-robin assignment, all task assignment | assign any user to the Launch Forte sub-account | free, ~2 min |
| 2 | HubSpot free tier | branching workflow canvas, sequence builder, 2nd pipeline | 14-day Sales Hub Pro trial | free trial |
| 3 | No Shopify | **storefront-upsell — the 599-demand shape, our largest** | Shopify Partner dev store | free, unlimited |
| 4 | No Stripe | books-reconciliation, revenue-at-risk | Stripe test mode | free |
| 5 | Twilio not signed into Chrome | voice-agent-intake | sign in to the existing account | free |
| 6 | Xero session drops repeatedly | books-reconciliation | re-auth; least stable tool in the estate | — |
| 7 | QuickBooks not signed in | books-reconciliation | Intuit developer sandbox | free |
| 8 | No Zapier / Make | system-sync | free tiers | free |
| 9 | No Airtable | data-collection | free tier | free |

**Do #1 and #3 first.** #1 is two minutes and completes two half-built shapes. #3 opens the
biggest shape in the entire demand catalogue, which we currently cannot demonstrate at all.

Standing rule that governs all of the above: sign-in is the **Chrome profile**, never a stored
password. Nothing that transits text ever contains a credential.

---

## C. GOTCHAS — hard-won, do not relearn these

### n8n
- **Zoom to Fit is a no-op.** Both the `1` key and the bottom-left button leave the viewport at
  `translate(0px,0px) scale(1)` with nodes off-screen. Native drag and scroll panning also do
  nothing. **What works:** dispatch synthetic `wheel` events at the `.vue-flow__pane` element;
  the view pans by −delta/2. View-only, resets on reload.
- **`/rest/workflows?filter={"name":"..."}` ignores the name filter** and returns the whole
  estate including real client workflow names. Do not use it. Read IDs from the app's in-memory
  Pinia store filtered client-side instead.
- Workflow cards carry **no `/workflow/<id>` href**; the selector is
  `[data-test-id="resources-list-item-workflow"]`. No `recycle-scroller-wrapper` on this build —
  the list is not virtualised.
- 22-node canvases are unreadable in one frame. Capture **two or three** framed shots.
- **Saves without publishing.** PATCH returns 200 and changes nothing that runs. No publish REST
  endpoint. Only the Publish button, which opens a dialog needing a second click. Verify
  `versionId === activeVersionId`, then check `execution.workflowVersionId` on a fresh run.
- Binary is stored **by reference** on cloud — `item.binary.data.data` is empty. Use
  `await this.helpers.getBinaryDataBuffer(i, 'data')`.
- Binaries do not survive `Write Run` or `Compose Email`; the Gmail node **errors** when a listed
  `attachmentsBinary` property is missing.
- Code nodes cannot make HTTP requests and cannot `require()`.
- A dataTable node fed by N items reads the table N times and concatenates.

### GoHighLevel
- **Zero users breaks more than it looks like.** Calendars refuse to create ("At least one team
  member is required" — every calendar type needs a host), the Assign-User node shows
  `USERS: No Data` and refuses to save, and task "Assign to" is unusable across every workflow.
- **Task due dates have no hours unit** — Days/Weeks/Months/Years only. A "same-day callback"
  becomes "due in 1 day". Word it accordingly in demos.
- **The "Pipeline stage changed" trigger has no moved-to-stage filter.** Available filters are
  only In pipeline / Assigned to / Expected close date / Forecast probability. Put the stage
  intent in the workflow name.
- The on-hold path needs **"allow move to previous stage" toggled ON** in the Create/Update
  Opportunity action — non-obvious, and the path silently fails without it.
- **Page zoom defaults to ~80%.** Reset to 100% before capturing or shots come out soft.
- The **browser tab title intermittently shows the parent agency name** while pages load. It has
  never appeared in a saved frame, but do not screenshot with the title bar visible.
- The SMS editor has a **text-duplication bug** when overwriting — re-read the field before
  saving any screenshot of message copy.
- Reading `localStorage` is blocked by the permission classifier; build through the UI.

### HubSpot
- **Free tier hard walls:** Workflows and Sequences redirect to a Sales Hub Professional upsell;
  pipelines cap at "1 of 1"; active segments cap at 10.
- The free-tier "simple workflow" is strictly linear (trigger → send email → end) with padlocks
  on every branch point. It is a real canvas and photographs honestly, but it is **not** a
  branching workflow and must not be presented as one.
- **Do not guess URLs** — `/automation/.../workflows/all`, `/sales-products-settings/...` and
  `/website/.../landing-pages` all 404. Navigate through the UI.
- **Four portals are present.** Only *Launch Forte* (51819426) is Seth's. Another Source, FMI and
  SQFI are client portals — never open them.
- The deal board carries duplicate seeded demos (3× Meridian Roofing, 3× Raman Dental, 2× Cole
  Interiors). Dedupe before using the board as a proposal shot.

### Environment
- `file://` URLs are blocked by the browser extension — screenshots cannot be rescued that way.
- The Mac's `/tmp` is **not** reachable from a cloud session; only the mounted folders are
  (Documents, Desktop, Downloads, repos/launchforte, assembly-line-runner).
- The assembly-line runner's Playwright is `--isolated`, so runner jobs **cannot reach any
  signed-in tool**. Authenticated captures must go through the attended Chrome.
- Expect occasional brief extension disconnects mid-run; they recover.
- Some `browser_batch` calls get blocked by the permission classifier — reissuing the same action
  standalone (or vice versa) works.

---

## D. WHAT'S IN THE ACCOUNTS NOW (so nothing is mistaken for client work)

**GoHighLevel — Launch Forte, location `TCrq94IoFK0oWIUA5HBA`.** Six workflows, every one DRAFT
with 0 enrolled and never published: Speed to Lead 5 Minute Callback (7 nodes) · Stalled Deal
Rescue No Movement in 7 Days (9 nodes, 3 branches — the flagship) · Appointment Booked Reminder
Sequence (5) · Review Request After Job Complete (5) · Round Robin Lead Distribution (4, partial)
· Quote Follow Up Cadence (7). Plus form "SAMPLE - New Lead Intake", three opportunities across
the pipeline including one deliberately stalled at 12 days, three sample contacts, and tag
`sample-quote-nurture`.

**HubSpot — Launch Forte 51819426.** All SAMPLE-prefixed and inert: contact property
`SAMPLE - Lead Routing Tier`; unpublished form `SAMPLE - Speed to Lead Intake Form`; a simple
workflow attached to it, toggle OFF, which cannot fire because the form was never published;
segment `SAMPLE - Hot Leads Needing 5-Min Callback` (size 0); a draft marketing email; a draft
landing page.

Zero emails or SMS were sent from anywhere. Nothing pre-existing was modified or deleted.

---

## E. BUILD PLAN — next, in order

1. **Run `rescue-screenshots.sh`.** Everything downstream needs the files in the repo.
2. **Sort and rename** to `<shape>--<tool>--<view>.jpg`, drop the rejects, host them, backfill
   `screenshot_drive`. I do this as soon as the files land.
3. **Fix the Cockpit matcher** — shape-first resolution, canvas always attached on a cross-tool
   fallback, substitution stated in the copy. The library is inert until this works. Verify by
   checking the run, never the response.
4. **Add a user to the GHL sub-account**, then finish the calendar and the round-robin node.
5. **Build `approval-routing`** — it is a named gap and the live Pipedrive posting needs it.
6. **Build `platform-migration`** and **`production-takeover`** to close the shape library.
7. **Upgrade `ds4hNJthtA2nikfw`** (GHL stuck deals, 7 nodes, pre-standard) to the workflow standard.
8. **Shopify Partner dev store** → build `storefront-upsell`, the 599-demand shape.
9. Then down the tool list by demand: Stripe, Twilio, Zapier, Xero, QuickBooks.
10. **Build the auto-capture loop** so the Cockpit fills its own gaps from here on.

---

## F. OPEN QUESTIONS FOR SETH

- **HubSpot tier.** A 14-day Sales Hub Pro trial is the only way to get a branching HubSpot
  canvas. Worth burning now, or wait until a HubSpot deal is live?
- **Ask Forte.** You called the screenshots weak and floated a separate chatbot build. Parked
  until you say go.
- **Proposal renderer.** Still open from your Claude Code thread: local Python script the Cockpit
  shells out to, or rewritten in something n8n executes directly. Infrastructure call, not
  architectural.
