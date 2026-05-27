---
name: Gourmet AI
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#ffb2b7'
  on-secondary: '#67001b'
  secondary-container: '#b50036'
  on-secondary-container: '#ffc2c4'
  tertiary: '#a4c9ff'
  on-tertiary: '#00315d'
  tertiary-container: '#60a5fa'
  on-tertiary-container: '#003a6b'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#ffdadb'
  secondary-fixed-dim: '#ffb2b7'
  on-secondary-fixed: '#40000d'
  on-secondary-fixed-variant: '#92002a'
  tertiary-fixed: '#d4e3ff'
  tertiary-fixed-dim: '#a4c9ff'
  on-tertiary-fixed: '#001c39'
  on-tertiary-fixed-variant: '#004883'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  display-hero:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  display-hero-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-card:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1.4'
    letterSpacing: -0.01em
  body-main:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: 0em
  label-caps:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.0'
    letterSpacing: 0.1em
  status-telemetry:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: '1.0'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 32px
  gutter: 24px
  sidebar-width: 280px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
The design system embodies a "Digital Sommelier" persona—sophisticated, precise, and authoritative. It targets a high-end demographic that values culinary excellence and technological precision. 

The aesthetic is **Glassmorphic-Industrial**, blending the sleekness of high-end software with the physical depth of luxury environments. It utilizes deep layering, background blurs, and luminous accents to create a sense of infinite depth. The interface feels like a premium glass cockpit for gastronomic exploration, emphasizing clarity through translucency and high-fidelity motion.

## Colors
This design system operates primarily in a high-contrast dark mode to evoke the atmosphere of a dimly lit, high-end restaurant. 

- **Foundational Neutrals:** The base uses Obsidian (#0B0F19) to provide maximum contrast for glass layers.
- **Accents:** Emerald is reserved for AI-generated insights and high-confidence matches. Rose is used sparingly for luxury-tier pricing and critical alerts.
- **Atmospherics:** Implement two massive background radial gradients: a 30% opacity Emerald blur (top-left) and a 20% opacity Rose blur (bottom-right). These should remain fixed during scroll to provide a sense of environmental lighting.

## Typography
The typography leverages **Plus Jakarta Sans** for its modern, geometric structure that maintains warmth. 

- **Headings:** Use tight letter-spacing and heavy weights to create a "editorial" feel.
- **Captions & Labels:** All labels, badges, and overlines must use the `label-caps` style to distinguish metadata from content.
- **Telemetry:** Small data points in status bars should use **Inter** for its superior legibility at micro-scales.

## Layout & Spacing
The system utilizes a **12-column fluid grid** for the main content area, anchored by a fixed-width sidebar. 

- **Margins:** Desktop views require a minimum of 32px outer padding to allow the background blurs to frame the content.
- **Rhythm:** Use a 4px base unit. Component internal padding should default to 16px (4 units) or 24px (6 units) for premium "breathing room."
- **Sidebar:** The sidebar is a semi-transparent blur (`sidebar` token) that sits at the highest Z-index, visually pinning the navigation.

## Elevation & Depth
Depth is created through "Glass-Stacking" rather than traditional drop shadows.

1.  **Level 0 (Floor):** The base background with radial accent blurs.
2.  **Level 1 (Sub-surface):** Used for sidebar and search inputs. Subtle 1px border.
3.  **Level 2 (Cards):** 20px Backdrop blur. Border is a 1px linear gradient (Top-left: White 15% to Bottom-right: White 2%).
4.  **Level 3 (Modals/Overlays):** Increased backdrop blur (40px) and a slightly brighter border to denote floating priority.

**Interactions:** On hover, cards should "Lift" by 4px and the border opacity should increase to 20%. Add a 2px vertical accent bar of the `primary_color` on the left edge during the active state.

## Shapes
The system uses a **Rounded** (0.5rem base) corner radius to soften the high-tech aesthetic, making it feel more approachable and organic (like high-end dinnerware).

- **Standard Elements:** 8px (0.5rem) for buttons and small cards.
- **Large Containers:** 16px (1rem) for main content cards and modals.
- **Status Badges:** Fully rounded (pill) for quick visual scanning.

## Components

### Premium Glassmorphic Cards
Cards feature a `surface` fill with 20px backdrop blur. 
- **AI Confidence Ring:** A circular SVG stroke in the top-right corner. The stroke color uses `accent-emerald` for high confidence (>85%) and `accent-amber` for lower. 
- **Justification Box:** A bottom-docked section within the card with a slightly darker background (10% more opaque) explaining "Why this for you."

### Status Bars (Live Telemetry)
Positioned at the bottom of the viewport or card. Use `status-telemetry` typography. Include small "pulsing" dot icons next to live data strings (e.g., "AI PROCESSING: 42ms").

### Sidebar Navigation
The sidebar should use the `sidebar` color token. Active links feature a glowing left-border and a subtle horizontal gradient background behind the text. Search controls within the sidebar should be recessed (inset shadow) to feel like they are cut out of the glass.

### Comparison Modal
A full-screen overlay with two side-by-side glass cards. Use a vertical divider line with 5% white opacity. Differences between restaurants should be highlighted with a subtle `accent-blue` text glow.

### Feedback Buttons
Thumbs up/down icons.
- **Unselected:** Thin stroke, no fill.
- **Selected:** Solid fill with an outer glow (Primary for up, Secondary for down).
- **Animation:** A subtle haptic-like "pop" scale effect (1.1x) when clicked.

### Inputs & Form Controls
Inputs use a "Ghost" style: no fill, 1px white (7% opacity) border. On focus, the border transitions to `primary_color` and adds a subtle 10px outer glow of the same color.