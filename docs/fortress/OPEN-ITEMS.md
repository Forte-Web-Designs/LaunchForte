# Open items — Aug 13, 2026

Read [`START-HERE.md`](./START-HERE.md) first. This is the live list, in the order I
would take them. Everything here is known, reproduced, and unfixed.

## Blocking a clean autonomous run

**1. SOLVED — the worktree collision.** Root cause: two runner daemons alive at
once, racing for the same card. A LaunchAgent at
`~/Library/LaunchAgents/com.launchforte.assembly-runner.plist` has supervised a
runner since Aug 4; every manual start added a second one. Nothing in `runner.py`
stopped a second process from starting, so a restart added a daemon instead of
replacing one.
The winner built, the loser died on the branch and path the winner had just taken
and mailed a failure for a card that was building fine. "a branch named ... already
exists", `'<path>' already exists`, "worktree landed on main", duplicate emails and
$0.00 failures were all the same one fault.
Seven patches went into the worktree block, two were reverted, none touched the
real fault.
Found by four measurements, not by reading: out-of-order timestamps in a stream
that flushes every write; a log line missing its first 110 characters with its tail
intact; `drain()` claims serially at `max_parallel` 1 so one process cannot claim
twice in one second; and n8n claim-call gaps that came in pairs summing to one 30s
poll, drifting from 10.1s apart to 0.1s apart over ten minutes. After the fix the
gaps are flat at about 32s.
Fix: `take_singleton_lock()` in `runner.py`, an `fcntl.flock` on `logs/runner.lock`,
taken before the queue exists, held for the poll loop and `--once` and `--dry-run`,
not for `--check` or `--selftest`. A second process exits naming the PID that holds
it. `flock` is released by the OS when the holder dies. `runner.py --selftest`
asserts a second holder is refused and a dead holder frees it.
Operating rule: launchd owns the runner, never start it by hand.
Second fix: `worktrees_dir` sits inside `~/assembly-line-runner`, which is itself a
git checkout on `main`, so `rev-parse --abbrev-ref HEAD` in a directory that is not
a worktree walks UP and answers `main`. That is the whole origin of "worktree
landed on main". The setup now checks `rev-parse --git-common-dir` against the
intended repo first, and preflight prints a note naming the enclosing repo at every
startup.

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
