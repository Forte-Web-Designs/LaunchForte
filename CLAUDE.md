# LaunchForte — Project Configuration for Claude Code

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
All colors and design tokens are defined as CSS custom properties in `:root`:

```css
:root {
  --text-primary: #edf2f7;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent: #0088DB;
  --accent-warm: #38b2f5;
  --background: #0d1117;
  --background-alt: #121a28;
  --border: #1e2a3a;
  --card-bg: #172030;
}
```

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
- Default is dark theme
- Light theme via `[data-theme="light"]` attribute on HTML element
- Theme toggle handled by `theme-toggle.js`
- Logo swaps between `.logo-img-dark` and `.logo-img-light`

## Important Notes
- Do NOT introduce Tailwind CSS, React, or any framework
- Do NOT create external CSS files — styles go in `<style>` within each page
- Do NOT add npm/package.json — this is a zero-dependency static site
- Match the existing dark, professional aesthetic in all new components
- When creating new pages, copy the header/footer structure from an existing page
- Always use `var()` references to CSS custom properties for theming support
