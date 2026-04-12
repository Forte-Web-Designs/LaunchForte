# Website Build & Redesign Instructions for Claude Code

Two prompts below. Copy the one that fits your situation and paste it into Claude Code in any new project terminal.

---

## PROMPT 1 — Create a new website from scratch

> Use this when starting a brand new project with no existing HTML files.

```
Build me a complete static website from scratch. No build tools, no npm, no frameworks — vanilla HTML, CSS, and JavaScript only. All styles go inline in <style> tags within each HTML page. Deploy on Netlify.

Before writing any HTML, create these two files:

### CLAUDE.md
Document the following so future Claude Code sessions stay consistent:
- Project overview (what the site is, what it does, who it's for)
- Tech stack: vanilla HTML/CSS/JS, no frameworks, no npm, deployed on Netlify
- Directory structure (put all pages and assets in /site/)
- List of all pages with one-line descriptions
- Full CSS custom properties design system (every variable)
- Typography rules (font, sizes, weights, line heights)
- Component patterns: cards, buttons, animations, layout widths
- Responsive breakpoints
- Coding conventions: inline <style> tags, desktop-first media queries, always use var() for colors
- Dark/light theme rules
- DO NOT rules: no Tailwind, no React, no external CSS files, no npm

### design_brief.md
Document the visual design system:
- Brand identity and tone
- Full color system: variable names, hex values, and usage
- Typography scale: hero, h1, h2, section labels, body, small, fine print
- Component CSS snippets: cards, buttons, section labels, dividers
- Layout rules: content widths, spacing scale, grid patterns
- Animation standards: scroll reveal, fade-in, hover interactions
- Responsive breakpoints table
- Page structure template (header → hero → sections → footer)
- Design principles

### Then build every page with this design system:

**Site details to fill in before pasting:**
- Site name: [SITE NAME]
- Brand color (accent): [HEX e.g. #0088DB]
- Pages to create: [LIST PAGES e.g. index, about, services, contact]
- Brief description of the business: [1-2 SENTENCES]

**CSS Custom Properties:**
```css
:root {
    --text-primary: #f0f4f8;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent: [YOUR BRAND COLOR];
    --accent-hover: [SLIGHTLY LIGHTER];
    --accent-warm: [SECONDARY ACCENT];
    --accent-glow: rgba(0,136,219,0.15);
    --background: #0a0e17;
    --background-alt: #111827;
    --border: #1e293b;
    --border-light: #2a3a50;
    --card-bg: rgba(17,24,39,0.7);
    --card-bg-solid: #111827;
    --card-hover: rgba(30,41,59,0.5);
    --gradient-start: [YOUR BRAND COLOR];
    --gradient-end: [YOUR SECONDARY ACCENT];
    --success: #10b981;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
}
```

**Font:** Inter via Google Fonts (weights 400, 500, 600, 700, 800)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

**Design patterns to apply on every page:**

1. **Glassmorphism header** — sticky, `backdrop-filter:blur(20px) saturate(1.2)`, semi-transparent background
2. **Nav links** — pill-style hover background `rgba(255,255,255,0.05)`, active state with accent tint
3. **Hero sections** — badge pill with pulsing dot, large headline `letter-spacing:-0.03em`, staggered fade-up animations, `clamp()` for fluid font sizing
4. **Section labels** — uppercase, 0.75rem, accent color, with `::before` 20px accent bar on the left
5. **Cards** — `backdrop-filter:blur(10px)`, `var(--card-bg)` background, border, hover `translateY(-2px)` + box-shadow
6. **Gradient buttons** — `background:linear-gradient(135deg, var(--accent), var(--accent-hover))`, `::after` shine overlay on hover
7. **Background atmosphere** — `body::before` fixed radial gradients for ambient glow
8. **Scroll reveal** — `.reveal` class starts at `opacity:0; transform:translateY(24px)`, transitions to visible via IntersectionObserver
9. **Smooth transitions** — `cubic-bezier(0.16,1,0.3,1)` for reveals, 0.2-0.3s for hover interactions
10. **Footer** — 3-column grid (services, company, connect links), collapses to single column on mobile
11. **Responsive** — desktop-first, breakpoints at 768px and 480px, single column on mobile

**Dark/light theme:**
- Default: dark theme
- Light: `[data-theme="light"]` attribute on `<html>` element overrides all CSS variables
- Theme toggle button in header
- Logo swaps between `.logo-img-dark` and `.logo-img-light`

**JavaScript files to create in /site/:**
- `scroll-reveal.js` — IntersectionObserver that adds `.revealed` class to `.reveal` elements
- `theme-toggle.js` — creates toggle button, manages localStorage, injects light theme CSS variable overrides
- `scroll-top.js` — scroll-to-top button that appears after 300px scroll
- `hamburger.js` — mobile hamburger menu that clones desktop nav links into a full-screen overlay

**Hard rules:**
- Every page: same header/nav and footer structure
- All styles: inline in `<style>` tags, never in external CSS files
- All colors: via `var()` — never hardcode hex in component styles
- All pages: include all 4 JS files at the bottom of `<body>`
- Mobile: single column, smaller padding, smaller font sizes
- Semantic HTML: proper heading hierarchy (h1→h2→h3), descriptive link text

Build all pages now. Work in parallel where possible.
```

---

## PROMPT 2 — Redesign an existing website

> Use this when you have existing HTML files and want them rebuilt with a modern design system.

```
I want you to do a full redesign of my website. It's a static HTML/CSS/JS site with no build tools, no frameworks, no npm. All styles are inline in <style> tags within each HTML page. The site is deployed on Netlify.

Before you start coding, create two files in the project root:

### 1. CLAUDE.md
Create a CLAUDE.md file that documents:
- Project overview (what the site is, what it does)
- Tech stack (vanilla HTML/CSS/JS, no frameworks, deployed on Netlify)
- Key directories and what's in them
- List of all site pages with descriptions
- Design system CSS custom properties (list every CSS variable)
- Typography (font family, sizes, weights)
- Component patterns (cards, buttons, animations, layout)
- Responsive breakpoints
- Coding conventions (inline styles, no external CSS, use var() for all colors, desktop-first media queries)
- Dark/light theme rules if applicable
- "Do NOT" rules (no Tailwind, no React, no npm, no external CSS files)

### 2. design_brief.md
Create a design_brief.md that documents:
- Brand identity and tone
- Full color system with variable names, hex values, and usage descriptions
- Typography scale (hero, h1, h2, section labels, body, small, fine print)
- Component patterns with actual CSS code snippets (cards, buttons, review cards, links, dividers)
- Layout rules (content widths, spacing scale, grid patterns)
- Animation standards (scroll reveal, fade in, hover interactions)
- Responsive breakpoints table
- Page structure template
- Design principles

### 3. Then redesign every HTML page and JS file with this modern design system:

**CSS Custom Properties (design tokens):**
```css
:root {
    --text-primary: #f0f4f8;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent: #0088DB;           /* change to your brand color */
    --accent-hover: #0099f0;     /* slightly lighter version */
    --accent-warm: #38b2f5;      /* secondary accent */
    --accent-glow: rgba(0,136,219,0.15);
    --background: #0a0e17;
    --background-alt: #111827;
    --border: #1e293b;
    --border-light: #2a3a50;
    --card-bg: rgba(17,24,39,0.7);
    --card-bg-solid: #111827;
    --card-hover: rgba(30,41,59,0.5);
    --gradient-start: #0088DB;
    --gradient-end: #38b2f5;
    --success: #10b981;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
}
```

**Font:** Inter via Google Fonts (weights 400, 500, 600, 700, 800)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

**Key design patterns to apply everywhere:**

1. **Glassmorphism header** — sticky, with `backdrop-filter:blur(20px) saturate(1.2)` and semi-transparent background
2. **Nav links** — pill-style with border-radius, subtle hover background `rgba(255,255,255,0.05)`, active state with accent tint
3. **Hero sections** — badge pill with pulsing dot animation, large headline with `letter-spacing:-0.03em`, staggered fade-up animations
4. **Section labels** — uppercase, small, accent colored, with a `::before` line (20px wide accent-colored bar)
5. **Cards** — `backdrop-filter:blur(10px)`, semi-transparent background `var(--card-bg)`, border, hover lifts with `translateY(-2px)` and box-shadow
6. **Gradient buttons** — `background:linear-gradient(135deg, var(--accent), var(--accent-hover))` with `::after` shine overlay that appears on hover
7. **Background atmosphere** — `body::before` with fixed radial gradients for subtle ambient glow
8. **Scroll reveal** — `.reveal` class with `opacity:0; transform:translateY(24px)` that transitions to visible via IntersectionObserver
9. **Smooth transitions** — `cubic-bezier(0.16,1,0.3,1)` for reveals, 0.2-0.3s for interactions
10. **Responsive** — desktop-first, breakpoints at 768px and 480px, single column on mobile

**Dark/light theme support:**
- Default dark theme
- Light theme via `[data-theme="light"]` on the HTML element
- Theme toggle button in header (moves to fixed position on scroll)
- Light theme overrides all CSS variables with appropriate light values
- Logo swap between dark/light versions

**JavaScript files to create/update:**
- `scroll-reveal.js` — IntersectionObserver that adds `.revealed` class to `.reveal` elements
- `theme-toggle.js` — creates toggle button, manages localStorage, injects light theme CSS overrides
- `scroll-top.js` — scroll-to-top button + sticky CTA bar that appear after 300px scroll
- `hamburger.js` — mobile hamburger menu that clones desktop nav links into a full-screen overlay

**Rules:**
- Keep ALL existing content, links, form attributes, and tracking scripts
- Every page gets the same header/nav and footer structure
- All styles inline in <style> tags, no external CSS files
- Use var() for every color — never hardcode hex in component styles
- All pages must include all 4 JS files at the bottom of <body>
- Mobile breakpoint: single column everything, smaller padding, smaller font sizes
- Use `clamp()` for hero headlines for fluid sizing
- Footer with 3-column grid: services links, company links, connect links

Go through every HTML page and every JS file. Redesign them all with this system. Work in parallel where possible for speed.
```

---

## Tips (both prompts)

- If Claude Code asks clarifying questions, say: "just do it, build everything"
- If it tries to create external CSS files: "all styles inline in `<style>` tags within each HTML file"
- If it suggests Tailwind or React: "vanilla HTML/CSS/JS only, no frameworks"
- After the build, ask for specific tweaks: "make the hero bigger", "change accent to #XX", "add a testimonials section"
- The CLAUDE.md and design_brief.md files keep Claude Code consistent across all pages and future sessions
- To change brand color: find-replace `[YOUR BRAND COLOR]` in the prompt before pasting
