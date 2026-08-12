# Content Platform — Data Model & Build Spec

Source: Upwork posting, "Multi-Site AI Content Planning & Automated WordPress Publishing Platform." This is a simulation artifact — no build, no client, nothing activated.

## 1. The Seven Levels

The posting's hierarchy, top to bottom:

1. **Website** — the isolation boundary; owns every setting that must not cross into another site.
2. **Content Plan** — the strategic period (3/6/12 months) that decides which clusters get built.
3. **Content Cluster** — the primary organizational unit; one commercial/informational subject and everything built to establish authority on it.
4. **Content Asset** — an individual piece of content belonging to a cluster.
5. **Production Workflow** — the state an asset moves through on its way to publishable.
6. **Publishing Calendar** — when a ready asset is due to go out.
7. **WordPress** — the destination the asset is written to.

## 2. Fields and Parentage Per Level

### Website
Parent: none (top of the hierarchy; the tenant/account boundary).
Fields: brand rules, business information, products/services, target customers, geographic markets, SEO strategy, AI knowledge/context, competitors, approved templates, prompt rules, WordPress connection, publishing rules.

### Content Plan
Parent: Website (one plan belongs to exactly one website).
Fields: planning period (3, 6, or 12 months), business priorities, products/services, target markets, existing website content, search opportunities, customer questions, commercial search intent, informational search intent, competitor content, existing content gaps, seasonal opportunities, geographic opportunities. Output: the set of Content Clusters it determines are needed.

### Content Cluster
Parent: Content Plan.
Fields: strategic objective, target customer, primary topic, search intent, primary keywords, supporting keywords, commercial objective, products/services supported, target locations (where relevant), pillar content, supporting content, internal linking strategy, required media, publishing sequence, and a derived completeness view (per-asset status, e.g. Created / Approved / Published / Scheduled / Awaiting Review / Draft / Planned) used to judge authority-building, not article count.

### Content Asset
Parent: Content Cluster.
Fields: asset type (pillar page, service page, product/category landing page, industry landing page, geographic landing page, Knowledge Centre article, supporting article, buying guide, comparison page, FAQ, case study, video, video script, video brief, infographic, downloadable resource — the posting requires this type list to be extensible without a rebuild), the content itself, and its linking relationships (link to its pillar, links from the pillar and sibling supporting assets to it), since the posting requires the system to understand relationships between assets for internal linking.

### Production Workflow
Parent: Content Asset (it tracks one asset's progress).
Fields: the posting is silent on a distinct workflow entity or its fields beyond the status values it shows on assets (Draft, Awaiting Review, Created, Approved, Scheduled, Published, Planned) — treated here as the state machine an asset moves through.

### Publishing Calendar
Parent: Content Cluster (a cluster's assets carry a "publishing sequence," and its assets show a "Scheduled" state), spanning the Content Plan's period.
Fields: the posting is silent on explicit calendar-entry fields beyond the scheduling implied by an asset's "Scheduled" status and the cluster's publishing sequence.

### WordPress
Parent: Website (via the Website's own "WordPress connection" field).
Fields: the posting is silent on any WordPress-level entity or fields beyond being the connected destination that receives an approved, scheduled asset.

## 3. The Isolation Rule

The posting states website information must never leak into another website's AI content. Enforcement points:

- Every Content Plan, Content Cluster, Content Asset, and Publishing Calendar record carries a foreign key to exactly one Website, and all reads/writes are scoped to that key.
- AI generation for a given asset draws brand rules, business information, competitors, prompt rules, and AI knowledge/context only from the one Website record that owns the asset's cluster, never merged across websites.
- The WordPress connection and publishing rules used at the publish step are the ones stored on that same owning Website, so an asset can only ever be written to its own site.

The posting does not specify enforcement mechanics beyond this (e.g. database-level tenancy, row-level security) — it states the requirement, not the implementation.

## 4. The Publish Step

- **Trigger:** the posting is silent on the exact trigger mechanics; the only signal it gives is an asset reaching "Scheduled" status against its place in the Publishing Calendar/cluster publishing sequence.
- **Reads:** the Content Asset's approved content, the asset's type/template, and the owning Website's WordPress connection and publishing rules.
- **Allowed to write:** the target WordPress site (create/update the corresponding post/page) and the asset's own status (e.g. Scheduled → Published) and the cluster's completeness view.
- **On failure:** the posting does not specify retry, rollback, or alerting behavior for a failed publish — no requirement is invented here.
