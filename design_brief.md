# LaunchForte Design Brief

## Brand Identity
LaunchForte is a web design and automation agency that builds growth systems for businesses. The brand conveys **technical competence, professionalism, and trust** — not flashy or trendy, but reliable and results-driven.

## Color System

### Dark Theme (Default)
| Role | Variable | Value | Usage |
|------|----------|-------|-------|
| Primary text | `--text-primary` | `#edf2f7` | Headlines, names, key content |
| Secondary text | `--text-secondary` | `#94a3b8` | Body copy, descriptions |
| Muted text | `--text-muted` | `#64748b` | Labels, metadata, fine print |
| Accent blue | `--accent` | `#0088DB` | CTAs, links, highlights |
| Accent warm | `--accent-warm` | `#38b2f5` | Secondary highlights, stars |
| Background | `--background` | `#0d1117` | Page background |
| Background alt | `--background-alt` | `#121a28` | Nested/alternative backgrounds |
| Border | `--border` | `#1e2a3a` | All borders and dividers |
| Card background | `--card-bg` | `#172030` | Card and panel backgrounds |

### Stage Colors (Service Tiers)
| Stage | Color | Usage |
|-------|-------|-------|
| Foundation | `#8a8578` | Warm gray/taupe |
| Launch | `var(--accent)` / `#0088DB` | Primary blue |
| Growth | `#5fb88a` | Green |
| Scale | `var(--accent-warm)` / `#38b2f5` | Light blue |

### Accent Gradient
```css
background: linear-gradient(135deg, #0088DB, #38b2f5, #0088DB, #38b2f5);
background-size: 300% 300%;
animation: gradientShift 6s ease infinite;
```
Used for hero rotating words and key visual emphasis.

### Background Atmosphere
```css
background-image:
  radial-gradient(ellipse at 20% 0%, rgba(0,136,219,0.07) 0%, transparent 50%),
  radial-gradient(ellipse at 80% 100%, rgba(56,178,245,0.04) 0%, transparent 50%);
background-attachment: fixed;
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
| Body text | `17px` (base) | 400 | `line-height: 1.7–1.8` |
| Small text | `0.85rem–0.9rem` | 400–500 | — |
| Fine print | `0.75rem` | 400 | `color: var(--text-muted)` |

## Component Patterns

### Cards
```css
background: var(--card-bg);
border: 1px solid var(--border);
border-radius: 10px;
padding: 1.5rem; /* or 1.75rem for larger cards */
```
- Hover: `transform: translateY(-2px)` for interactive cards
- Stage cards: left border accent `border-left: 4px solid [stage-color]`

### Buttons
**Primary:**
```css
background: var(--accent);
color: #fff;
padding: 0.75rem 1.75rem;
border-radius: 6px;
font-size: 0.95rem;
font-weight: 500;
/* Hover: */
transform: translateY(-2px);
box-shadow: 0 6px 20px rgba(0,136,219,0.35);
```

**Secondary:**
```css
border: 1px solid var(--border);
color: var(--text-secondary);
padding: 0.75rem 1.75rem;
border-radius: 6px;
/* Hover: */
border-color: var(--accent);
color: var(--accent);
```

### Review Cards
- Star rating in `var(--accent-warm)` / gold `#f4c542`
- Quote text in italic, `var(--text-secondary)`
- Author name bold in `var(--text-primary)`
- Project label in `var(--text-muted)` smaller text

### Section Dividers
```css
border: none;
border-top: 1px solid var(--border);
margin: 4rem 0;
```

### Links
- Default: `color: var(--accent)`
- Hover: underline
- Transition: `color 0.2s ease`

## Layout Rules

### Content Width
- **Header container:** `max-width: 1000px`
- **Main content:** `max-width: 860px`
- Both centered with `margin: 0 auto`

### Spacing Scale
- Section gaps: `4rem` (via `<hr class="section-divider">`)
- Card grid gaps: `1.25rem`
- Content padding: `2rem` horizontal (desktop), `1.25rem` (mobile)
- Main content top/bottom: `5rem / 6rem` (desktop), `3rem / 4rem` (mobile)

### Grid Patterns
- **2-column grid:** `grid-template-columns: 1fr 1fr; gap: 1.25rem`
- **3-column grid:** `grid-template-columns: 1fr 1fr 1fr; gap: 2rem` (footer)
- **4-column grid:** `grid-template-columns: repeat(4, 1fr)` (credibility bar)
- All grids collapse to single column on mobile

## Animation Standards

### Scroll Reveal
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

### Interaction Feedback
- Hover lifts: `transform: translateY(-2px)`
- Transition duration: `0.2s ease` for interactions, `0.5s ease` for reveals
- Box shadows on hover: `box-shadow: 0 6px 20px rgba(0,136,219,0.35)`

## Responsive Design

### Desktop First
Styles are written for desktop, then overridden with `max-width` media queries.

### Breakpoints
| Breakpoint | Target | Key Changes |
|------------|--------|-------------|
| Default | Desktop (1024px+) | Full multi-column layouts |
| `max-width: 768px` | Tablet/mobile | Single column grids, reduced padding |
| `max-width: 600px` | Small mobile | Smaller hero text, adjusted spacing |
| `max-width: 480px` | Smallest | Single column footer |

## Page Structure Template
Every page follows this structure:
1. `<header class="site-header">` — sticky nav with logo + links
2. `<main class="main-content">` — page content at 860px max
3. Sections separated by `<hr class="section-divider">`
4. `<footer>` inside main content area with tools, columns, copyright

## Design Principles
1. **Subtlety over flash** — soft glows, gentle gradients, restrained animation
2. **Content-first** — generous whitespace, readable line lengths (~860px)
3. **Consistent depth** — cards lift slightly on hover, never dramatic shadows
4. **Professional trust** — clean typography, structured layouts, no visual clutter
5. **Accessible** — sufficient color contrast, semantic HTML, keyboard navigable
