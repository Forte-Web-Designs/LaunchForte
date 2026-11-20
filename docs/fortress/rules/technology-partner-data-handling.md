# technology-partner-data-handling

Seth, Nov 20 2026 3:55 PM CT. These seven lines are the only data handling statements used anywhere. The website says "we". Client pages and the demo say "I". No claim of security monitoring, threat detection, protection or guarantees, and no mention of AI.

## The lines
1. Read only access wherever possible. Changes only happen when you ask for them.
2. Access keys are kept in a secure vault, never sent by email or kept in notes.
3. Your data is kept separate from every other client's.
4. Documents are stored privately and only open for the people you approve.
5. Every update is reviewed by a person before it reaches you.
6. You can see which tools are connected and remove access anytime.
7. Everything stays in your name. If you leave, we remove our access and you keep everything.

## Verification (Nov 20 2026)
A line ships on client pages, the demo or the website only once it is marked VERIFIED here.

| Line | Status | What was checked |
|---|---|---|
| 1 Read only | VERIFIED | Client access used for checks is read only (ex: the Haas n8n credential is read only, Airtable structure is read, not written). Client systems are changed only on a request. |
| 2 Keys in a vault | NOT YET | n8n credentials are vaulted, but the current rule still allows keys in a client doc's KEPT BY HAND section, which is a note. True once keys live only in the vault. |
| 3 Separate data | VERIFIED | Row level security is on for every lf_tp table. Pages read through a per client token that only returns that client's rows. |
| 4 Private documents | VERIFIED | The tp-documents bucket is private. Files open only through a signed in client page session for that client. |
| 5 Reviewed by a person | NOT YET | Pages stay internal until Seth clicks, but the independent page reviewer that checks every item is not built yet. True once it gates every item. |
| 6 See and remove access | NOT YET | Your systems shows what is connected. There is no remove access control on the page yet, so the "anytime" half is not true in the product. |
| 7 Stays in your name | NOT YET | Builds live in client owned accounts by practice, but there is no recorded offboarding step that removes access. True once offboarding is a recorded step. |
