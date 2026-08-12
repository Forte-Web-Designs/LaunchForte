# SIM-HS-1 — close-out

Simulated delivery of a real Upwork posting. No client was contacted, nothing was
funded, and every record touched in HubSpot was sample data. This file is the
permanent record of what was built and proven, for whoever opens this engagement
next — including a future Fortress session with no memory of this one.

## Source posting

Upwork job **2083116803740842406**, "HubSpot CRM Expert and Automation Setup." The
posting asked for four things: pipelines, lead nurturing, follow-ups and task
creation, and notifications.

## What was built

n8n draft workflow **`eRWgIpfRg3430MFm`**, "SIM HS: Lead to HubSpot," `active: false`.
Ten nodes, in order:

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

Exported to `docs/fortress/kits/hs-lead-to-hubspot.json`. **That file is not on
`main`** — it was committed on branch `runner/hs-3-add-the-notification-ste`
(commit `cc0a63ee`), which has not been merged. Pull it from there, or wait for
Seth to open a PR, before assuming the path resolves on `main`.

The workflow maps to the posting's four asks: pipeline placement happens in
Create Deal (existing pipelines/stages, nothing new), lead nurturing and
follow-ups run through the contact/deal upsert chain, Create Task covers task
creation, and Log HubSpot Note + Send Notification Email cover notifications.

## Proof — verified by running it, not by reading it

Reading the workflow and its build/check cards both passed at one point in this
engagement's history. Neither reading caught what running it caught. Treat that as
the reason a run card exists at all, and don't skip it on the next engagement.

**Execution 40425** ran the draft against HubSpot portal **51819426** and wrote:

- contact `241618009783`
- deal `63810312501`
- task `114747401768`
- note `114751581580`
- an alert email, Gmail id `19ff7ab881c02500`

The deal and the task both came back associated to that same contact id — the
thing the earlier defects (below) had broken.

**Sample leads used:** Dana Reyes, Kit Alvarez, Morgan Vale, Tomas Vega, Priya
Raman. All invented, all `@example.com`. No real name or contact ever entered this
workflow.

## Defects found only by running it

The build card and its check card had both already passed before these surfaced.
All three were caught in the same run and fixed in card `hs-2`, re-verified by
executions `40322` and `40323`:

1. The deal was attached to nothing — no contact association.
2. The contact id and the deal id were both lost before the Summary node, so the
   summary reported them as missing even on a successful run.
3. The sample-data prefix was applied twice on payloads that already carried it.

Root cause (see the `hs-2` commit): `Merge After Contact` was reading `$json.id`
instead of `$json.vid`, and `Merge After Deal` was reading `$json.id` instead of
`$json.dealId` — both ids came through `undefined`, which HubSpot silently accepts
as "no association" rather than rejecting.

## Left open

- **Pipelines and stages** were used as they already existed in the portal. None
  were created. If the client's real pipeline needs a dedicated stage for this
  flow, that is a follow-on scope item, not something this build assumed.
- **No lead-source property exists in the portal.** Source is written into the
  HubSpot note body instead of a dedicated contact/deal field. If the client wants
  source as a filterable property later, that's a schema change on their portal,
  not a workflow change.
- Nothing in this engagement was ever made live. The workflow's `active` flag has
  never been set to `true`.

## Where things live

| Artifact | Location |
|---|---|
| Draft workflow | n8n `launchforte.app.n8n.cloud`, workflow `eRWgIpfRg3430MFm` |
| Workflow export | `docs/fortress/kits/hs-lead-to-hubspot.json` on branch `runner/hs-3-add-the-notification-ste` (commit `cc0a63ee`) — not yet on `main` |
| Final canvas screenshot | `docs/proof/hs-6-sim-hs-final-canvas.png` (this branch) |
| Build history | branches `runner/hs-1b-*`, `runner/hs-2-*`, `runner/hs-3-*` — none merged to `main` as of this close-out |
