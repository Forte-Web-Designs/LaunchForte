# SIM-HS-1 — close-out

Simulated delivery of a real Upwork posting. No client was contacted, nothing was
funded, and every record touched in HubSpot was sample data throughout. This file
is the permanent record of what was built and proven, written for whoever opens
this engagement next — including a future Fortress session with no memory of this
one.

## Source posting

Upwork job **2083116803740842406**, "HubSpot CRM Expert and Automation Setup." The
posting asked for four things: pipelines, lead nurturing, follow-ups and task
creation, and notifications.

## What was built

n8n draft workflow **`eRWgIpfRg3430MFm`**, "SIM HS: Lead to HubSpot," `active: false`
on `launchforte.app.n8n.cloud`. Ten nodes, in order:

1. Lead Webhook
2. Read Lead Fields
3. Upsert Contact
4. Merge After Contact
5. Create Deal
6. Merge After Deal
7. Create Task
8. Log HubSpot Note
9. Send Notification Email
10. Summary

Exported to `docs/fortress/kits/hs-lead-to-hubspot.json`. **That path does not
exist on `main` or on this branch.** The export was committed on
`runner/hs-3-add-the-notification-ste` (commit `cc0a63ee`), which has never been
merged. Anyone who needs the export file has to pull it from that branch, not
assume it resolves off `main`.

## Proof — verified by running it, not by reading it

A build card and its check card on this engagement both passed before the
defects below were found. Neither passed by accident — reading the workflow and
running it are different tests, and only running it caught what was wrong. Don't
skip the run step on the next engagement on the strength of a passing read.

**Execution 40425** ran the draft against HubSpot portal **51819426** and wrote:

- contact `241618009783`
- deal `63810312501`
- task `114747401768`
- note `114751581580`
- an alert email, Gmail id `19ff7ab881c02500`

The deal and the task both came back associated to that same contact id — the
exact thing the defects below had broken.

**Sample leads used:** Dana Reyes, Kit Alvarez, Morgan Vale, Tomas Vega, Priya
Raman. All invented, all `@example.com`.

## Defects found only by running it

All three surfaced in the same run, after the build card and its check had both
already passed. All three were fixed in card `hs-2` and re-verified by executions
`40322` and `40323`:

1. The deal was attached to nothing — no contact association.
2. The contact id and the deal id were both lost before the Summary node.
3. The sample-data prefix was applied twice on payloads that already carried it.

## Left open

- **Pipelines and stages** were used as they already existed in the portal. None
  were created.
- **No lead-source property exists in the portal.** Source rides in the HubSpot
  note body instead of a dedicated contact/deal field.
- Nothing in this engagement was ever made live. The workflow's `active` flag has
  never been set to `true`.

## Where things live

| Artifact | Location |
|---|---|
| Draft workflow | n8n `launchforte.app.n8n.cloud`, workflow `eRWgIpfRg3430MFm`, `active: false` |
| Workflow export | `docs/fortress/kits/hs-lead-to-hubspot.json` on branch `runner/hs-3-add-the-notification-ste` (commit `cc0a63ee`) — not on `main` |
| Final canvas screenshot | `docs/proof/hs-6-sim-hs-final-canvas.png` |
| Build history | branches `runner/hs-1b-*`, `runner/hs-2-*`, `runner/hs-3-*` — none merged to `main` as of this close-out |
