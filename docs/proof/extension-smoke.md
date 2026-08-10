# Extension Smoke Test — Browser Connection Check

Date: 2026-08-10

## Step 1 — Initial tab
The connected tab was the extension's own relay page, not a normal browsing tab:
- URL: `chrome-extension://mmlmfjhmonkocbjadbfplnigmagldckm/connect.html?...`
- Title: `Welcome`
- Content: `✅ "claude-code" connected.`

## Step 2 — n8n workflows page
Navigated to `https://launchforte.app.n8n.cloud/home/workflows` and let it settle (title went from the default n8n.io landing title to `Workflows - n8n` after ~2s).

- **Signed in: yes.** The Overview page rendered fully — insights tiles (Prod. executions, Failed prod. executions, Failure rate, Run time avg.), the Workflows/Credentials/Executions/Variables/Data tables tablist, and a live paginated list (Total 353 workflows). A signed-out session would show a login form instead.
- **Workspace/account name:** No literal account/email name was found as visible text on the page (searched for "launchforte", "workspace", "@", "Seth" — no matches). The workspace/project name shown throughout the workflow list is **"Personal"** (linked at `/projects/G1EzIclYs4hXjhBw/workflows`), which is the only account/workspace identifier exposed as text on this page.

## Step 3 — Screenshot
Skipped intentionally per instructions — the workflow list contains real client names.

## Usable for real work?
Yes — the browser connection is authenticated into the launchforte n8n instance and rendering live data; it is usable for real work.
