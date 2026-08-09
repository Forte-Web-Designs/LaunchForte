# Hardening protocol: three amendments

**Aug 9, 2026. Amends `fortress_hardening_runbook.md`.**

## 1. Phase 0 closes on the UI sign-off alone

Console image paste and the trial client pack seed **move into Phase 1** as things
the run exercises, not gates in front of it.

The reasoning, worth keeping because it generalises: both are features Phase 1
would drive anyway. Pre-proving them delays the run that would prove them
properly, and if the image paste breaks mid-run that IS a Phase 1 finding, logged,
which is the entire point of a hardening run. Clearing two more gates before
starting repeats the exact failure the run exists to correct — building without
validating.

**Phase 0 exit is now:** Seth opens `/command/`, and says yes or no.

## 2. Phase 2 gains mid-build redirection

The runbook tests intake questions, one rejected card, and a scope addition. All
three are *clean sequential* events. None of them is the thing Seth actually does,
which is change his mind while work is in flight.

**Added to Phase 2.** Seth interrupts the build three ways:

1. **Redirect a card mid-flight** — "do it this way instead" while it is being worked
2. **Kill a card** that stopped making sense
3. **Reorder priority** while work is in progress

The system must absorb all three:

- **without a re-intake** — no starting over to change one thing
- **without losing completed work on adjacent cards** — a redirect is not a reset
- **without silently continuing the original instruction** — the failure mode that
  looks like everything is fine until the wrong thing is delivered

**Measure:** Seth-minutes per redirection, and whether any in-flight session had
to be killed to absorb it.

Why this earns a slot: a system that only handles clean forward progress feels
rigid the first real week, and rigidity is not a bug anyone files. It just makes
the tool quietly not get used.

## 3. Phase 1 drives the console the way it will really be used

Seth pastes a **screenshot** rather than typing, so the image path is exercised
under real conditions rather than in a synthetic test. Same principle as
amendment 1: the honest test of a feature is a person using it for its purpose.

---

## What this leaves

**Phase 0:** UI sign-off. Nothing else.
**Phase 1:** intake, with a screenshot paste and the pack seed exercised in passing.
**Phase 2:** the build, plus three deliberate redirections.
**Phases 3–5:** unchanged.

**Selected job:** Candidate B, the AI Client Intake Workflow — uid
`2082023975899034093`, shape `data-collection`, ~8 cards, derived $5,800.
Chosen because a proven kit only certifies the shape it builds, and the Intake
System is one of the 24 catalog patterns. A kit for a shape that never appears in
a quote is a demo.

**Before Phase 3:** doorbell button auth, designed in `DOORBELL-AUTH.md`, built
then, not now.
