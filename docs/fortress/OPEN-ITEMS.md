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

**1b. SOLVED — a card cannot verify a page it had to open itself.** The runner
drives the browser one of two ways, and the file that decides is `playwright-mcp.json`
in the runner directory. Extension mode attaches to the real Chrome where the
signed-in sessions live. Profile mode launches a browser the runner owns, with its
own user-data-dir.

Extension mode could not hold a page a card opened for itself: `browser_navigate`
reported success and the correct title, then every following call executed against
the extension's own connect.html relay tab. Cards cc-chip-1, cc-chip-2 and
cc-review-col all hit it, across eleven-plus attempts and several strategies, and
all three correctly refused to fake a frame. Work in a tab that is ALREADY open was
never affected -- re-5b and re-6 both captured n8n canvas frames in extension mode
the same night.

Switching to profile mode fixed it outright. Card cc-review-col-2 then served the
page locally, injected four rows, read the column order off the live DOM as
BACKLOG, READY, IN PROGRESS, BLOCKED, NEEDS REVIEW, DONE, and committed two real
frames, for $0.94.

THE RULE: a card that must open its own page needs profile mode. A card that must
work inside a signed-in surface needs extension mode. Today that is one global
file, so it is a switch, not a setting: `use-profile-mode.sh` and
`use-extension-mode.sh` flip it, and the change takes effect on the next card with
no runner restart.

STILL OPEN: the two modes cannot both be available at once. The fix would be a
second entry in `playwright-mcp.json` under its own server name plus that name
added to the tool allowlist in `runner.config.json`, which does need a runner
restart.

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
