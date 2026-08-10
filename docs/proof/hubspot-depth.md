# HubSpot Depth Test — Portal 51819426

Read-only navigation probe of the Launch Forte HubSpot portal, checking how far
the editor UI nests and whether every level can be exited cleanly. Nothing was
saved, typed, or changed. Screenshots below are editor chrome only — no list
views or record data were captured.

## Portal confirmed

- Opened `https://app.hubspot.com/`, landed on the Accounts Dashboard, which
  listed several accounts reachable from this login (this login can see more
  than one portal).
- Selected **Launch Forte**, account domain `www.launchforte.com`, portal ID
  **51819426**.
- Confirmed via the top-right profile menu ("Seth Forte / Launch Forte") and
  via every subsequent URL, all of which carried `51819426`. No navigation in
  this session left that portal ID.

## Path down

Entry point: Marketing Email (open on this plan) → the one existing item is a
draft named "SAMPLE - New Lead Welcome Email (draft, do not send)". Workflows
and Campaigns were not tested — the task noted they're locked on this plan.

1. **Level 1 — Email editor.** Opened the draft into its content editor.
   Chrome: top bar (Back/File/Help, title, Save/Preview/Review-and-send),
   a device toggle, a left rail of tool icons, a module palette, and the
   email canvas. The canvas and the module palette are each their own
   iframe nested inside the page.
2. **Level 2 — Inbox content panel.** Opened the settings panel that holds
   the email's header-level fields (a `#inbox-content` panel: Subject line,
   Preview text, From name, From address, plus a locked reply-to checkbox).
3. **Level 3 — Field-level popovers.** From that panel:
   - Subject line's emoji-picker icon opened a popover with its own search
     box and an emoji grid.
   - From name opened a categorized dropdown (one existing HubSpot-user
     option, a personalization-token option, three action links).
   - Clicking the body-text module in the canvas selected it and exposed a
     per-module toolbar (edit / hide / duplicate / delete).
4. **Level 4 — Module edit mode (deepest point reached).** Clicking the
   module's edit icon opened an "Edit Text" settings panel (Visibility
   toggle, Show/Hide radio group, Padding toggle with four populated
   spinbuttons: Top/Bottom/Left/Right) alongside a full rich-text toolbar
   inside the canvas iframe (paragraph style, font size, bold/italic/
   underline, text color, alignment, lists, link/emoji/special-character,
   Personalize).

No level beyond this was found reachable from Marketing Email without
creating new content.

## Fields entered

Three fields were clicked into; none were typed into or altered:

- **Subject line** — empty, required (red border, inline validation
  message). Clicking its emoji icon revealed a search-box-plus-grid popover.
- **From name** — a populated dropdown/combobox.
- **Padding (module edit panel)** — four populated number spinbuttons
  (unit: px), each with its own increment/decrement stepper.

All three released cleanly on Escape/close with values unchanged.

## Path up

Climbed back out one level at a time, in reverse order:

- Emoji popover → Escape → back to the inbox-content panel, subject line
  field unchanged. Clean.
- From-name dropdown → Escape → back to the inbox-content panel, value
  unchanged. Clean.
- Edit Text panel (level 4) → panel's own Close button → back to the canvas
  with the module still selected. Clean.
- Selected module → Escape → module deselected. Clean.
- Email editor (level 1) → the editor's own Back button → returned to the
  Marketing Email list. No Save/Cancel dialog appeared at any exit; nothing
  trapped navigation at any level.

One honest caveat: HubSpot's own UI showed a "Saving…" / "Autosaved"
indicator in the editor top bar merely from opening the module's edit panel
— this is the platform's autosave firing on entering edit mode, not a save
action taken here. No field value was changed (subject line was still empty,
body copy and padding numbers were unchanged on re-inspection), but the
draft's own "last updated" timestamp did advance as a side effect. This
appears to be inherent HubSpot editor behavior, not something avoidable
short of never opening a module's settings panel.

## Rung per level

| Level | What | Rung | Fallback |
|---|---|---|---|
| 0 → 1 | List row → email editor | Plain locator (link click) | — |
| 1 → 2 | Editor → inbox-content panel | Plain locator (click a settings-summary block) | — |
| 2 → 3a | Subject line → emoji popover | Plain locator (icon button) | — |
| 2 → 3b | From name → dropdown | Plain locator (combobox button) | — |
| 1 → 3c | Canvas → module selected | Frame locator, then screenshot + coordinate | A `click-catcher` overlay div inside the canvas iframe intercepted pointer events on the accessibility-tree-resolved element (both the text node and its module wrapper timed out with "element intercepts pointer events"). Fell back to a coordinate click read off a screenshot of the same iframe region, which worked. |
| 3c → 4 | Module toolbar → Edit Text panel | Screenshot + coordinate (the edit-pencil icon in the module's floating toolbar had no clean accessible name to target by locator) | — |
| 4 → 3c | Close Edit Text panel | Plain locator (panel Close button) | — |
| 3c → 1 | Deselect module | Plain locator (Escape key) | — |
| 1 → 0 | Editor → list | Plain locator (editor's Back button) | — |

## Result

Deepest point reached: module edit mode inside the email canvas iframe
(Level 4 — a settings panel plus a rich-text toolbar, both nested inside the
canvas iframe which is itself nested inside the editor page). Every level
released cleanly back to the Marketing Email list with no dialog, no stuck
state, and no unintended save. The one rung that needed a fallback was
inside the canvas iframe, where a click-catcher overlay blocked direct
element targeting and a coordinate click on a screenshot was used instead.
