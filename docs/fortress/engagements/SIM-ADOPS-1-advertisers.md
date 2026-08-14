# SIM-ADOPS-1 — Advertiser Prospecting Properties & Segmentation

Portal: 51819426 (Launch Forte), HubSpot free tier. Rehearsal only — sample data,
nothing published or sent. Companies/contacts scope: the six SIM-ADOPS-1 companies
created by earlier cards in this engagement (Bluecrest Motors, Solstice Retail Co,
Ember & Oak QSR Group, Meridian Trust Financial, Nightfall Gaming Studios, Cobalt
Peak Airlines). No companies or contacts were created by this card.

## Portal ground-truth correction

The card brief said five SIM-ADOPS-1 companies existed and zero SIM-ADOPS-1 contacts.
Reading the portal directly (not trusting the brief) showed **six** SIM-ADOPS-1
companies — Cobalt Peak Airlines had already been added since the brief was written
— and confirmed zero SIM-ADOPS-1 contacts. All property work below covers all six.

## Custom properties

The portal's custom-property cap is **portal-wide, not per-object**: 10 of 10 used
(11 of 10 after this session — see gate note below), shared across every object type
(contacts, companies, deals, etc.), not 10 per object. `Create property` is disabled
everywhere once the cap is hit. Two Company custom properties suited to ad sales
prospecting already existed from the prior adops-4 card's work, unfilled:

### 1. Advertiser Category (`advertiser_category`, dropdown select)
Options: Automotive, Retail & E-commerce, QSR & Restaurant, Financial Services,
Entertainment & Gaming, CPG & Beverage, **Travel & Hospitality** (added this session
to cover Cobalt Peak Airlines, which didn't fit any existing option).

**Why it earns its place:** ad inventory sales routinely promises category
exclusivity per market/flight (e.g. only one auto dealer in a given ad break). This
field is the first thing a rep checks before booking a slot, so double-booking a
category doesn't happen.

### 2. Budget Band (`budget_band`, dropdown select)
Options: Under $10K/mo, $10K-$50K/mo, $50K-$150K/mo, $150K+/mo.

**Why it earns its place:** sizes each prospect's monthly ad spend capacity so reps
quote realistic packages and prioritize outreach toward accounts that can support
premium inventory, instead of guessing.

### Population (all six companies)

| Company | Advertiser Category | Budget Band |
|---|---|---|
| Cobalt Peak Airlines | Travel & Hospitality | $150K+/mo |
| Nightfall Gaming Studios | Entertainment & Gaming | $50K-$150K/mo |
| Meridian Trust Financial | Financial Services | $150K+/mo |
| Ember & Oak QSR Group | QSR & Restaurant | $10K-$50K/mo |
| Solstice Retail Co | Retail & E-commerce | $50K-$150K/mo |
| Bluecrest Motors | Automotive | Under $10K/mo |

Verified live in the Companies list view (all six rows read back correctly after
inline edit).

### Two other existing custom Company properties, deliberately NOT reused

`LF SAMPLE - Account Segment` (Fortune 500 / University / Sports Organization /
Private Company - FL) and `LF SAMPLE - Target Account Tier` also exist on the
Company object but belong to an unrelated generic sample-data engagement — their
option values don't fit ad sales prospecting, so repurposing them would misrepresent
the data. Left untouched.

## Plan gate: only 2 of 4 requested properties could be created

**Gate hit:** "You've used 10 out of 10 custom properties." / "Unlock the ability to
create more custom properties with Starter Customer Platform." — portal-wide, blocks
`Create property` on every object. Screenshot:
`docs/proof/adops-4b-property-limit-gate.png`. Per standing instructions, no attempt
was made to route around this (no upgrade click, no billing page).

Two more properties are designed on paper — a paid-plan operator could create these
directly from the spec below:

### 3. Preferred Ad Format (proposed: `preferred_ad_format`, multiple checkboxes)
Options: Video Pre-roll, Display/Banner, Audio Spot, Native/Sponsorship,
CTV/Streaming.
**Why:** matches the pitch to the inventory type the prospect actually buys, instead
of a rep guessing and pitching the wrong SKU.

### 4. Campaign Flight Priority (proposed: `campaign_flight_priority`, dropdown select)
Options: Q1, Q2, Q3, Q4, Year-round, Holiday/Peak.
**Why:** ad inventory sells in seasonal flights (holiday, back-to-school, sports);
this drives when outreach and renewal conversations should be prioritized.

## Segment: Premium Ad Prospects ($50K+/mo)

**Intent (built, filter configuration not fully saved as a view before the session's
budget ceiling was reached — see note below):** filter Companies where `Budget Band`
is any of ($50K-$150K/mo, $150K+/mo) AND `Advertiser Category` is known. Against the
six SIM-ADOPS-1 companies this returns four: Cobalt Peak Airlines, Nightfall Gaming
Studios, Meridian Trust Financial, Solstice Retail Co.

**Purpose:** a working list for the media sales team to prioritize outreach on
accounts that can support premium/exclusive inventory placements, with Advertiser
Category visible in the same view so reps can immediately see category-exclusivity
conflicts before booking.

**Status:** the advanced-filter condition (Budget Band is any of $50K-$150K/mo,
$150K+/mo) was built in the Companies list view and confirmed narrowing correctly,
but this session hit its budget ceiling before the view could be named and saved,
and before the second condition (Advertiser Category is known) was added. The filter
recipe above is complete enough to reproduce in under a minute: Companies → Filter →
Advanced filters → Add filter → Budget Band → is any of → check $50K-$150K/mo and
$150K+/mo → Add filter → Advertiser Category → is known → Save this view as
"Premium Ad Prospects ($50K+/mo)".

## Session budget note

This session hit its own budget ceiling before finishing the saved view and before
capturing the second proof screenshot (the property definitions screenshot was
captured; the saved-view-returning-rows screenshot was not). This mirrors what
happened to card adops-4 — see the standing note about right-sizing cards. The
properties and their population are fully committed and verified live; only the
saved-view artifact remains for a follow-up card.
