# UI Reach: n8n Workflow Version — Proof

## Account and instance confirmed
- Instance: `https://launchforte.app.n8n.cloud`
- Signed-in account: **Seth Forte**, `seth@launchforte.com`, role **Owner**
- Confirmed by opening the user Settings > Personal panel (`/settings/personal`) and reading the account name, role badge, and email back from the page — no changes made there. Dialog was closed by navigating away, nothing was saved on that screen.

## Target item
- Workflow ID: `mLhUCREosvsYZSRB`
- Workflow name: `Probe: UI Reach Test (safe, inactive)`
- URL: `https://launchforte.app.n8n.cloud/workflow/mLhUCREosvsYZSRB`

## Version identifier
- **Before:** an unnamed draft entry labeled "Current changes" in the Version History list, backing UUID `f0009643-a430-4a53-b643-07fd55b68589` (visible in the history URL `/workflow/mLhUCREosvsYZSRB/history/f0009643-a430-4a53-b643-07fd55b68589` and pre-filled into the "Name version" dialog as `Version f0009643`).
- **After:** the same UUID (`f0009643-a430-4a53-b643-07fd55b68589`) is now stored as a named version, **"Version f0009643"**, with description "Driven by the runner as a reach test.", authored by Seth Forte, timestamped Aug 10 at 09:25:30.

## How the change was driven
Note: the top-right **Publish** button was disabled with the tooltip "This workflow has no trigger nodes that require publishing" (this probe workflow's trigger is a manual "When clicking Execute" node, so the Publish/Unpublish action does not apply to it). The version-naming action lives one level down, in the split-button's dropdown ("More actions" chevron next to Publish) as **Name version** (⌘S) — this opens the exact two-step dialog described for the job: a "Version name" field pre-filled with `Version f0009643`, and a "Describe changes (optional)" box.

1. Opened `/home/workflows`, confirmed the signed-in account (Seth Forte / Launch Forte instance) via Settings > Personal, closed without changes.
2. Navigated to `/workflow/mLhUCREosvsYZSRB`.
3. Screenshot before: `docs/proof/ui-reach-n8n-before.png` (shows workflow name and the full top-right button row: `Publish` (disabled) + chevron, `Version History`, `Actions`).
4. Clicked the chevron next to `Publish` (`data-test-id="version-menu-button"`), then clicked **Name version** (`data-test-id="version-menu-item-name-version"`) in the dropdown that appeared — this is the top-right control that opens the two-step dialog.
5. In the dialog: left "Version name" exactly as pre-filled (`Version f0009643`); typed `Driven by the runner as a reach test.` into "Describe changes (optional)" (`data-test-id="workflowHistoryNameVersion-description-input"`).
6. Clicked the orange **Save** button (`data-test-id="workflowHistoryNameVersion-submit-button"`, confirmed via computed CSS `background-color: lab(63.6491 55.8045 72.8887)` — an orange hue).
7. A toast confirmed: "Version name updated successfully."
8. Screenshot after: `docs/proof/ui-reach-n8n-after.png` (shows the same editor with the success toast visible).
9. Navigated to `/workflow/mLhUCREosvsYZSRB/history` and read the resulting list entry back from the application: it now reads "Version f0009643 — Seth Forte, Aug 10 at 09:25:30" with the description "Driven by the runner as a reach test." under the same history UUID (`f0009643-a430-4a53-b643-07fd55b68589`) the draft carried before the save — confirming the press landed and the stored identifier matches the pre-save draft identifier.

## Ladder rung
**Plain locator**, driven through Playwright MCP browser tools using accessibility-tree element refs / `data-test-id` selectors (e.g. `[data-test-id="version-menu-button"]`, `[data-test-id="version-menu-item-name-version"]`, `[data-test-id="workflowHistoryNameVersion-description-input"]`, `[data-test-id="workflowHistoryNameVersion-submit-button"]`). No frame locator, network/storage read, or coordinate-click was needed — every control was reachable and clickable by its accessible role/name or stable `data-test-id`, and the resulting state was read back from the rendered page (toast message, then the Version History list and its URL) rather than assumed.

No earlier rungs were tried and abandoned — plain locators worked on the first attempt for every step.
