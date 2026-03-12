# Website Redesign Instructions for Claude Code

Copy-paste this entire prompt into Claude Code in your other project. Replace the placeholder values in brackets with your actual project details.

---

## Prompt to paste:

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

## Tips

- If Claude Code asks clarifying questions, tell it to "just do it, redesign everything"
- If it tries to create external CSS files, remind it: "all styles inline in <style> tags within each HTML file"
- If it suggests Tailwind or React, remind it: "vanilla HTML/CSS/JS only, no frameworks"
- After the redesign, review the site and ask for specific tweaks (e.g. "make the hero bigger", "change accent color to #XX")
- The CLAUDE.md and design_brief.md files help Claude Code maintain consistency across all pages and future sessions
