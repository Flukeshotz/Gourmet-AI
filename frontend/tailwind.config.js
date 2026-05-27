/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class", '[data-theme="dark"]'],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // All colors reference CSS variables as RGB triples for opacity modifier support
        "background":                  "rgb(var(--color-background) / <alpha-value>)",
        "surface":                     "rgb(var(--color-surface) / <alpha-value>)",
        "surface-dim":                 "rgb(var(--color-surface-dim) / <alpha-value>)",
        "surface-bright":              "rgb(var(--color-surface-bright) / <alpha-value>)",
        "surface-container-lowest":    "rgb(var(--color-surface-container-lowest) / <alpha-value>)",
        "surface-container-low":       "rgb(var(--color-surface-container-low) / <alpha-value>)",
        "surface-container":           "rgb(var(--color-surface-container) / <alpha-value>)",
        "surface-container-high":      "rgb(var(--color-surface-container-high) / <alpha-value>)",
        "surface-container-highest":   "rgb(var(--color-surface-container-highest) / <alpha-value>)",
        "surface-variant":             "rgb(var(--color-surface-variant) / <alpha-value>)",
        "surface-tint":                "rgb(var(--color-surface-tint) / <alpha-value>)",

        "on-background":               "rgb(var(--color-on-background) / <alpha-value>)",
        "on-surface":                  "rgb(var(--color-on-surface) / <alpha-value>)",
        "on-surface-variant":          "rgb(var(--color-on-surface-variant) / <alpha-value>)",

        "primary":                     "rgb(var(--color-primary) / <alpha-value>)",
        "on-primary":                  "rgb(var(--color-on-primary) / <alpha-value>)",
        "primary-container":           "rgb(var(--color-primary-container) / <alpha-value>)",
        "on-primary-container":        "rgb(var(--color-on-primary-container) / <alpha-value>)",
        "primary-fixed":               "rgb(var(--color-primary-fixed) / <alpha-value>)",
        "primary-fixed-dim":           "rgb(var(--color-primary-fixed-dim) / <alpha-value>)",
        "on-primary-fixed":            "rgb(var(--color-on-primary-fixed) / <alpha-value>)",
        "on-primary-fixed-variant":    "rgb(var(--color-on-primary-fixed-variant) / <alpha-value>)",
        "inverse-primary":             "rgb(var(--color-inverse-primary) / <alpha-value>)",

        "secondary":                   "rgb(var(--color-secondary) / <alpha-value>)",
        "on-secondary":                "rgb(var(--color-on-secondary) / <alpha-value>)",
        "secondary-container":         "rgb(var(--color-secondary-container) / <alpha-value>)",
        "on-secondary-container":      "rgb(var(--color-on-secondary-container) / <alpha-value>)",
        "secondary-fixed":             "rgb(var(--color-secondary-fixed) / <alpha-value>)",
        "secondary-fixed-dim":         "rgb(var(--color-secondary-fixed-dim) / <alpha-value>)",
        "on-secondary-fixed":          "rgb(var(--color-on-secondary-fixed) / <alpha-value>)",
        "on-secondary-fixed-variant":  "rgb(var(--color-on-secondary-fixed-variant) / <alpha-value>)",

        "tertiary":                    "rgb(var(--color-tertiary) / <alpha-value>)",
        "on-tertiary":                 "rgb(var(--color-on-tertiary) / <alpha-value>)",
        "tertiary-container":          "rgb(var(--color-tertiary-container) / <alpha-value>)",
        "on-tertiary-container":       "rgb(var(--color-on-tertiary-container) / <alpha-value>)",
        "tertiary-fixed":              "rgb(var(--color-tertiary-fixed) / <alpha-value>)",
        "tertiary-fixed-dim":          "rgb(var(--color-tertiary-fixed-dim) / <alpha-value>)",
        "on-tertiary-fixed":           "rgb(var(--color-on-tertiary-fixed) / <alpha-value>)",
        "on-tertiary-fixed-variant":   "rgb(var(--color-on-tertiary-fixed-variant) / <alpha-value>)",

        "error":                       "rgb(var(--color-error) / <alpha-value>)",
        "on-error":                    "rgb(var(--color-on-error) / <alpha-value>)",
        "error-container":             "rgb(var(--color-error-container) / <alpha-value>)",
        "on-error-container":          "rgb(var(--color-on-error-container) / <alpha-value>)",

        "outline":                     "rgb(var(--color-outline) / <alpha-value>)",
        "outline-variant":             "rgb(var(--color-outline-variant) / <alpha-value>)",
        "inverse-surface":             "rgb(var(--color-inverse-surface) / <alpha-value>)",
        "inverse-on-surface":          "rgb(var(--color-inverse-on-surface) / <alpha-value>)",
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      spacing: {
        "gutter": "24px",
        "sidebar-width": "280px",
        "stack-lg": "32px",
        "stack-md": "16px",
        "unit": "4px",
        "container-padding": "32px",
        "stack-sm": "8px"
      },
      fontFamily: {
        "headline-card": ["Plus Jakarta Sans"],
        "label-caps": ["Plus Jakarta Sans"],
        "display-hero": ["Plus Jakarta Sans"],
        "status-telemetry": ["Inter"],
        "body-main": ["Plus Jakarta Sans"],
        "display-hero-mobile": ["Plus Jakarta Sans"]
      },
      fontSize: {
        "headline-card": ["20px", {"lineHeight": "1.4", "letterSpacing": "-0.01em", "fontWeight": "700"}],
        "label-caps": ["12px", {"lineHeight": "1.0", "letterSpacing": "0.1em", "fontWeight": "600"}],
        "display-hero": ["48px", {"lineHeight": "1.1", "letterSpacing": "-0.04em", "fontWeight": "800"}],
        "status-telemetry": ["11px", {"lineHeight": "1.0", "letterSpacing": "0.05em", "fontWeight": "500"}],
        "body-main": ["16px", {"lineHeight": "1.6", "letterSpacing": "0em", "fontWeight": "400"}],
        "display-hero-mobile": ["32px", {"lineHeight": "1.2", "letterSpacing": "-0.02em", "fontWeight": "800"}]
      }
    }
  },
  plugins: [],
}
