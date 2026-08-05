# Evidence-Based Review

Acceptance criteria for each task are written by the AI, derived directly
from the job instruction — not from the worker's own account of what it did.

The reviewing agent grades those criteria against the real commit diff, not
against the worker's summary or self-report. If the diff does not show the
change, the criterion fails, regardless of what the worker claims.

This keeps review evidence-based: the source of truth is the code that
actually changed, not a description of it.
