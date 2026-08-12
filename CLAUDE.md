# LaunchForte — Project Configuration for Claude Code

## Fortress — read this before doing anything

This repo is not only the website. It is also the working memory of **Fortress**,
the build system that runs Launch Forte.

**If this session is Fortress work — a build card, a client project, a proposal, an
n8n change, anything that is not a plain site edit — stop and read
[`docs/fortress/START-HERE.md`](docs/fortress/START-HERE.md) first.** It carries the
stack, the card loop, the proven recipes and the standing constraints, and it is the
only Fortress document kept current. Files in `docs/fortress/` with a date in the
title are history, not instruction.

A new client project starts from a handoff paste, not from a conversation here:
[`docs/fortress/CLIENT-HANDOFF-TEMPLATE.md`](docs/fortress/CLIENT-HANDOFF-TEMPLATE.md).

Three constraints that apply to every session in this repo, without exception:
never drive upwork.com with browser automation; nothing is ever published, activated
or sent live; sample data only, never a real client record.


## Project Overview
LaunchForte is a web design and automation agency site. Static HTML/CSS/JS deployed on Netlify.

## Tech Stack
- **Frontend:** Vanilla HTML, CSS (custom properties), vanilla JavaScript
- **Styling:** Custom CSS with CSS custom properties (NO Tailwind, NO frameworks)
- **Deployment:** Netlify (static hosting via `netlify.toml`)
- **Analytics:** Google Tag Manager (GTM-TT7NJCP7)
- **No build step** — files in `/site/` are served directly

## Key Directories
- `/site/` — All public-facing HTML pages, JS, and assets
- `/site/images/` — All image assets
- `/site/posts/` — Blog/article pages
- `/site/video-walkthroughs/` — Video content pages
- `.claude/` — Claude Code settings

## Site Pages
- `index.html` — Homepage (services overview, reviews, credibility)
- `foundation.html` — Foundation tier service page
- `launch.html` — Launch tier service page
- `growth.html` — Growth tier service page
- `scale.html` — Scale tier service page
- `services.html` — Services overview
- `work.html` — Portfolio/case studies
- `reviews.html` — Client testimonials
- `about.html` — About page
- `contact.html` — Contact page
- `writing.html` — Blog listing

## Design System — CSS Custom Properties
All colors and design tokens are defined as CSS custom properties. The site uses
an Apple-style palette with **light as the default theme** (`:root`), and a dark
override under `[data-theme="dark"]`.

```css
/* Light theme — default */
:root {
  --text-primary: #1d1d1f;
  --text-secondary: #515154;
  --text-muted: #86868b;
  --accent: #0088DB;
  --accent-warm: #4ab5ed;
  --accent-hover: #4ab5ed;
  --accent-tint: rgba(0,136,219,0.10);
  --background: #f5f5f7;
  --background-alt: #ffffff;
  --card-bg: #ffffff;
  --background-dark: #1d1d1f;
  --border: rgba(0,0,0,0.08);
  --border-strong: rgba(0,0,0,0.12);
  --on-accent: #ffffff;
}

/* Dark theme */
[data-theme="dark"] {
  --text-primary: #f5f5f7;
  --text-secondary: #a1a1a6;
  --text-muted: #86868b;
  --accent: #4ab5ed;
  --accent-hover: #0088DB;
  --accent-warm: #0088DB;
  --accent-tint: rgba(74,181,237,0.14);
  --background: #1d1d1f;
  --background-alt: #000000;
  --card-bg: #2a2a2c;
  --background-dark: #000000;
  --border: rgba(255,255,255,0.10);
  --border-strong: rgba(255,255,255,0.16);
  --on-accent: #0b0b0c;
}
```

Note: the blue flips between modes — `#0088DB` is the primary accent in light and
moves to hover in dark, where the lighter `#4ab5ed` becomes primary for contrast.
`--on-accent` is the text color for content sitting on an `--accent` fill.

## Typography
- **Font stack:** -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- **Base size:** 17px
- **Line height:** 1.7
- **Headings:** Use `letter-spacing: -0.02em` for large headings
- **Section titles:** 0.8rem, uppercase, letter-spacing 0.1em, `--text-muted` color

## Component Patterns

### Cards
- Background: `var(--card-bg)`
- Border: `1px solid var(--border)`
- Border radius: `10px`
- Padding: `1.5rem` to `1.75rem`

### Buttons
- **Primary:** `background: var(--accent)`, white text, `border-radius: 6px`, hover lifts with `translateY(-2px)` and blue box-shadow
- **Secondary:** `border: 1px solid var(--border)`, muted text, hover changes border/text to accent color

### Animations
- `fadeInUp` — opacity 0→1, translateY 20px→0
- `fadeIn` — opacity 0→1
- `gradientShift` — animated gradient backgrounds
- `.reveal` class with `.revealed` for scroll-triggered animations
- Delay classes: `.animate-delay-1` (0.1s), `.animate-delay-2` (0.2s), `.animate-delay-3` (0.3s)

### Layout
- **Max width:** `1000px` for header, `860px` for main content
- **Padding:** `2rem` horizontal desktop, `1.25rem` mobile
- **Section spacing:** `4rem` between sections (via `section-divider`)

## Responsive Breakpoints
- **Desktop:** Default styles
- **Tablet/mobile:** `@media (max-width: 768px)` — single column grids, reduced padding
- **Small mobile:** `@media (max-width: 600px)` — further size adjustments
- **Smallest:** `@media (max-width: 480px)` — single column footer

## Coding Conventions
1. **All styles are inline in `<style>` tags** within each HTML file — no external CSS files
2. **No build tools or preprocessors** — write production-ready CSS directly
3. **Use CSS custom properties** (`var(--accent)`, etc.) for all colors — never hardcode hex values
4. **Mobile-first is NOT used** — desktop-first with `max-width` media queries
5. **JavaScript files** are separate: `hamburger.js`, `scroll-reveal.js`, `scroll-top.js`, `theme-toggle.js`
6. **Keep it minimal** — no unnecessary libraries, frameworks, or dependencies
7. **Every page** includes the same header/nav and footer structure
8. **Accessibility:** Use semantic HTML, proper heading hierarchy (h1→h2→h3), descriptive link text

## Dark/Light Theme
- Default is light theme (`data-theme="light"` on the `<html>` element)
- Dark theme via `[data-theme="dark"]` attribute on the HTML element
- Theme toggle handled by `theme-toggle.js`
- Logo inverts in dark mode via `filter: brightness(0) invert(1)`

## Important Notes
- Do NOT introduce Tailwind CSS, React, or any framework
- Do NOT create external CSS files — styles go in `<style>` within each page
- Do NOT add npm/package.json — this is a zero-dependency static site
- Match the existing dark, professional aesthetic in all new components
- When creating new pages, copy the header/footer structure from an existing page
- Always use `var()` references to CSS custom properties for theming support
