# The simulation loop — how Fortress gets proven, and stays proven

Read [`START-HERE.md`](./START-HERE.md) first.

This is the standard rehearsal. A real Upwork posting, built for real in Seth's own
environment, with sample data, for nobody. It is how a capability gets proven before a
paying client's name is ever on a card. It is also the honest test: a posting nobody
wrote for us asks for things we did not plan for.

Proven end to end on Aug 12 with posting `2083116803740842406`, "HubSpot CRM Expert and
Automation Setup" — see [`engagements/SIM-HS-1.md`](./engagements/SIM-HS-1.md).

---

## Step 0 — Seth signs in. Every time, before anything else.

The first move of every simulation is Seth opening whatever tool the posting needs and
signing in on the runner's Chrome profile. Not the runner. Not a card. Him.

Nothing downstream works without it and nothing downstream should try: a card that meets
a sign-in wall stops and says so, and never types a secret into a field. Ask up front,
so the answer arrives before a card is burning budget against a login screen.

## Step 1 — Take a real posting from the feed

Read it out of the `upwork_jobs` data table (`iSZB081VXkJjbZs5`). **Never drive
upwork.com with browser automation** — the account is the business.

Pick a posting that names tools we can actually reach, and quote its ask verbatim into
the cards. Their nouns, not ours. The value of the rehearsal is that the requirements
were not written to suit us.

## Step 2 — Open a simulated client and engagement

A `clients` row slugged `sim-<something>`, and an `engagements` row with `funded: false`,
whose `decision_ledger` says in plain words: simulated, real posting, nobody contacted,
sample data. Anyone reading these tables in six months must not mistake it for revenue.

## Step 3 — Cards, in this shape

Every tool-shaped deliverable is **three** cards, never one:

| Card | Job |
|---|---|
| build | make the thing |
| run | execute it against sample data and paste what came back |
| close-out | write `engagements/<ID>.md` and photograph the result |

The run card is not optional and it is not a formality. On Aug 12 a build card and its
check card both passed a workflow that would have held every lead in production. Running
it took four minutes and found two defects. Later the same day a HubSpot build reported
itself complete with three defects in it, all found by running. **Reading has never once
caught a defect on this project. Running has caught five.**

Every card: quote node names and saved-entry names so the refusal gates read them as
names; carry `client_slug` and `engagement_id` or it will not appear on the board; push
its own branch; end with an `EVIDENCE` block per [`EVIDENCE-STANDARD.md`](./EVIDENCE-STANDARD.md).

## Step 4 — Sample data, and nothing live

Invented people, `@example.com` addresses, a visible marker on anything written into a
real tool (`LF SAMPLE - <name>`) so every row a rehearsal created is obvious later.

Workflows stay `active: false`. Notifications go to Seth and nobody else, with the
recipient typed as a literal string — never built from the payload, never a fallback to
whatever address the sample lead carried. Nothing in the tool's own configuration is
created or edited: use the pipelines, stages and properties that already exist, and
report a missing one as a finding rather than making it.

Never delete anything. Archive.

## Step 5 — Close it out

The last card writes `docs/fortress/engagements/<ID>.md`: what was built, where it lives,
what was proven **by running it** with the real ids it returned, and what was left open.
Written for a stranger, because the next reader is one.

---

## What the rehearsal is actually testing

Not whether Fortress can build. It can — six for six on Aug 12, including a working
HubSpot integration proven by real records.

It is testing whether the **reporting** can be trusted without a human standing behind
it. That is where every failure has been: a truncated report, an empty commit sha, a
"tree is unchanged" line that was never true, gates refusing careful prompts, proof
frames stranded on unpushed branches.

Before the next rehearsal, and before any client work:

```bash
cd ~/assembly-line-runner && python3 runner.py --selftest
```

It spawns nothing and spends nothing, and every one of those bugs fails it in under a
second. `--check` proves the machine can start. `--selftest` proves it tells the truth.
