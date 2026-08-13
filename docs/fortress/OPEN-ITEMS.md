# Open items — Aug 13, 2026

Read [`START-HERE.md`](./START-HERE.md) first. This is the live list, in the order I
would take them. Everything here is known, reproduced, and unfixed.

## Blocking a clean autonomous run

**1. The worktree collision.** Every card's FIRST attempt can fail at setup with
"a branch named ... already exists", at $0.00, before any work. The retry then
succeeds, so no work is lost — but Seth gets a red failure email per card, and an
operator who learns to ignore alerts is the real damage.
Cause: `git worktree add -b` CREATES the branch and then fails for a reason git does
not report (stderr is empty apart from "Preparing worktree"). The retry trips over the
branch its own predecessor made.
Tried and reverted: `-B` instead of `-b`. It removed the collision and introduced a
worse failure — two cards died with "worktree landed on protected branch main", caught
by the guard that refuses to build on main. Not worth it. Reverted to `-b`.
Next idea, untried: give each attempt a unique branch suffix so collision is impossible
by construction, rather than racing git's ref handling.

**1a. The worktree setup is the blocker, and it needs a rewrite not another patch.**
Symptoms seen on Aug 13, all at $0.00 before any work: "a branch named ... already
exists", and "worktree landed on protected branch main" (the guard doing its job).
Four changes were made to this code in one night -- a cleanup pass, an ordering fix,
a switch to `-B`, and a revert of that switch because it produced the protected-branch
failure. The reverted code is what is running now and it still fails.

Do NOT patch it again in place. The design that removes the whole class:
**give every attempt its own branch name** -- `runner/<job_id>-<short-slug>-<attempt>`
-- so a collision is impossible by construction and no fallback path can ever end up
checking out base. Write it fresh, with `runner.py --selftest` extended to cover:
a clean create, a create when the branch already exists, a create when a stale
worktree directory is present, and an assertion that HEAD is never `main` afterwards.

**1b. A card cannot verify a page it had to open itself.** The runner drives the
browser through the Playwright MCP in `--extension` mode (see `playwright-mcp.json`
in the runner directory), which attaches to the real Chrome the signed-in sessions
live in. In that mode `browser_navigate` and `browser_evaluate` operate on two
different underlying sessions. Navigate reports success and the correct page title,
then the very next call executes against the extension's own connect.html relay tab.
Observed by two independent cards on Aug 13, cc-chip-1 and cc-chip-2, across eleven
attempts between them, with three distinct strategies: new tab, current tab, and
closing the relay tab first. Representative evidence: `browser_navigate` returned
"Page URL http://127.0.0.1:8934/command/index.html, Page Title: Command" and
`browser_evaluate` of `location.href` immediately after returned a
`chrome-extension://.../connect.html` URL. Work on a page that is ALREADY open is
unaffected -- cards re-5b and re-6 both screenshotted the n8n canvas the same night
without trouble, because the tab was already there and signed in. So the limit is
specific: a card can prove work in a surface that is already open, and cannot prove
work in a page it had to open for itself. Any card whose evidence depends on loading
a local build, a preview server or a fresh URL will stall at the proof step after
doing the work correctly. Both cards refused to substitute a code-level check for a
browser and call it browser-verified. That is the behaviour we want and should not be
tuned out. Untried options, in the order worth trying: switch that one card to the
profile mode script that ships beside the extension one, which drives its own Chrome
and its own tabs but does not carry the signed-in sessions; or have the card assert
against the served HTML through a real DOM implementation and label the evidence as
what it is, never as a browser screenshot. Do not add a rule that lets a card claim
browser verification it did not perform.

## Silent failures that look like facts

**2. The Command Center renders an empty board on a 401.** The page holds a dashboard
token per browser in localStorage. If it does not match `__DASHBOARD_TOKEN__` in
`Ops: Dashboard API` -> "Code in JavaScript", the snapshot returns 401 and the board
draws itself empty, with no message. Verified Aug 13: the API returns 259 tasks with
the right token and `__unauth` without it. The board must say "unauthorized, re-enter
your token" instead of showing a convincing empty board.

**3. `build-enqueue` silently drops an oversized prompt.** A ~3.7k prompt returns
200 OK with an empty body and creates no row. It looks exactly like success. Either
raise the limit or return an error the caller can see.

## Product

**4. The Demand section has no "last refreshed" date.** The corpus is rebuilt roughly
monthly, so a reader cannot tell whether they are looking at this week or last quarter.
Add the refresh timestamp to the snapshot payload and render it under the Demand
heading. Requested by Seth, Aug 13.

**5. A rejection should not be able to cite housekeeping.** Fixed in draft `6f800d7b`
(the Lead reviewer may only FAIL by quoting a stated criterion, and gets a third verdict
UNVERIFIED for missing evidence) — confirm it holds over a few real cards.

**6. No client-facing message on an unfunded engagement.** Also in `6f800d7b`. The
reviewer drafted an apology to send a client, about an internal formatting rule, on a
simulated engagement with no client. Confirm it stays silent now.

## Standing

**7. Run `python3 runner.py --selftest` before any rehearsal and before any client
work.** It spawns nothing and spends nothing. `--check` proves the runner can start;
`--selftest` proves it reports itself honestly.

**8. The bar for client-ready is not "it worked".** It is a full rehearsal in which no
card produces a false failure email. As of Aug 13 individual cards run clean end to end
— `triage-5b` built, cropped, committed, pushed and passed an independent check with no
error — but a multi-card run still produces noise. That is the gap.
