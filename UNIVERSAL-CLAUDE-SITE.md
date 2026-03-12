# Universal Modern Static Site — Claude Code Instructions

> **How to use:** Copy this file into any project as `CLAUDE.md`. Replace placeholder values (brand name, colors, fonts) with your own. Claude Code will follow these conventions when building your site.

## Project Overview
[YOUR_BRAND] is a static HTML/CSS/JS website. No frameworks, no build tools, no dependencies.

## Tech Stack
- **Frontend:** Vanilla HTML, CSS (custom properties), vanilla JavaScript
- **Styling:** Custom CSS with CSS custom properties (NO Tailwind, NO frameworks)
- **Deployment:** Static hosting (Netlify, Vercel, GitHub Pages, etc.)
- **No build step** — files are served directly

## Key Directories
- `/site/` — All public-facing HTML pages, JS, and assets
- `/site/images/` — All image assets

## Design System — CSS Custom Properties

All colors and design tokens are defined as CSS custom properties in `:root`. **Never hardcode hex values in component styles — always use `var()` references.**

```css
:root {
  /* =========================
     TEXT COLORS
     ========================= */
  --text-primary: #edf2f7;       /* Headlines, names, key content */
  --text-secondary: #94a3b8;     /* Body copy, descriptions */
  --text-muted: #64748b;         /* Labels, metadata, fine print */

  /* =========================
     BRAND / ACCENT COLORS
     ========================= */
  --accent: #0088DB;             /* CTAs, links, highlights */
  --accent-warm: #38b2f5;        /* Secondary highlights, hover states */

  /* =========================
     BACKGROUNDS
     ========================= */
  --background: #0d1117;         /* Page background */
  --background-alt: #121a28;     /* Nested/alternative sections */
  --card-bg: #172030;            /* Card and panel backgrounds */

  /* =========================
     BORDERS & DIVIDERS
     ========================= */
  --border: #1e2a3a;             /* All borders and dividers */
}
```

### Background Atmosphere (optional subtle depth)
```css
body {
  background-color: var(--background);
  background-image:
    radial-gradient(ellipse at 20% 0%, rgba(0,136,219,0.07) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 100%, rgba(56,178,245,0.04) 0%, transparent 50%);
  background-attachment: fixed;
}
```

### Accent Gradient (for hero elements, key visual emphasis)
```css
background: linear-gradient(135deg, var(--accent), var(--accent-warm), var(--accent), var(--accent-warm));
background-size: 300% 300%;
animation: gradientShift 6s ease infinite;

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
```

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Scale
| Element | Size | Weight | Properties |
|---------|------|--------|------------|
| Hero headline | `clamp(1.75rem, 4vw, 2.5rem)` | 700 | `letter-spacing: -0.02em; line-height: 1.3` |
| Page headline (h1) | `1.75rem–2.5rem` | 700 | `letter-spacing: -0.02em` |
| Section heading (h2) | `1.1rem–1.25rem` | 700 | — |
| Section label | `0.8rem` | 600 | `uppercase; letter-spacing: 0.1em; color: var(--text-muted)` |
| Body text | `17px` (base) | 400 | `line-height: 1.7` |
| Small text | `0.85rem–0.9rem` | 400–500 | — |
| Fine print | `0.75rem` | 400 | `color: var(--text-muted)` |

## Component Patterns

### Cards
```css
.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.5rem;
  transition: transform 0.2s ease;
}
.card:hover {
  transform: translateY(-2px);
}
```
- Use `padding: 1.75rem` for larger feature cards
- For category/accent cards: add `border-left: 4px solid var(--accent)`

### Buttons
**Primary:**
```css
.btn-primary {
  background: var(--accent);
  color: #fff;
  padding: 0.75rem 1.75rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
  display: inline-block;
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,136,219,0.35);
}
```

**Secondary:**
```css
.btn-secondary {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0.75rem 1.75rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease;
  text-decoration: none;
  display: inline-block;
}
.btn-secondary:hover {
  border-color: var(--accent);
  color: var(--accent);
}
```

### Links
```css
a {
  color: var(--accent);
  text-decoration: none;
  transition: color 0.2s ease;
}
a:hover {
  text-decoration: underline;
}
```

### Section Dividers
```css
.section-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 4rem 0;
}
```

## Layout Rules

### Content Width
- **Header/nav container:** `max-width: 1000px`
- **Main content:** `max-width: 860px`
- Both centered with `margin: 0 auto`

### Spacing
- Section gaps: `4rem` (via `<hr class="section-divider">`)
- Card grid gaps: `1.25rem`
- Content padding: `2rem` horizontal (desktop), `1.25rem` (mobile)
- Main content top padding: `5rem` (desktop), `3rem` (mobile)
- Main content bottom padding: `6rem` (desktop), `4rem` (mobile)

### Grid Patterns
```css
/* 2-column grid */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

/* 3-column grid */
.grid-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 2rem;
}

/* 4-column grid */
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

/* All grids collapse to single column on mobile */
@media (max-width: 768px) {
  .grid-2, .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
}
```

## Animation Standards

### Scroll Reveal (JavaScript-triggered)
```css
.reveal {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.reveal.revealed {
  opacity: 1;
  transform: translateY(0);
}
```

### Fade In Up (page load)
```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Stagger Delays
```css
.animate-delay-1 { animation-delay: 0.1s; }
.animate-delay-2 { animation-delay: 0.2s; }
.animate-delay-3 { animation-delay: 0.3s; }
```

### Interaction Rules
- Hover lifts: `transform: translateY(-2px)`
- Transition duration: `0.2s ease` for interactions, `0.5s ease` for reveals
- Box shadows on hover: `box-shadow: 0 6px 20px rgba(0,136,219,0.35)` (adjust rgba to match your accent)

## Responsive Design

### Desktop First
Styles are written for desktop, then overridden with `max-width` media queries.

### Breakpoints
| Breakpoint | Target | Key Changes |
|------------|--------|-------------|
| Default | Desktop (1024px+) | Full multi-column layouts |
| `max-width: 768px` | Tablet/mobile | Single column grids, reduced padding, smaller headings |
| `max-width: 600px` | Small mobile | Smaller hero text, adjusted spacing |
| `max-width: 480px` | Smallest | Single column footer, minimal padding |

## Page Structure Template
Every page follows this structure:
```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title — [YOUR_BRAND]</title>
  <style>
    /* All styles inline here — no external CSS files */
  </style>
</head>
<body>
  <header class="site-header">
    <!-- Sticky nav with logo + links -->
  </header>

  <main class="main-content">
    <!-- Page content at 860px max-width -->
    <!-- Sections separated by <hr class="section-divider"> -->

    <footer>
      <!-- Footer inside main content area -->
    </footer>
  </main>

  <script src="scroll-reveal.js"></script>
</body>
</html>
```

## Scroll Reveal Script (scroll-reveal.js)
```javascript
document.addEventListener('DOMContentLoaded', function() {
  const reveals = document.querySelectorAll('.reveal');
  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  reveals.forEach(function(el) { observer.observe(el); });
});
```

## Hamburger Menu Script (hamburger.js)
```javascript
document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.querySelector('.hamburger');
  const nav = document.querySelector('.nav-links');
  if (toggle && nav) {
    toggle.addEventListener('click', function() {
      nav.classList.toggle('open');
      toggle.classList.toggle('active');
    });
  }
});
```

## Coding Conventions (STRICT)
1. **All styles are inline in `<style>` tags** within each HTML file — NO external CSS files
2. **No build tools or preprocessors** — write production-ready CSS directly
3. **Use CSS custom properties** (`var(--accent)`, etc.) for ALL colors — never hardcode hex values in component styles
4. **Mobile-first is NOT used** — desktop-first with `max-width` media queries
5. **Keep it minimal** — no unnecessary libraries, frameworks, or dependencies
6. **Every page** includes the same header/nav and footer structure
7. **Accessibility:** Use semantic HTML, proper heading hierarchy (h1 > h2 > h3), descriptive link text
8. Do NOT introduce Tailwind CSS, React, or any framework
9. Do NOT create external CSS files — styles go in `<style>` within each page
10. Do NOT add npm/package.json — this is a zero-dependency static site
11. Match the dark, professional aesthetic in all new components
12. When creating new pages, copy the header/footer structure from an existing page
13. Always use `var()` references to CSS custom properties for theming support

## Design Principles
1. **Subtlety over flash** — soft glows, gentle gradients, restrained animation
2. **Content-first** — generous whitespace, readable line lengths (~860px)
3. **Consistent depth** — cards lift slightly on hover, never dramatic shadows
4. **Professional trust** — clean typography, structured layouts, no visual clutter
5. **Accessible** — sufficient color contrast, semantic HTML, keyboard navigable
