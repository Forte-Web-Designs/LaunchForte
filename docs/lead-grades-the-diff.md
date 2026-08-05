# Lead grades the diff

The reviewing agent (the "lead") no longer takes a worker's word for what it did.

Instead, it pulls the actual commit diff from GitHub for the branch under
review and reads the real code changes that landed.

Each acceptance criterion is then graded against that diff, not against the
worker's own summary or description of its work. If a criterion claims
something happened but the diff does not show evidence of it, the lead treats
that criterion as failed — the benefit of the doubt goes to the code, not the
claim.

This closes the gap where a worker could describe work it didn't actually do,
or forget to commit part of what it described, and still pass review.
