# Fortress system map — GENERATED, do not hand-edit

Regenerate with `docs/fortress/generators/system-map.js` in the browser console on a
`launchforte.app.n8n.cloud` tab, then `copy(__MD)` and paste over this file.
It reads the deployed workflows, so it is true by construction. If this file
disagrees with the tenant, the file is stale — regenerate it rather than argue.

---

## Ops: Build Queue API

`nuNkZu0VqDVwtS9d` · 106 nodes · ACTIVE

### `POST /webhook/build-claim-9f2ad4c7`

- **data tables:** ops_state, build_queue, lessons, tasks, tools_kb
- **chain:** Claim In → Claim Auth → Claim Auth If → Read Ops (Claim) → Respond Unauthorized → Stop All? → Respond Stopped → Read Queued → Pick Job → Claim Gate → Empty Gate → Mark Running → Read Lessons (Claim) → Mark Task In Progress → Notify Claimed → Read Tools KB (Claim) → Claim Body → Respond Claim

### `POST /webhook/build-report-9f2ad4c7`

- **data tables:** build_queue, tasks, engagements, F5vZVMEHiMIBLgeN
- **saved connections:** Anthropic, Forte Web Designs GitHub, Gmail account
- **chain:** Report In → Report Auth → Report Auth If → Build Update → Respond Unauthorized → Write Report → Verify Row → Report Body → Non-Done Status? → Build Rating Prompt → Respond Report → Get Report Task Row → Rate Job → Prep Token → Get Engagement Row → Parse Rating → Has Task Row? → Compute API Spend → Save Rating → Update Task Row → Shape Task Row → Update Engagement Spend → Lesson Worth Filing? → Criteria Gate → Create Task Row → Log Lesson → Build Criteria Prompt → Lead Gate If → Derive Criteria → Prep Diff Fetch → Stuck Gate If → Apply Criteria → Fetch Real Diff → Lead: Triage Prompt → Build Report Email → Save Criteria → Shape Diff → Lead: Triage Validate → Pretty Report → Needs An Eye? → Ask Prompt → Lead: Parse Triage → Add CC Link → Queue The Check → Summarise Ask → Add CC Link Send Report Email → Parse Ask → Shot List → Lead: Build Prompt → Any Shots? → Lead: Validate → Fetch Shot → Send Report Email (no proof) → Lead: Parse Verdict → Shot To JPEG → Lead: Pass? → Make Proof PDF → Lead: Stamp Pass → Lead: Fail Update Row → Has Proof? → Send Report Email

### `GET /webhook/approve-report`

- **data tables:** tasks
- **chain:** Approve Report Webhook → Get All Tasks → Process Approve → Not Found? → Respond Not Found → Already Processed? → Respond Already Processed → Approve: Update Task Row → Respond Approved

### `GET /webhook/request-changes`

- **data tables:** tasks
- **chain:** Request Changes Webhook → Get All Tasks 2 → Process Request Changes → Not Found? 2 → Respond Not Found 2 → Already Processed? 2 → Respond Already Processed 2 → Respond Form

### `POST /webhook/request-changes-submit`

- **data tables:** tasks
- **chain:** Request Changes Submit Webhook → Get All Tasks 3 → Process Request Changes Submit → Not Found? 3 → Respond Not Found 3 → Already Processed? 3 → Respond Already Processed 3 → Request Changes: Update Task Row → Respond Submitted

---

## Ops: Dashboard API

`XOjXyxgywZJK3G5x` · 82 nodes · ACTIVE

### `POST /webhook/build-enqueue`

- **data tables:** build_queue, tasks
- **saved connections:** Anthropic
- **chain:** Enqueue In → Enqueue Guard → Enqueue Guard If → Check Dupe → Enqueue Body → Dupe Gate → Respond Enqueue → Dupe Gate If → Draft Criteria → Criteria Guard → Task Dupe Check → Task Dupe If → Write Task → Write Queue

### `GET /webhook/dashboard-snapshot`

- **data tables:** clients, engagements, tasks, build_queue
- **chain:** Snapshot In → Get Clients → Get Engagements → Get Tasks → Get Queue → Merge1 → Code in JavaScript → Respond to Webhook

### `POST /webhook/task-note`

- **data tables:** clients, tasks
- **saved connections:** Anthropic, Gmail account
- **chain:** Task Note In → Route Note → Switch → Draft Criteria1 → Get Client Row → Get Task Row → Note Error → Criteria Guard1 → Append Note → Update Task → Merge → Read Open Tasks → Update Client → Respond to Webhook1 → Dupe Check → Write Task1 → Access Needed? → Draft Access Ask → Access Ask Call → Parse Access Ask → Add CC Link Email Access Ask → Email Access Ask

### `POST /webhook/console-turn`

- **data tables:** clients, tasks, engagements, console_turns
- **chain:** Console Turn In → Validate Console → Console Blocked? → Get Console Client → Respond Console Blocked → Get Console Tasks → Get Console Engagements → Get Pricing Repository → Build Console Context → AI Agent → Log Console Turn → Save Console Turn

### `POST /webhook/pack-request`

- **data tables:** tasks, clients
- **chain:** Pack Request In → Validate Pack Request → Blocked? → Respond Pack Blocked → Get Task Row2 → Get Client Row2 → Build Pack Text → Respond Pack Success

### `POST /webhook/drop-box`

- **data tables:** clients, tasks
- **saved connections:** Anthropic
- **chain:** Drop Box In → Get Clients (Drop Box) → Get Open Tasks → Build Classify Request → Classify → Parse Classification → Classification OK? → File It → Respond Drop Box Fallback → Build Echo → Respond Drop Box

---

## Proposal: Cockpit

`Hl5zah3PZcHaEkuo` · 56 nodes · ACTIVE

### `POST /webhook/cockpit-submit-754cf2072a1fa8eb684043f8`

- **data tables:** upwork_jobs, proposal_template, lessons, shapes, builds, tools_kb, blockers, product_specs, reference_builds, forge_queue, proposal_runs
- **saved connections:** Anthropic, Google Drive account, Gmail account
- **chain:** Cockpit Form → Make Run → Working Page → Respond Accepted → Read Job Row → Merge Context → Read Template → Read Lessons → Ground Match → Read Shapes (Cockpit) → Read Builds → Read Tools KB → Read Blockers → Route the job → Read Specs C → Match Product → Read Reference Builds → Match Reference → Pick the evidence to attach → Price the build → Prompt of Record → Generate → Parse Outputs → Voice Call → Voice Gate → Voice Merge → Audit → Render Sketch → Build Pack → Proposal Prompt → Prep Archive → Read Forge Queue → Generate Proposal → Archive Folder → Read Builds G → Shape Proposal → With Folder → Forge Gate → Post Proposal → Archive Sketch → Archive Pack → Fire Forge → Restore Pack → Store Row → Attach Reference Builds → Shot URLs → Fetch Shots → Build Evidence PDF → Write Run → Compose Email → Flip Job Status → Add Proposal Link → Mark Job → Add CC Link Email Backup → Attach Shots Binary → Email Backup

---

## Upwork: Job Engine

`7MY8Bqj42haaFbPF` · 26 nodes · ACTIVE

### trigger: Instant Poll

- **data tables:** upwork_jobs, ideas, builds, build_queue
- **saved connections:** Apify - Header Auth, Anthropic, Gmail account
- **chain:** Instant Poll → Instant Config → Fetch Jobs → Read Seen → Normalize → Chunk → Judge → Parse Judge → Insert Rows → A Filter → Read Jobs Shapes → Add CC Link Email A Fit → Read Ideas → Email A Fit → Read Proven Builds → Shape Scan → File Opportunity → Read Unfiled Gaps → Read Queue Week → Prep Enqueue → Enqueue to Build Queue → Mark Gap Enqueued

### trigger: Sweep Poll

- **data tables:** upwork_jobs, ideas, builds, build_queue
- **saved connections:** Apify - Header Auth, Anthropic, Gmail account
- **chain:** Sweep Poll → Sweep Config → Fetch Jobs → Read Seen → Normalize → Chunk → Judge → Parse Judge → Insert Rows → A Filter → Read Jobs Shapes → Add CC Link Email A Fit → Read Ideas → Email A Fit → Read Proven Builds → Shape Scan → File Opportunity → Read Unfiled Gaps → Read Queue Week → Prep Enqueue → Enqueue to Build Queue → Mark Gap Enqueued

### trigger: Net Poll

- **data tables:** upwork_jobs, ideas, builds, build_queue
- **saved connections:** Apify - Header Auth, Anthropic, Gmail account
- **chain:** Net Poll → Net Config → Fetch Jobs → Read Seen → Normalize → Chunk → Judge → Parse Judge → Insert Rows → A Filter → Read Jobs Shapes → Add CC Link Email A Fit → Read Ideas → Email A Fit → Read Proven Builds → Shape Scan → File Opportunity → Read Unfiled Gaps → Read Queue Week → Prep Enqueue → Enqueue to Build Queue → Mark Gap Enqueued

---

## Error Watch

`mb0BkCseIfoMUqT2` · 4 nodes · ACTIVE

### trigger: On Failure

- **saved connections:** Gmail account
- **chain:** On Failure → Format → Add CC Link Email Seth → Email Seth
