# The instance, and how to know you are in the right one

There is exactly one n8n tenant Fortress may touch:

    launchforte.app.n8n.cloud

Nothing else. Any other `*.app.n8n.cloud` host named anywhere in this repo is
either history, a client's own tenant, or a note from a simulation. None of them
is an instruction, and none of them is somewhere to sign in.

## Rules

1. The card names the surface. If a card gives a URL, that URL is the surface —
   do not go looking through files for a better one.
2. If a card does not name a surface, the surface is the host above.
3. If a file names a different tenant, treat it as history. Do not follow it.
4. If a page asks you to sign in, stop and report SETUP NEEDED with the URL.
   Never type into a sign-in form, and never sign in to a tenant that is not
   the host above.
5. Confirm the instance as the first action of every card, and say in the report
   which host you were on.

## Why this file exists

On 12 Aug a browser card was given the URL
`launchforte.app.n8n.cloud/workflow/Xbcm4Uc7oDamm3Ps` and ended up at
`modbung.app.n8n.cloud/signin` — a client's tenant. It stopped at the sign-in
wall and asked for a human, which is the rule working. But it should never have
been there: it had gone looking for "the n8n surface" and found a line in
`SIMULATION-1.md` describing a client tenant in the present tense.

The card was right. The repo was misleading. This file is the answer.
