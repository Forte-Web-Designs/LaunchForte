# Never depend on an MCP connector

**Standing rule. Applies to every card, every engagement, no exceptions.**

Seth, 13 Aug 2026:

> "most clients arent going to want to give us MCP access why cant we just get around that"
> "we shouldnt rely on mcp ever since clients probably wont give us that"

## The rule

A card reaches a client system by **driving the browser** — opening the app in a signed-in
profile and clicking, the way a person does. That is the supported route and the only one a
card may plan around.

An MCP connector is a **convenience, never a prerequisite**. If one is available, use it and
go faster. If it is absent, open the browser. A card must never:

- stop and wait for a connector to be authorised
- report `SETUP NEEDED` because a connector is missing
- treat missing MCP auth as a blocker of any kind

## Why

A client hands a consultant **a seat in their system** — the same thing they give a
contractor or a new hire. That is a five-minute admin action they already understand.

What a client will **not** do is approve a third-party OAuth application, route it through a
security review, and grant it API scope over their CRM. If Fortress required that, the deal
dies at procurement — before anyone has seen the work.

So the browser route is not the fallback. It is the product. The connector is the shortcut.

## What it cost to learn

`adops-4`, 13 Aug 2026. The card stopped at **$0.13** without opening a single page and
reported:

> SETUP NEEDED: HubSpot MCP connector — Seth needs to authorize the claude.ai HubSpot
> connector before this card can run

It was wrong, and provably so. Every other HubSpot card in the same engagement reached the
portal through the browser and finished:

| card | route | result |
|---|---|---|
| `adops-1` | noted MCP unavailable, drove the browser anyway | done — portal id confirmed, 9 objects mapped |
| `adops-2` | browser | 8 ad products created |
| `adops-2b` | browser | done — *"no HubSpot MCP auth was needed since I navigated the UI directly"* |
| `adops-3` | browser | done — pipeline settings read and photographed |
| `adops-4` | **asked for MCP and stopped** | $0.13, nothing attempted |

A card that stalls waiting for a connector is a card that could never have run on a real
client engagement.

## For card authors

Every card that touches a client system carries this block:

```
DRIVE THE BROWSER. NEVER WAIT ON A CONNECTOR.
You reach the system by driving it in the signed-in browser profile, the same way a person
does. Do NOT treat an MCP connector as a prerequisite. Do not stop and ask for it to be
authorised, and never report SETUP NEEDED because a connector is missing. If an MCP tool
happens to be available it is a convenience, nothing more.
```

## For the checker

A missing connector is never grounds to fail a criterion, and never grounds to pass one
either. If a card reports `SETUP NEEDED` for a connector, that is a fault **in the card**,
not a blocker for Seth to clear.
