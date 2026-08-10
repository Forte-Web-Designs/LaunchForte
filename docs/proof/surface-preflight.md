# Surface Preflight Survey

Read-only check of which external surfaces this browser profile can already
reach signed in, run 2026-08-10. No records, workflows, or contacts were
opened or modified; this only reports what was found.

| Surface | Signed in? | Account / URL observed | What a human needs to do |
|---|---|---|---|
| n8n (`launchforte.app.n8n.cloud/home/workflows`) | Yes | Workspace subdomain reads `launchforte` — this is the Launch Forte n8n workspace | Nothing — already usable. |
| HubSpot (`app.hubspot.com/`) | No | Redirected to `https://app.hubspot.com/login` (sign-in page, no session) | A human needs to log in to HubSpot in this browser profile with Launch Forte credentials before any HubSpot job can run. |
| GoHighLevel (`app.gohighlevel.com/`) | Yes, but **wrong account** | Signed in as **"First Cornerstone Group LLC"** — not Launch Forte. Per standing instructions, this surface was not touched further: no clicks, no menus opened, no screenshot of account content (a Google account-chooser popup for a different sign-in also appeared but was not interacted with). | A human needs to sign out of the "First Cornerstone Group LLC" GoHighLevel session in this browser profile and sign back in with the correct Launch Forte GoHighLevel account. Until that happens, this surface must not be used for any Launch Forte job — it currently carries a live session for a different business. |

## Notes
- No screenshots of workflow lists, contacts, or other records were taken or kept. An initial n8n screenshot was captured that inadvertently showed workflow titles; it was deleted immediately after review and is not included here.
- `docs/proof/hubspot-signin.png` is the only screenshot kept, and it shows only the empty HubSpot sign-in page.
