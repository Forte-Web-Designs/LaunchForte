# Evidence coverage — status

**564 shippable shots · 22 patterns · 14 tools.** 
Rejects held back and never shipped: 68.

Dry run against the 12 real postings in `jobs.json`: **12 of 12 produce a full four-shot pack, 0 raise a build-gap notice.**

## Per tool

| tool | shots |
|---|---|
| n8n | 171 |
| ghl | 116 |
| hubspot | 50 |
| quickbooks | 42 |
| instantly | 34 |
| shopify | 33 |
| google-sheets | 22 |
| airtable | 21 |
| pipedrive | 20 |
| monday | 15 |
| stripe | 13 |
| zapier | 11 |
| activecampaign | 9 |
| twilio | 7 |

## Per pattern

| pattern | shots | tools |
|---|---|---|
| ai-assistant | 34 | ghl, instantly, n8n |
| alerting | 15 | airtable, google-sheets, n8n, zapier |
| approval-routing | 17 | airtable, n8n, pipedrive |
| books-reconciliation | 49 | n8n, quickbooks, stripe |
| client-onboarding | 23 | ghl, hubspot, n8n |
| cold-outreach | 10 | instantly, n8n |
| data-collection | 53 | activecampaign, airtable, ghl, google-sheets, hubspot, instantly, n8n, shopify, stripe, zapier |
| data-model-architecture | 18 | airtable, hubspot, n8n, pipedrive |
| document-assembly | 9 | n8n |
| lead-routing | 43 | activecampaign, ghl, hubspot, n8n, zapier |
| messaging-compliance | 10 | ghl, instantly, n8n |
| platform-migration | 13 | ghl, hubspot, n8n |
| production-takeover | 8 | n8n |
| project-ops | 18 | monday, n8n |
| quote-follow-up | 15 | activecampaign, ghl, n8n, pipedrive |
| reactivation | 17 | ghl, n8n |
| reporting | 29 | activecampaign, airtable, ghl, google-sheets, hubspot, n8n, pipedrive, quickbooks, shopify, stripe |
| scheduling | 19 | ghl, google-sheets, n8n, quickbooks |
| stalled-deal-escalation | 46 | activecampaign, ghl, hubspot, n8n, pipedrive, zapier |
| storefront-upsell | 32 | n8n, shopify |
| system-sync | 20 | hubspot, instantly, n8n, quickbooks, shopify, stripe, zapier |
| voice-agent-intake | 23 | ghl, n8n, twilio |

## The remaining gap, and it is a capture gap not a code gap

Every combination below resolves to the right pattern and shows the client's own tool, but
that tool holds only ONE shot for that pattern — so beat four (the result) has nothing left to
attach and the pack goes out as three. Three still lands. Four is better.

One frame each closes all of them. The fourth beat's line tells you what to shoot.

| pattern | if the client's tool is | shots we hold | shoot something that shows |
|---|---|---|---|
| alerting | airtable | 1 | And the precision check: how many alerts were actually real. |
| alerting | zapier | 1 | And the precision check: how many alerts were actually real. |
| data-collection | shopify | 1 | And the records it produces, clean and deduplicated. |
| data-collection | stripe | 1 | And the records it produces, clean and deduplicated. |
| data-model-architecture | pipedrive | 1 | And the property architecture underneath it, with fill rates so you can see what's actually use |
| lead-routing | zapier | 1 | And the segmentation behind it, so the right leads reach the right closer. |
| reporting | activecampaign | 1 | And the same layer on a second stack — the numbers move, the structure does not. |
| reporting | ghl | 1 | And the same layer on a second stack — the numbers move, the structure does not. |
| reporting | pipedrive | 1 | And the same layer on a second stack — the numbers move, the structure does not. |
| reporting | shopify | 1 | And the same layer on a second stack — the numbers move, the structure does not. |
| reporting | stripe | 1 | And the same layer on a second stack — the numbers move, the structure does not. |
| scheduling | quickbooks | 1 | And the reminder cadence timed against the appointment rather than a fixed delay. |
| stalled-deal-escalation | activecampaign | 1 | And this is what it looks like once it's running — every stage worked, and the stalled one flag |
| system-sync | instantly | 1 | And the connectors it reconciles across. |
| system-sync | shopify | 1 | And the connectors it reconciles across. |

15 frames closes the last gap.

## What is verified, and how

The dry run builds its harness from the **live** node file every time — never a snapshot.
That matters: the same staleness bug bit twice, once in the node (baked attachments) and once
in the harness (embedded node code). `run-dryrun.py` reads `cockpit-evidence-node.js` off disk.

Captions are pinned where the generic picker cannot know which shot a line is describing.
That pin table now lives in ONE place — `HINT` in `heroes.py` — and is compiled into both the
send list and the Cockpit node, so the two can no longer disagree about which shot a caption names.

