# Handoff Protocol: Claude Code ↔ Fortress

This note describes how a task passes between Claude Code and Fortress.

## Scope of access

Fortress can only read and write files that live inside this repository. It
has no visibility into, and no way to reach, anything else on the host
machine. Any instruction that depends on state outside the repo cannot be
fulfilled.

## Instructions must name exact paths

Every job handed to Fortress must include the exact file path(s) it needs to
touch. Fortress does not go hunting through the repo to guess intent —
open-ended instructions like "find the pricing component and update it" are
where jobs stall or fail. Name the file. If a new file is needed, name the
path it should be created at.

## Grading is automatic

Acceptance criteria are now derived directly from the instruction text
itself, so there is no separate step where a human writes a rubric — every
job is graded against what the instruction actually asked for. This means
the instruction doubles as the spec: vague instructions produce vague
grading, and precise instructions produce precise grading.

## Blockers must be reported, not swallowed

If a job cannot be completed as instructed — a missing dependency, an
ambiguous path, a conflict with existing content — Fortress must say so
explicitly and describe the blocker. Finishing "quietly" by skipping the
hard part, guessing, or doing something adjacent to the ask is treated as a
failure, not a success.
