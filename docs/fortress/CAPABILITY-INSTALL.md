# Fortress Capability Install: the checklist

**Against `fortress_capability_install_runbook.md` (Aug 8). Status as of Aug 9, 2026.**

This runbook installs software on the Fortress Mac mini and drives a Chrome
profile that holds live client sessions. Neither of those is something this
session can do from the cloud: the shell here runs in an isolated container, and
the device bridge reaches two connected folders (`repos/launchforte`,
`Downloads`) — it is not a terminal on the Mac. So what follows is the checklist
in the order it has to run, with everything already determined filled in.

---

## 0. What the device already tells us

The Mac mini's home directory contains **`.playwright-mcp/`** and **`pw-test/`**.

That is strong evidence Playwright MCP is already installed and has been run at
least once. Runbook §1.1 is explicit: *"Check first. If a Playwright MCP server
is already registered on the Fortress Mac mini and answers, skip to section 2. Do
not reinstall over a working one."*

**So section 1 is a confirmation, not an install.** Do not npx anything until the
check below comes back empty.

---

## 1. Confirm, do not install

Run on the Mac mini:

```bash
node --version
ls -la ~/.playwright-mcp ~/pw-test
npx @playwright/mcp@latest --version
grep -rn "playwright" ~/.claude.json ~/Library/Application\ Support/Claude/*.json 2>/dev/null | head
```

**If a server is registered and answers:** report the version and which Chrome
profile it is bound to, then go to section 2. Nothing else in section 1 applies.

**If it is absent**, register it against Fortress's OWN Chrome profile — the one
holding the estate's logged-in sessions. Extension mode reuses those sessions; it
is the sign-in doctrine continued, not a new credential surface.

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--extension",
               "--caps=network,storage,testing,vision,pdf,devtools"]
    }
  }
}
```

Then install the companion Chrome extension into that same profile.

**Report back:** installed or already-present · version · bound profile.

---

## 2. The four reach verifications

This is the whole point of the install. The walls that stopped the Margaret build
were the old tool's blindness, and Playwright is only worth trusting once it
demonstrably clears them. Capture **trace + screenshot** for each.

| # | Verification | Pass condition | Wall class it replays |
|---|---|---|---|
| 1 | **Iframe entry** — open a HubSpot workflow editor, enter the embedded frame via `frameLocator`, read a node's real state | real state read, **zero coordinate guessing** | the Margaret coordinate-bug day |
| 2 | **Stubborn control** — open a Salesforge step editor, write a subject line through the real input, read it back | written and verified by read-back | the off-screen-dialog class |
| 3 | **React input** — set a value on a React-controlled field in the estate's stack | the app registers it, via **real keyboard events**, not a raw value assignment | silent value-assignment failures |
| 4 | **Network route** — read the real API call underneath one stubborn UI action | rung 5 proven available, not theoretical | the whole ladder's escape hatch |

**A fail here is a finding, not a formality.** It means that surface class is not
certifiable and stays ladder-only until it passes. Record each result in
`blockers` — see section 3, which is where this runbook and the triage runbook
meet.

---

## 3. Rung-logging: the gap that matters most

Every session attempts in this order, stops at first success, and **logs which
rung won**:

```
API/MCP → CLI → Playwright locator → Playwright frameLocator → network/storage
→ Playwright vision (screenshot+coordinate) → OS accessibility (Phase 3)
→ pixel desktop control (Phase 3) → staged assist to Seth
```

**Rung-logging is NOT active today, and the ledger proves it.** The `blockers`
table has 14 rows and every single `kind` is `api_key`, `shell`, `reconnect`,
`quota`, `question`, `fix` or `scope`. Not one row records a UI surface, a wall
class, or a winning rung. The Margaret walls named in both runbooks — the
coordinate-bug day, the extension dropping the tab three times on the enrollment
build, the sequences inbox wall — **are not filed anywhere.**

This is not cosmetic. Triage check 3 ("the known-walls ledger shows zero open
walls for those surfaces") currently passes *vacuously* on every HubSpot-class
posting, because the ledger it reads has never had a wall written to it. A gate
reporting green off an empty ledger is worse than one reporting red.

**Before the volume lane can ever mean anything, `blockers` needs:**

- the three Margaret walls filed, with `kind` naming the surface class rather
  than the credential class (`ui_iframe`, `ui_offscreen_dialog`, `platform_inbox`)
- a `rung` recorded on each: which rung was tried, which one won, which one never
  got there
- the two Phase 1 acceptance replays (§2 rows 1 and 2) filed as the closing
  condition on the first two

Existing columns cover this without a new table: `kind` takes the surface class,
`how_to` takes the winning rung and the path, `last_error` takes what the losing
rungs did, `status` flips to `done` when the replay passes. **No new tables** —
same discipline as the triage build.

---

## 4. Escalation tools: triggers, not a shopping list

Budget is open. The discipline is that each tool has a **felt trigger**, so money
buys capability the estate reaches for rather than shelf-ware.

| Tool | Status | Trigger |
|---|---|---|
| **Playwright MCP** | free · likely already installed | none needed — this *is* the unlock |
| **Apify** | already owned, running the Upwork ingest | reach for it FIRST on any hostile scrape |
| **Browserbase + Stagehand** | purchase-approved, unbought | a scrape-class target that blocks the local browser, **or** genuinely parallel browser work across several client sites. Buy the fitting tier when a real shape needs it and report the dated price |
| **CAPTCHA solving (2Captcha class)** | permitted, narrowly | non-client, non-login, scrape-path only |
| **Agent SDK** | phased | programmatic hooks needed mid-job |
| **Cua (desktop control)** | phased | a recurring native-app need |

**The one rule open budget does not relax:** CAPTCHA and evasion tooling is
**never** pointed at a client's account login. A flagged client account is the one
outcome worse than losing a cheap job. This is a safety rule, not a budget rule.

**Standing instruction, now in force:** when Fortress hits a wall it cannot clear
and a purchasable tool would genuinely clear it (and it is not a client-account
login case), the wall arrives as a **named purchase request** — the tool, its
dated price, and what it unlocks — rather than as a silent failure. Reach gaps get
closed by naming them.

---

## 5. The honest bound

No tool, at any price, guarantees access to every surface. Hard passkeys,
bank-grade device attestation and novel anti-bot challenges on authenticated
client accounts defeat every agent and every stealth vendor, because the arms race
has no permanent winner.

For those, the staged two-minute assist is the answer and always will be. The
certification gate's job is to keep them off the cheap-work list entirely — which,
today, it does by failing closed on everything.

"Fortress can solve any task" is true for the vast majority and deliberately **not
promised** for the residual. The residual is handled by pricing — ladder or no bid
— never by a purchase. Buying more tooling raises the majority; it never
eliminates the residual. A surface that needs a human passkey tap is a correct
staged assist, not a failure to fix with money.

---

## 6. Acceptance, tracked

- [ ] **1.** Playwright MCP present (confirmed or installed), version and bound profile reported
- [ ] **2.** All four reach verifications run, each pass/fail with trace + screenshot
- [ ] **3.** Rung-logging active in `blockers` — *currently NOT active; see §3*
- [ ] **4.** Escalation triggers understood, naming instruction in place — **done, §4**
- [ ] **5.** The freshness rehearsal (triage check 6) can run against real certified paths — *blocked on 1 and 2*

Item 5 is the join between the two runbooks. Triage check 6 fails on 6,800 of
6,800 postings today because `tools_kb.session_last_verified` is empty on all 177
rows. Nothing can be rehearsed until the tool that walks the paths is confirmed
working — which is item 1, which is very likely already done and just needs
someone to look.
