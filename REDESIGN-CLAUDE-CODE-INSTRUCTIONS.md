# CLAUDE CODE: Apple-Style Bold and Clear Redesign

## Purpose

This is the complete spec for converting an existing dark-themed personal or brand website into an Apple-style light-default site with optional dark mode. It is a structural and visual redesign only. No copy changes. No framework changes. Pure HTML, CSS, JS with inline styles.

Hand this entire file to Claude Code in another repo. It contains everything needed to replicate the look across an arbitrary number of HTML pages.

## Aesthetic Direction

Apple style. Bold but professional. Soft warm-light background. Massive type with breathing room. One idea per scroll section. Generous whitespace. Single accent color used sparingly. Pill-shaped CTAs. Sentence-case copy. Flat surfaces. No shadows. No body gradients. No hover lift. No purples.

## Constraints

- Vanilla HTML, CSS, JS. No frameworks, no build tools, no npm packages.
- All styles stay inline in each page's `<style>` block per the existing convention.
- Do not delete pages or change routes.
- Do not rewrite copy. Do not change headlines, body text, CTAs, alt tags, or any other content.
- Do not modify scroll-reveal.js or hamburger.js.
- Do not introduce new fonts. Use the system stack only.
- Do not add box-shadow on cards or buttons. Apple uses neither.
- Do not use transform translateY on hover. No lift effects.
- Keep all images (logo, headshot, favicon) untouched.
- Preserve light AND dark mode. Light is the default. Dark is toggled via theme-toggle.js.

## Color System

### Light mode (default)

These tokens replace the existing :root block in every page. Do not change the variable names. Existing component CSS that references these vars will keep working with the new values.

```css
:root {
    --text-primary: #1d1d1f;
    --text-secondary: #515154;
    --text-muted: #86868b;

    --accent: #0088DB;
    --accent-hover: #4ab5ed;
    --accent-warm: #4ab5ed;
    --accent-subtle: rgba(0,136,219,0.10);
    --accent-glow: rgba(0,136,219,0.10);
    --accent-tint: rgba(0,136,219,0.10);
    --accent-2: #4ab5ed;
    --accent-3: #0088DB;

    --background: #f5f5f7;
    --background-alt: #ffffff;
    --background-dark: #1d1d1f;
    --surface: #ffffff;
    --surface-hover: #f5f5f7;
    --card-bg: #ffffff;

    --border: rgba(0,0,0,0.08);
    --border-light: rgba(0,0,0,0.12);

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
    --radius-pill: 980px;
}
```

### Dark mode (handled by theme-toggle.js)

Triggered by `data-theme="dark"` on `<html>`. Stored in localStorage. Default is `light`. The dark palette is warm gray, not pure black. Card backgrounds are slightly lighter than the page so cards stand out without borders carrying the weight.

```
text-primary: #f5f5f7
text-secondary: #a1a1a6
text-muted: #86868b
accent: #4ab5ed       (brighter blue for dark bg contrast)
accent-warm: #0088DB
accent-tint: rgba(74,181,237,0.14)
background: #1d1d1f
background-dark: #000000  (footer)
surface / card-bg: #2a2a2c
surface-hover: #3a3a3c
border: rgba(255,255,255,0.10)
border-light: rgba(255,255,255,0.16)
```

## Typography

System font stack only. No Google Fonts, no Inter import unless already there as fallback.

```css
body {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
    font-size: 17px;
    line-height: 1.5;
    color: var(--text-primary);
    background: var(--background);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Display headlines: hero h1 */
.hero-headline, h1.display, .page-title, .hero h1 {
    font-weight: 500;                       /* Apple uses 500, not 700 */
    letter-spacing: -0.025em;
    line-height: 1.05;
    font-size: clamp(2.25rem, 5vw, 3.25rem); /* 36-52px */
    color: var(--text-primary);
}

/* Section headings */
h2, .section-heading {
    font-weight: 500;
    letter-spacing: -0.022em;
    line-height: 1.1;
    font-size: clamp(1.875rem, 3.5vw, 2.5rem); /* 30-40px */
}

/* Card and feature headings */
h3, .card-heading {
    font-weight: 500;
    letter-spacing: -0.015em;
    font-size: 1.25rem; /* 20px */
}

/* Sentence case eyebrows above headings in accent color */
.eyebrow, .section-label {
    font-size: 0.875rem;        /* 14px */
    font-weight: 500;
    color: var(--accent);
    letter-spacing: 0;
    text-transform: none;       /* NEVER uppercase - Apple uses sentence case */
    margin: 0 0 12px;
}
.section-label::before { display: none; }   /* Remove old "bar" before label */

/* Sub copy under headlines - bigger than body */
.sub, .lede, .hero-sub, .page-subtitle {
    font-size: 1.1875rem;       /* 19px */
    line-height: 1.45;
    color: var(--text-secondary);
    font-weight: 400;
    letter-spacing: -0.005em;
}

/* Body */
p {
    font-size: 1.0625rem;       /* 17px */
    line-height: 1.55;
    color: var(--text-secondary);
}

/* Fine print */
.fine-print, small {
    font-size: 0.75rem;
    color: var(--text-muted);
}
```

Key moves:
- Weight 500 for headings (not 700)
- -0.025em letter-spacing on display type
- Eyebrows are sentence case (not uppercase), accent colored
- Sub copy is 19px (not 16-17px)
- Body is 17px (not 16px)

## Buttons

Pill-shaped. Flat. No shadow. No lift. Color changes on hover only.

```css
.btn-primary {
    display: inline-block;
    background: var(--accent);
    color: #ffffff !important;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 980px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.2s ease;
    box-shadow: none !important;
}
.btn-primary:hover {
    background: var(--accent-warm);
    transform: none !important;
    box-shadow: none !important;
}

.btn-ghost, .btn-secondary {
    background: transparent;
    color: var(--accent);
    border: 1px solid var(--border-light);
    border-radius: 980px;
    padding: 0.75rem 1.5rem;
    font-size: 0.95rem;
    font-weight: 500;
    text-decoration: none;
    transition: background 0.2s ease, opacity 0.2s ease;
}
.btn-ghost:hover, .btn-secondary:hover {
    background: var(--accent-tint);
    color: var(--accent);
    opacity: 0.75;
    transform: none !important;
}

.btn-link {
    color: var(--accent) !important;
    font-weight: 500;
    text-decoration: none;
}
.btn-link:hover {
    color: var(--accent-warm) !important;
    opacity: 0.85;
}
```

**Remove** all `transform: translateY(-2px)` and `box-shadow: 0 8px 30px ...` from existing button styles. Add `!important` if needed to override.

## Cards

Soft, flat, large radius, no borders that fight the layout.

```css
.stage-card, .result-card, .review-card, .capability-card,
.step-card, .case-study-card, .featured-card, .video-quote-card,
.feature-block, .service-card, .featured-case, .audit-section,
.stat-card, .metric-item, .cta-block, .cta-section, .next-step,
.engagement-block {
    background: var(--card-bg);
    border-radius: 18px;
    border: 1px solid var(--border);
    transition: background 0.2s ease, border-color 0.2s ease;
}

/* Hover: subtle bg shift only, no lift, no shadow */
.stage-card:hover, .result-card:hover, .review-card:hover,
.capability-card:hover, .step-card:hover, .case-study-card:hover,
.featured-card:hover, .video-quote-card:hover {
    background: var(--background);
    border-color: var(--border-light);
    transform: none !important;
    box-shadow: none !important;
}
```

Apple uses 18-22px radius on cards. Don't use 6-12px small radius for cards.

## Backgrounds and Section Rhythm

The body background is flat. No radial gradients. No grid overlays.

```css
body::before, body::after { display: none !important; }
.grid-bg { display: none !important; }
```

For sites that use semantic section structure, alternate backgrounds:

```css
.section {
    padding: 5rem 1.5rem;
    text-align: center;
}
.section.tinted { background: var(--background); }   /* #f5f5f7 */
.section.white { background: #ffffff; }
.section.dark {
    background: var(--background-dark);              /* #1d1d1f */
    color: #f5f5f7;
    padding: 6rem 1.5rem;
}
.section.dark h2 { color: #f5f5f7; }
.section.dark .sub, .section.dark p { color: #a1a1a6; }
.section.dark .eyebrow { color: var(--accent-warm); }

.section-inner {
    max-width: 980px;
    margin: 0 auto;
}
.section-content {
    max-width: 620px;
    margin: 0 auto;
}

@media (max-width: 768px) {
    .section { padding: 3.5rem 1.25rem; }
    .section.dark { padding: 4rem 1.25rem; }
}
```

If the existing site does not have semantic `.section` containers, that's fine. The redesign still works without restructuring because the tokens, typography, buttons, and cards all cascade through existing layouts.

## Grids

```css
.grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 3.5rem;
    text-align: left;
}
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 3.5rem;
    text-align: left;
}
@media (max-width: 768px) {
    .grid-3, .grid-2 { grid-template-columns: 1fr; }
}
```

## Header (Sticky with Backdrop Blur)

```css
.site-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(245, 245, 247, 0.85) !important;
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 0.5px solid var(--border);
    padding: 14px 28px;
}
.site-header::after { display: none !important; } /* kill the old gradient line */

.header-logo {
    font-size: 0.9375rem;
    font-weight: 500;
    letter-spacing: -0.01em;
    color: var(--text-primary);
}
.nav-link {
    color: var(--text-primary);
    opacity: 0.85;
    font-size: 0.8125rem;
    font-weight: 400;
}
.nav-link:hover { color: var(--text-primary); opacity: 1; }
.nav-link.active { color: var(--text-primary); opacity: 1; font-weight: 500; }
```

## Footer (Dark Statement)

The footer is the bold dark moment of the page. Warm gray, not pure black.

```css
.footer-section, .site-footer {
    background: var(--background-dark);
    color: #86868b;
    border-top: none;
    margin-top: 6rem;
    padding: 3rem 2rem 2rem;
    border-radius: 18px 18px 0 0;       /* matches card radius */
}
.footer-section a, .site-footer a { color: #86868b; }
.footer-section a:hover, .site-footer a:hover { color: #ffffff; }
.footer-col h4 {
    color: #ffffff;
    opacity: 0.75;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.footer-email-main, .footer-email-main a {
    color: #ffffff !important;
    opacity: 0.95;
    font-weight: 500;
}
.footer-location, .copyright, .footer-status { color: #86868b !important; }
```

## Tag and Pill Treatments

```css
.tech-tag, .case-study-tags span, .review-tag {
    background: var(--accent-tint);
    color: var(--accent);
    border: none;
}
```

## Stats and Gradient Text

Stats render as flat accent color, NOT as gradient text. Kill old `-webkit-background-clip: text` treatments.

```css
.result-stat, .case-study-stat, .featured-stat, .stat-card .stat,
.feature-block .stat, .metric-value, .stat {
    color: var(--accent) !important;
    -webkit-text-fill-color: var(--accent) !important;
    background: none !important;
    background-clip: unset !important;
    -webkit-background-clip: unset !important;
}

.gradient-text {
    color: var(--accent);
    background: none;
    -webkit-text-fill-color: var(--accent);
    animation: none !important;
}
```

Apple does not use gradient text. One flat accent color, used sparingly.

## Eyebrow / Label Sentence Case Enforcement

Override any uppercase labels still present:

```css
.section-label, .stage-number, .step-number, .stage-label,
.case-label, .review-stars, .trust-label, .metric-label,
.featured-label, .stage-badge, .case-study-meta, .case-study-tags,
.review-attribution, .review-project, .footer-col h4 {
    text-transform: none;
    letter-spacing: 0;
}
```

(The footer h4 keeps uppercase, override it back where needed via the footer rules above.)

## Implementation Order

1. **Inventory the repo.** List every `.html` file. Note shared header/nav/footer patterns. Note image references. Read the existing CLAUDE.md if present.

2. **Replace :root tokens in every page.** Use sed/perl across all HTML files to swap the old values to the new ones. The variable names stay the same so existing CSS keeps working.

3. **Strip dark-mode artifacts.** Replace any `rgba(255,255,255,0.x)` borders, `linear-gradient(rgba(255,255,255,0.02)...)` grid backgrounds, dark hex literals (`#09090b`, `#141418`, `#0f0f13`, `#1a1a20`, `#0a0e17`) with their light counterparts.

4. **Inject Apple-style overrides** at the END of each page's `<style>` block (just before `</style>`). This block cascades over the existing rules using its later position and selective `!important` on hover/transform/shadow rules.

5. **Rewrite theme-toggle.js** so dark mode applies a warm-gray Apple-style palette (NOT pure black) and matches the same flat aesthetic. Default theme is `light`.

6. **Do not touch:** scroll-reveal.js, hamburger.js, image files, copy in HTML.

## The Sitewide Inject Block

This is the exact block to paste before each page's closing `</style>`. It is the heart of the redesign. Variable names match the tokens above.

```css
        /* Apple-style overrides */
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            font-size: 17px;
            line-height: 1.5;
        }
        .hero-headline, h1.display, .page-title, .hero h1 {
            font-weight: 500;
            letter-spacing: -0.025em;
            line-height: 1.05;
        }
        h2, .section-heading, .section-label.section-heading {
            font-weight: 500;
            letter-spacing: -0.022em;
            line-height: 1.1;
        }
        h3, .card-heading {
            font-weight: 500;
            letter-spacing: -0.015em;
        }
        .eyebrow {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--accent);
            letter-spacing: 0;
            text-transform: none;
            margin: 0 0 12px;
        }
        .sub, .lede, .hero-sub, .page-subtitle {
            font-size: 1.1875rem;
            line-height: 1.45;
            color: var(--text-secondary);
            font-weight: 400;
            letter-spacing: -0.005em;
        }
        p { font-size: 1.0625rem; line-height: 1.55; }

        .btn-primary {
            background: var(--accent);
            color: #fff !important;
            border-radius: 980px;
            font-weight: 500;
            box-shadow: none !important;
            transition: background 0.2s ease, color 0.2s ease;
        }
        .btn-primary:hover {
            background: var(--accent-warm, #4ab5ed);
            transform: none !important;
            box-shadow: none !important;
        }
        .btn-ghost, .btn-secondary {
            background: transparent;
            color: var(--accent);
            border: 1px solid var(--border-light);
            border-radius: 980px;
            font-weight: 500;
            transition: opacity 0.2s ease, background 0.2s ease;
        }
        .btn-ghost:hover, .btn-secondary:hover {
            opacity: 0.75;
            transform: none !important;
            background: var(--accent-tint, rgba(0,136,219,0.10));
            color: var(--accent);
            border-color: var(--border-light);
        }
        .btn-link { color: var(--accent) !important; font-weight: 500; }
        .btn-link:hover { color: var(--accent-warm, #4ab5ed) !important; opacity: 0.85; }

        .stage-card, .result-card, .review-card, .capability-card,
        .step-card, .case-study-card, .featured-card, .video-quote-card,
        .feature-block, .service-card, .featured-case, .audit-section,
        .stat-card, .metric-item, .cta-block, .cta-section, .next-step,
        .engagement-block {
            background: var(--card-bg, #ffffff);
            border-radius: 18px;
            border: 1px solid var(--border);
            transition: background 0.2s ease, border-color 0.2s ease;
        }
        .stage-card:hover, .result-card:hover, .review-card:hover,
        .capability-card:hover, .step-card:hover, .case-study-card:hover,
        .featured-card:hover, .video-quote-card:hover {
            transform: none !important;
            box-shadow: none !important;
            background: var(--background);
            border-color: var(--border-light);
        }

        .section-label, .stage-number, .step-number, .stage-label,
        .case-label, .review-stars, .trust-label, .metric-label,
        .featured-label, .stage-badge, .case-study-meta, .case-study-tags,
        .review-attribution, .review-project, .footer-col h4 {
            text-transform: none;
            letter-spacing: 0;
        }
        .section-label {
            color: var(--accent);
            font-size: 0.875rem;
            font-weight: 500;
        }
        .section-label::before { display: none; }

        body::before, body::after { display: none !important; }
        .grid-bg { display: none !important; }

        .footer-section, .site-footer {
            background: var(--background-dark, #1d1d1f);
            color: #86868b;
            border-top: none;
            margin-top: 6rem;
            padding: 3rem 2rem 2rem;
            border-radius: 18px 18px 0 0;
        }
        .footer-section a, .site-footer a { color: #86868b; }
        .footer-section a:hover, .site-footer a:hover { color: #ffffff; }
        .footer-col h4 {
            color: #ffffff;
            opacity: 0.75;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .footer-email-main, .footer-email-main a {
            color: #ffffff !important;
            opacity: 0.95;
            font-weight: 500;
        }
        .footer-location, .copyright, .footer-status { color: #86868b !important; }

        .site-header {
            background: rgba(245, 245, 247, 0.85) !important;
            backdrop-filter: saturate(180%) blur(20px);
            -webkit-backdrop-filter: saturate(180%) blur(20px);
            border-bottom: 0.5px solid var(--border);
        }
        .site-header::after { display: none !important; }
        .nav-link { color: var(--text-primary); opacity: 0.85; font-weight: 400; }
        .nav-link:hover { color: var(--text-primary); opacity: 1; }
        .nav-link.active { color: var(--text-primary); opacity: 1; font-weight: 500; }

        .tech-tag, .case-study-tags span, .review-tag {
            background: var(--accent-tint, rgba(0,136,219,0.10));
            color: var(--accent);
            border: none;
        }

        .result-stat, .case-study-stat, .featured-stat, .stat-card .stat,
        .feature-block .stat, .metric-value, .stat {
            color: var(--accent) !important;
            -webkit-text-fill-color: var(--accent) !important;
            background: none !important;
            background-clip: unset !important;
            -webkit-background-clip: unset !important;
        }
        .gradient-text {
            color: var(--accent);
            background: none;
            -webkit-text-fill-color: var(--accent);
            animation: none !important;
        }
```

## The theme-toggle.js Replacement

Drop this in as the complete file. It assumes there is a header container `.header-container` to place the toggle into. It falls back to `body` for mobile. It uses `localStorage` to persist the choice.

```javascript
(function() {
    var darkCSS = ':root[data-theme="dark"]{' +
        '--text-primary:#f5f5f7;' +
        '--text-secondary:#a1a1a6;' +
        '--text-muted:#86868b;' +
        '--accent:#4ab5ed;' +
        '--accent-hover:#0088DB;' +
        '--accent-warm:#0088DB;' +
        '--accent-subtle:rgba(74,181,237,0.12);' +
        '--accent-glow:rgba(74,181,237,0.12);' +
        '--accent-tint:rgba(74,181,237,0.14);' +
        '--accent-2:#0088DB;' +
        '--accent-3:#4ab5ed;' +
        '--background:#1d1d1f;' +
        '--background-alt:#000000;' +
        '--background-dark:#000000;' +
        '--surface:#2a2a2c;' +
        '--surface-hover:#3a3a3c;' +
        '--card-bg:#2a2a2c;' +
        '--border:rgba(255,255,255,0.10);' +
        '--border-light:rgba(255,255,255,0.16)}' +
        '[data-theme="dark"] body{background:#1d1d1f;color:#f5f5f7}' +
        '[data-theme="dark"] .site-header{background:rgba(29,29,31,0.85)!important;border-bottom:0.5px solid rgba(255,255,255,0.10)}' +
        '[data-theme="dark"] .nav-link{color:#f5f5f7;opacity:0.85}' +
        '[data-theme="dark"] .nav-link:hover,[data-theme="dark"] .nav-link.active{color:#f5f5f7;opacity:1}' +
        '[data-theme="dark"] .header-logo{color:#f5f5f7}' +
        '[data-theme="dark"] .stage-card,[data-theme="dark"] .result-card,[data-theme="dark"] .review-card,[data-theme="dark"] .capability-card,[data-theme="dark"] .step-card,[data-theme="dark"] .case-study-card,[data-theme="dark"] .featured-card,[data-theme="dark"] .video-quote-card,[data-theme="dark"] .feature-block,[data-theme="dark"] .service-card,[data-theme="dark"] .featured-case,[data-theme="dark"] .audit-section,[data-theme="dark"] .stat-card,[data-theme="dark"] .metric-item,[data-theme="dark"] .cta-block,[data-theme="dark"] .cta-section,[data-theme="dark"] .next-step,[data-theme="dark"] .engagement-block{background:#2a2a2c;border-color:rgba(255,255,255,0.10);color:#f5f5f7}' +
        '[data-theme="dark"] .stage-card:hover,[data-theme="dark"] .result-card:hover,[data-theme="dark"] .review-card:hover,[data-theme="dark"] .capability-card:hover,[data-theme="dark"] .step-card:hover,[data-theme="dark"] .case-study-card:hover,[data-theme="dark"] .featured-card:hover,[data-theme="dark"] .video-quote-card:hover{background:#3a3a3c;border-color:rgba(255,255,255,0.16)}' +
        '[data-theme="dark"] h1,[data-theme="dark"] h2,[data-theme="dark"] h3,[data-theme="dark"] h4,[data-theme="dark"] .page-title,[data-theme="dark"] .section-heading,[data-theme="dark"] .hero-headline{color:#f5f5f7}' +
        '[data-theme="dark"] p,[data-theme="dark"] .body-text,[data-theme="dark"] .about-text,[data-theme="dark"] .sub,[data-theme="dark"] .hero-sub,[data-theme="dark"] .page-subtitle{color:#a1a1a6}' +
        '[data-theme="dark"] .review-text,[data-theme="dark"] .video-quote-text{color:#a1a1a6}' +
        '[data-theme="dark"] .review-name,[data-theme="dark"] .video-quote-name{color:#f5f5f7}' +
        '[data-theme="dark"] .review-project,[data-theme="dark"] .video-quote-project,[data-theme="dark"] .case-study-meta,[data-theme="dark"] .stage-tagline{color:#86868b}' +
        '[data-theme="dark"] .btn-primary{background:#4ab5ed;color:#1d1d1f!important}' +
        '[data-theme="dark"] .btn-primary:hover{background:#0088DB;color:#ffffff!important}' +
        '[data-theme="dark"] .btn-ghost,[data-theme="dark"] .btn-secondary{color:#4ab5ed;border-color:rgba(255,255,255,0.16)}' +
        '[data-theme="dark"] .btn-ghost:hover,[data-theme="dark"] .btn-secondary:hover{background:rgba(74,181,237,0.12);color:#4ab5ed}' +
        '[data-theme="dark"] .btn-link{color:#4ab5ed!important}' +
        '[data-theme="dark"] .btn-link:hover{color:#7ec9f1!important}' +
        '[data-theme="dark"] a{color:#4ab5ed}' +
        '[data-theme="dark"] .section-label,[data-theme="dark"] .eyebrow{color:#4ab5ed}' +
        '[data-theme="dark"] .result-stat,[data-theme="dark"] .case-study-stat,[data-theme="dark"] .featured-stat,[data-theme="dark"] .stat-card .stat,[data-theme="dark"] .feature-block .stat,[data-theme="dark"] .metric-value,[data-theme="dark"] .stat,[data-theme="dark"] .gradient-text{color:#4ab5ed!important;-webkit-text-fill-color:#4ab5ed!important}' +
        '[data-theme="dark"] .footer-section,[data-theme="dark"] .site-footer{background:#000000;color:#86868b}' +
        '[data-theme="dark"] .tech-tag,[data-theme="dark"] .case-study-tags span,[data-theme="dark"] .review-tag{background:rgba(74,181,237,0.14);color:#4ab5ed}' +
        '[data-theme="dark"] .carousel-item{color:#a1a1a6}' +
        '[data-theme="dark"] .metric-label,[data-theme="dark"] .trust-label,[data-theme="dark"] .featured-label,[data-theme="dark"] .stage-number,[data-theme="dark"] .step-number,[data-theme="dark"] .case-label{color:#86868b}' +
        '[data-theme="dark"] .featured-in,[data-theme="dark"] .featured-in a{color:#a1a1a6}' +
        '[data-theme="dark"] hr,[data-theme="dark"] .section-divider{border-color:rgba(255,255,255,0.10)}' +
        '[data-theme="dark"] .results-summary li{color:#a1a1a6}' +
        '[data-theme="dark"] .results-summary li strong{color:#f5f5f7}' +
        '[data-theme="dark"] .hamburger-overlay{background:rgba(29,29,31,0.98)}' +
        '[data-theme="dark"] .hamburger-overlay a{color:#f5f5f7}' +
        '[data-theme="dark"] .hamburger-overlay a:hover{color:#4ab5ed}' +
        '[data-theme="dark"] #scroll-top-btn{background:#2a2a2c;border-color:rgba(255,255,255,0.10);color:#a1a1a6}' +
        '[data-theme="dark"] #scroll-top-btn:hover{color:#4ab5ed;border-color:rgba(74,181,237,0.40)}' +
        '[data-theme="dark"] #sticky-cta-bar{background:rgba(29,29,31,0.95);border-top-color:rgba(255,255,255,0.10)}' +
        '[data-theme="dark"] #sticky-cta-link{background:#4ab5ed;color:#1d1d1f}' +
        '[data-theme="dark"] #sticky-cta-link:hover{background:#0088DB;color:#ffffff}';

    var toggleCSS = '#theme-toggle{width:36px;height:36px;border-radius:50%;border:1px solid var(--border);background:transparent;color:var(--text-muted);font-size:1rem;cursor:pointer;z-index:1001;display:flex;align-items:center;justify-content:center;transition:color 0.3s ease,border-color 0.3s ease;line-height:1;flex-shrink:0;margin-left:0.75rem}' +
        '#theme-toggle.scrolled{position:fixed;top:auto;bottom:8.5rem;right:2rem;margin-left:0;background:var(--background);border:1px solid var(--border-light)}' +
        '#theme-toggle:hover{color:var(--text-primary);border-color:var(--border-light)}' +
        '@media(max-width:768px){#theme-toggle{position:fixed;top:1rem;right:4rem;margin-left:0;background:var(--background);border:1px solid var(--border-light)}}' +
        '@media(max-width:480px){#theme-toggle{width:34px;height:34px;font-size:0.95rem;right:3.5rem}#theme-toggle.scrolled{right:1.25rem;bottom:8rem}}';

    var style = document.createElement('style');
    style.textContent = darkCSS + toggleCSS;
    document.head.appendChild(style);

    var toggle = document.createElement('button');
    toggle.id = 'theme-toggle';
    toggle.setAttribute('aria-label', 'Toggle light/dark mode');

    var isMobile = window.innerWidth <= 768;
    var headerContainer = document.querySelector('.header-container');

    if (headerContainer && !isMobile) {
        headerContainer.appendChild(toggle);
    } else {
        document.body.appendChild(toggle);
    }

    var saved = localStorage.getItem('theme');
    var theme = saved || 'light';
    applyTheme(theme);

    function applyTheme(t) {
        document.documentElement.setAttribute('data-theme', t);
        toggle.innerHTML = t === 'dark' ? '☀️' : '🌘';
        localStorage.setItem('theme', t);
    }

    toggle.addEventListener('click', function() {
        var current = document.documentElement.getAttribute('data-theme');
        applyTheme(current === 'dark' ? 'light' : 'dark');
    });

    var isScrolled = false;
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            if (!isScrolled) {
                isScrolled = true;
                toggle.classList.add('scrolled');
                if (!isMobile && headerContainer && toggle.parentNode === headerContainer) {
                    document.body.appendChild(toggle);
                }
            }
        } else {
            if (isScrolled) {
                isScrolled = false;
                toggle.classList.remove('scrolled');
                if (!isMobile && headerContainer) {
                    toggle.style.position = '';
                    toggle.style.top = '';
                    toggle.style.right = '';
                    headerContainer.appendChild(toggle);
                }
            }
        }
    });
})();
```

## Step-by-Step Execution Recipe

These are the exact shell commands used to apply the redesign to the existing site. Run from the repo root.

### Step 1: Swap design tokens in every page

```bash
cat > /tmp/swap_tokens.pl << 'PERLEOF'
use strict;
use warnings;

my $file = $ARGV[0];
open(my $fh, '<', $file) or die "Cannot open $file: $!";
my $content = do { local $/; <$fh> };
close($fh);

$content =~ s/--text-primary:\s*#f0f4f8/--text-primary: #1d1d1f/g;
$content =~ s/--text-secondary:\s*#94a3b8/--text-secondary: #515154/g;
$content =~ s/--text-muted:\s*#64748b/--text-muted: #86868b/g;
$content =~ s/--accent-hover:\s*#38b2f5/--accent-hover: #4ab5ed/g;
$content =~ s/--accent-subtle:\s*rgba\(0,136,219,0\.08\)/--accent-subtle: rgba(0,136,219,0.10)/g;
$content =~ s/--accent-glow:\s*rgba\(0,136,219,0\.25\)/--accent-glow: rgba(0,136,219,0.10)/g;
$content =~ s/--accent-2:\s*#0EA5E9/--accent-2: #4ab5ed/gi;
$content =~ s/--accent-3:\s*#06B6D4/--accent-3: #0088DB/gi;
$content =~ s/--background:\s*#09090b/--background: #f5f5f7/g;
$content =~ s/--background-alt:\s*#0f0f13/--background-alt: #ffffff/g;
$content =~ s/--surface:\s*#141418/--surface: #ffffff/g;
$content =~ s/--surface-hover:\s*#1a1a20/--surface-hover: #f5f5f7/g;
$content =~ s/--border:\s*rgba\(255,255,255,0\.06\)/--border: rgba(0,0,0,0.08)/g;
$content =~ s/--border-light:\s*rgba\(255,255,255,0\.1\)/--border-light: rgba(0,0,0,0.12)/g;

if ($content !~ /--background-dark/) {
    $content =~ s/(--border-light:[^;]+;)/$1\n            --background-dark: #1d1d1f;\n            --card-bg: #ffffff;\n            --accent-warm: #4ab5ed;\n            --accent-tint: rgba(0,136,219,0.10);/;
}

$content =~ s/rgba\(9,9,11,0\.7\)/rgba(245,245,247,0.85)/g;
$content =~ s/background:\s*#09090b\b/background: #f5f5f7/g;
$content =~ s/background-color:\s*#09090b\b/background-color: #f5f5f7/g;
$content =~ s/#141418/#ffffff/g;
$content =~ s/#0f0f13/#ffffff/g;
$content =~ s/#1a1a20/#f5f5f7/g;

open(my $out, '>', $file) or die "Cannot write $file: $!";
print $out $content;
close($out);
PERLEOF

find . -name "*.html" -not -path "./v2/*" -exec perl /tmp/swap_tokens.pl {} \;
```

Notes:
- The "old" hex values in the script are what the existing site uses. If your starting site has DIFFERENT old hexes, modify the regex left-hand sides to match.
- The `--background-dark`, `--card-bg`, `--accent-warm`, `--accent-tint` vars are appended if missing.

### Step 2: Strip residual white-on-dark CSS

```bash
find . -name "*.html" -not -path "./v2/*" -exec perl -i -pe '
s/linear-gradient\(rgba\(255,255,255,0\.02\)\s+1px,\s*transparent\s+1px\)/linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px)/g;
s/linear-gradient\(90deg,\s*rgba\(255,255,255,0\.02\)\s+1px,\s*transparent\s+1px\)/linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px)/g;
s/rgba\(255,255,255,0\.04\)/rgba(0,0,0,0.04)/g;
s/rgba\(255,255,255,0\.03\)/rgba(0,0,0,0.03)/g;
s/rgba\(255,255,255,0\.05\)/rgba(0,0,0,0.04)/g;
s/rgba\(255,255,255,0\.06\)/rgba(0,0,0,0.06)/g;
s/rgba\(255,255,255,0\.08\)/rgba(0,0,0,0.08)/g;
s/rgba\(255,255,255,0\.1\)/rgba(0,0,0,0.10)/g;
s/rgba\(255,255,255,0\.12\)/rgba(0,0,0,0.12)/g;
s/rgba\(255,255,255,0\.15\)/rgba(0,0,0,0.12)/g;
s/rgba\(255,255,255,0\.2\)/rgba(0,0,0,0.18)/g;
s/#0a0e17/#f5f5f7/g;
s/#0b0b0e/#ffffff/g;
s/#161618/#ffffff/g;
' {} \;
```

### Step 3: Inject the Apple-style override block

Save the override block (from "The Sitewide Inject Block" section above) to `/tmp/apple_overrides.css`. Then:

```bash
cat > /tmp/inject_apple.pl << 'PERLEOF'
use strict;
use warnings;

my $file = $ARGV[0];
open(my $fh, '<', $file) or die "Cannot open $file: $!";
my $content = do { local $/; <$fh> };
close($fh);

exit 0 if $content =~ /Apple-style overrides/;

open(my $cssfh, '<', '/tmp/apple_overrides.css') or die "Cannot open overrides";
my $overrides = do { local $/; <$cssfh> };
close($cssfh);

my $changed = ($content =~ s|</style>|$overrides\n    </style>|);

if ($changed) {
    open(my $out, '>', $file) or die "Cannot write $file: $!";
    print $out $content;
    close($out);
    print "Injected: $file\n";
}
PERLEOF

for f in $(find . -name "*.html" -not -path "./v2/*"); do
  perl /tmp/inject_apple.pl "$f" > /dev/null
done

# Handle filenames with spaces separately
find . -name "*.html" -not -path "./v2/*" -print0 | while IFS= read -r -d '' f; do
  perl /tmp/inject_apple.pl "$f" > /dev/null
done
```

### Step 4: Replace theme-toggle.js

Save the theme-toggle.js replacement (from "The theme-toggle.js Replacement" section above) as `theme-toggle.js` in the repo root.

### Step 5: Validation

```bash
# Token count check
grep -l "#1d1d1f" --include="*.html" -r . | grep -v "v2/" | wc -l
grep -l "Apple-style overrides" --include="*.html" -r . | grep -v "v2/" | wc -l

# Should equal total HTML file count
find . -name "*.html" -not -path "./v2/*" | wc -l

# No leftover dark backgrounds
grep -rn "background:\s*#09090b\|--background:\s*#09090b" --include="*.html" . | grep -v "v2/"

# No leftover white-on-dark borders
grep -rn "rgba(255,255,255" --include="*.html" . | grep -v "v2/"

# Brace balance on key pages
for f in index.html about.html services.html; do
  style_content=$(awk '/<style>/,/<\/style>/' "$f")
  open_count=$(echo "$style_content" | grep -o "{" | wc -l | tr -d ' ')
  close_count=$(echo "$style_content" | grep -o "}" | wc -l | tr -d ' ')
  echo "$f: { $open_count, } $close_count"
done

# Local server check (HTTP 200 on every page)
python3 -m http.server 8765 > /dev/null 2>&1 &
sleep 2
for page in / /about.html /services.html /contact.html; do
  http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8765$page")
  echo "$page -> $http_code"
done
kill %1 2>/dev/null
```

## Design Principles Cheatsheet

When in doubt, follow these:

1. **Apple-style breathing room.** One idea per section. Generous whitespace. Sub copy at 19px, body at 17px. Section padding 5rem desktop, 3.5rem mobile.
2. **Sentence case everywhere.** No ALL CAPS labels. No Title Case in body copy. Eyebrows are sentence case in accent blue.
3. **Single accent.** Blue (#0088DB) used sparingly for CTAs, links, eyebrows, stat numbers, icon backgrounds. Never as a background fill.
4. **Soft contrast.** Warm light backgrounds. Near black text (#1d1d1f). Never pure black on pure white. Never gradient backgrounds on body.
5. **Flat surfaces.** No shadows. No hover lift. 18-22px radius on cards. Sticky header with backdrop blur is the only "depth" effect.
6. **Pill buttons.** 980px radius. Color shift on hover, never lift, never glow.
7. **Two backgrounds plus one dark.** Sections alternate between #f5f5f7 (tinted) and #ffffff (white). Footer is dark warm gray (#1d1d1f). That's the entire palette.
8. **No purples.** Single accent in the blue family. Even gradients stay in blue.

## What Should Be UNCHANGED

- All page copy
- All headlines and CTAs
- All image references (logo, headshot, favicons)
- Page routes and file paths
- scroll-reveal.js, hamburger.js, scroll-top.js
- Meta tags, OpenGraph, Twitter cards, JSON-LD schema
- The hero gradient text wrap (if it exists, just remove the animation and gradient — keep the span)
- Existing navigation structure
- Footer content (only styling changes)

## Commit Message Template

```
Redesign [sitename] Apple style bold and clear visual refresh

Replaced dark indigo palette with soft warm light background (#f5f5f7)
across all N HTML files. Tokens preserved by name so existing component
CSS keeps working with new values.

Tokens (light default):
  --text-primary: #1d1d1f
  --text-secondary: #515154
  --text-muted: #86868b
  --accent: #0088DB
  --background: #f5f5f7
  --background-dark: #1d1d1f

Apple style overrides injected into every page:
  - SF Pro Display system font stack
  - 17px body, 19px sub, weight 500 headings, -0.025em letter-spacing
  - Pill shaped 980px radius buttons, no hover lift, no glow
  - Cards: 18px radius, no shadows, soft borders
  - Sticky header with backdrop blur
  - Dark footer (warm gray #1d1d1f)
  - Sentence case eyebrows in accent color
  - Flat body bg, removed radial overlays and grid pattern

theme-toggle.js rewritten:
  - Light is now the default Apple style
  - Dark mode shifts to warm-gray (#1d1d1f) instead of pure black
  - All cards, buttons, links, footer adapt cleanly
  - Same blue accent (#4ab5ed brighter) in dark mode

All copy preserved unchanged. Images, schema, and routes untouched.
All pages validated 200 OK on local server.
```
