# Doorbell button auth: the design, before building

**Flagged before Phase 3 rather than discovered inside it.**

## The problem

Phase 3 requires accept and request-changes to work from a phone mail client. A
link in an email cannot send a header, so the `X-Dashboard-Token` mechanism the
dashboard now uses cannot reach these buttons. And the fallback that suggests
itself — an unauthenticated endpoint that trusts a card id — is not a fallback,
it is the same hole in a new place.

## The design

A **signed, single-use, single-purpose URL**. The token is not a secret to be
kept; it is a statement the server can verify it made, and can only be redeemed
once.

```
https://launchforte.app.n8n.cloud/webhook/doorbell
  ?c=<card_id>
  &a=<accept|changes>
  &e=<expiry unix>
  &s=<signature>
```

**The signature** is `HMAC-SHA256(secret, c + '|' + a + '|' + e)`, base64url, where
`secret` is a constant in the doorbell workflow — a sibling of
`__DASHBOARD_TOKEN__`, never in the repo. Verified by recomputation, compared
without short-circuiting, exactly as the dashboard guard does.

Four properties, each earning its place:

1. **Scoped to one card and one action.** The signature covers both, so an accept
   link cannot be edited into a request-changes link, and a link for card 12
   cannot be pointed at card 13. Tampering changes the input, so the signature
   stops matching.
2. **Short-lived.** `e` is inside the signature. Seven days suits a doorbell that
   fires when a phase completes; expired links explain themselves rather than
   failing blank.
3. **Single-use.** On redemption the workflow writes the signature to a `used`
   column on the card row and refuses a second presentation. Without this, a link
   sitting in an inbox forever is a standing credential.
4. **Stateless until redeemed.** Nothing is stored when the email is sent — only
   when a link is used. No table of outstanding tokens to grow or clean.

## What it deliberately does not do

- **No login.** The point is that Seth taps a button on a phone at a bus stop.
  Anything requiring a session defeats the doorbell.
- **No bearer of wider authority.** The token authorises one state change on one
  card. Even fully compromised it cannot read the roster, price anything, or
  touch another card.
- **No reuse of `__DASHBOARD_TOKEN__`.** Different blast radius, different
  lifetime, different transport. One secret doing two jobs is the mistake that
  put the dashboard token in a URL in the first place.

## The residual risk, stated

The URL is in an email, and email is not a secure channel. Anyone reading Seth's
inbox can accept a card. That is accepted deliberately: the blast radius is one
card transition on a simulated engagement, the alternative costs the phone
workflow the doorbell exists to provide, and anyone with his inbox has larger
options anyway.

What the design refuses is the *unbounded* version — a link that never expires,
works repeatedly, or can be edited into a different card.

## Confirmation, not just redemption

`request-changes` needs a note. The link opens a minimal page carrying the
signature in a form, posting note plus signature back. The GET does not mutate —
which also means a mail client prefetching links cannot accept a card by
accident. **Accept should be a POST from a confirmation page for the same
reason.** Scanners follow links; a one-tap GET that mutates state will eventually
be tapped by a machine.

## Build order, when Phase 3 arrives

1. Secret constant in the doorbell workflow, minted the way the dashboard token was
2. Signing helper in the email builder
3. Verify → check expiry → check `used` → mutate → mark `used`
4. Confirmation page for both actions, POST to mutate
5. Test the four failures explicitly, not just the happy path: expired, replayed,
   tampered card id, tampered action

Point 5 is the standard the dashboard guard was held to — unauthenticated, wrong
token and correct token were all checked. Only testing the happy path is how a
guard ships that never guarded anything.
