#!/usr/bin/env python3
# LADESTUFE 3 — RESSOURCE | KATEGORIE: Frontend / CSS-Framework / Design-System
# Quellcode belastet das Kontextfenster nicht. Nur stdout (Ergebnis) wird
# dem Modell zurückgegeben. Ausführung in Sandbox auf expliziten Nutzerruf.
#
# BESCHREIBUNG: Design-System-Generator mit Anti-Generisch-KI-Ästhetik.
#               Erzeugt tailwind.config.js, CSS Custom Properties, HTML-Starter,
#               Button/Card-Komponenten und Mikrointeraktions-CSS nach dem
#               Design-Manifest des shell-scripting-skill.
#
# VERWENDUNG:
#   python ui_design_system.py manifest   [--output stdout|datei]
#   python ui_design_system.py tailwind   [--akzent HEX] [--warm HEX] [--output PATH]
#   python ui_design_system.py css        [--akzent HEX] [--bg HEX] [--output PATH]
#   python ui_design_system.py html       [--titel TEXT] [--akzent HEX] [--output PATH]
#   python ui_design_system.py komponente button|card|input|badge [--output stdout|datei]
#   python ui_design_system.py palette    [--basis HEX] [--output stdout]
#   python ui_design_system.py fonts      [--output stdout]
#   python ui_design_system.py vollstaendig [--projektname NAME] [--verzeichnis PFAD]
#
# VORAUSSETZUNG: Python 3.8+  (keine Abhängigkeiten außer Stdlib)
#
# DESIGN-MANIFEST:
#   Verbotene Schriftarten: Inter, Roboto, DM Sans, Plus Jakarta Sans, Nunito, Poppins
#   Verbotene Patterns: Symmetrische Layouts, Flat-Backgrounds, standard Tailwind-Farben
#   Pflicht: CSS Custom Properties, Gradient Mesh, Noise-Overlay, GPU-Mikrointeraktionen

from __future__ import annotations

import sys
import os
import json
import colorsys
from pathlib import Path
from typing import Any

# =============================================================================
# KONFIGURATION
# =============================================================================

VERBOTENE_FONTS = [
    "Inter", "Roboto", "DM Sans", "Plus Jakarta Sans",
    "Nunito", "Poppins", "Open Sans", "Lato", "Source Sans Pro",
]

EMPFOHLENE_FONTS = {
    "display": [
        ("Clash Display", "https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&display=swap"),
        ("Syne", "https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&display=swap"),
        ("Gambarino", "https://fonts.cdnfonts.com/css/gambarino"),
    ],
    "body": [
        ("Cabinet Grotesk", "https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@400,500,700&display=swap"),
        ("Space Grotesk", "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap"),
        ("Fraunces", "https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,400;0,600;1,400&display=swap"),
    ],
    "mono": [
        ("JetBrains Mono", "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap"),
    ],
}

DEFAULT_PALETTE = {
    "bg_primary":    "#0a0a0f",
    "bg_secondary":  "#12121a",
    "accent_primary":"#7c3aed",
    "accent_warm":   "#f59e0b",
    "text_primary":  "#fafaf9",
    "text_muted":    "#71717a",
    "border_subtle": "rgba(255,255,255,0.08)",
}

ASYMMETRISCHE_SPACING = {
    "4.5": "1.125rem",
    "7.5": "1.875rem",
    "13":  "3.25rem",
    "22":  "5.5rem",
    "33":  "8.25rem",
}

BEZIER_KURVEN = {
    "spring":      "cubic-bezier(0.175, 0.885, 0.32, 1.275)",
    "smooth-out":  "cubic-bezier(0.16, 1, 0.3, 1)",
    "anticipate":  "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
    "ease-back":   "cubic-bezier(0.34, 1.56, 0.64, 1)",
}

# =============================================================================
# UTILITIES
# =============================================================================

def _ts() -> str:
    import datetime
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _log(msg: str) -> None:
    print(f"[{_ts()}] {msg}", file=sys.stderr)

def _err(msg: str, code: int = 1) -> None:
    print(f"ERR | {msg}", file=sys.stderr)
    sys.exit(code)

def _schreiben(inhalt: str, pfad: str | None) -> None:
    if pfad and pfad != "stdout":
        p = Path(pfad)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(inhalt, encoding="utf-8")
        _log(f"Geschrieben: {p}")
    else:
        print(inhalt)

def _hex_zu_rgb(hex_farbe: str) -> tuple[int, int, int]:
    hex_farbe = hex_farbe.lstrip("#")
    if len(hex_farbe) == 3:
        hex_farbe = "".join(c*2 for c in hex_farbe)
    r, g, b = int(hex_farbe[0:2], 16), int(hex_farbe[2:4], 16), int(hex_farbe[4:6], 16)
    return r, g, b

def _rgb_zu_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"

def _farbpalette_generieren(basis_hex: str) -> dict[str, str]:
    """Generiert eine harmonische Farbpalette aus einer Basisfarbe."""
    r, g, b = _hex_zu_rgb(basis_hex)
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

    palette = {}
    # Komplementärfarbe (180° gegenüber)
    h_kompl = (h + 0.5) % 1.0
    r2, g2, b2 = colorsys.hsv_to_rgb(h_kompl, s * 0.7, min(v * 1.2, 1.0))
    palette["komplementaer"] = _rgb_zu_hex(int(r2*255), int(g2*255), int(b2*255))

    # Analoge Farben (±30°)
    h_ana1 = (h + 0.083) % 1.0
    r3, g3, b3 = colorsys.hsv_to_rgb(h_ana1, s, v)
    palette["analog_warm"] = _rgb_zu_hex(int(r3*255), int(g3*255), int(b3*255))

    h_ana2 = (h - 0.083) % 1.0
    r4, g4, b4 = colorsys.hsv_to_rgb(h_ana2, s, v)
    palette["analog_kalt"] = _rgb_zu_hex(int(r4*255), int(g4*255), int(b4*255))

    # Helle und dunkle Variante
    r5, g5, b5 = colorsys.hsv_to_rgb(h, s * 0.5, min(v * 1.5, 1.0))
    palette["hell"] = _rgb_zu_hex(int(r5*255), int(g5*255), int(b5*255))

    r6, g6, b6 = colorsys.hsv_to_rgb(h, min(s * 1.2, 1.0), v * 0.4)
    palette["dunkel"] = _rgb_zu_hex(int(r6*255), int(g6*255), int(b6*255))

    palette["basis"] = basis_hex
    return palette

# =============================================================================
# MODUS 1: MANIFEST — Design-Regeln ausgeben
# =============================================================================

def modus_manifest(output: str) -> None:
    manifest = """# DESIGN-MANIFEST — Anti-Generisch-KI-Ästhetik
# Erstellt von ui_design_system.py
# Pflicht: Dieses Manifest MUSS vor jeder UI-Implementierung gelesen werden.

## ❌ VERBOTENE ELEMENTE — niemals einsetzen

### Verbotene Schriftarten
""" + "\n".join(f"  - ❌ {f}" for f in VERBOTENE_FONTS) + """

### Verbotene Patterns
  - ❌ Symmetrische 2-Spalten-Grids (grid-cols-2 mit gleichen Spaltenbreiten)
  - ❌ Einheitliches Padding (p-4 überall ohne Rhythmus-Variation)
  - ❌ Flache Hintergründe (bg-white, bg-gray-100 ohne Textur)
  - ❌ Standard Hover: hover:opacity-70 ohne Bewegung
  - ❌ Direkte Tailwind-Farben (blue-500, gray-200) ohne CSS Custom Properties
  - ❌ Gleichmäßige Abstände zwischen allen Elementen

## ✅ PFLICHT-ELEMENTE — immer umsetzen

### Typografie
  - ✅ Display: Clash Display, Syne, Fraunces, Gambarino
  - ✅ Body: Cabinet Grotesk, Space Grotesk
  - ✅ Mono: JetBrains Mono

### Farbe
  - ✅ CSS Custom Properties für alle Farben (--color-*)
  - ✅ Kein direktes Tailwind-Klassen-Farbchaos in Templates
  - ✅ Farbpalette: Basis + Komplementär + Analog (generiert via palette-Modus)

### Layout
  - ✅ Asymmetrische Grids: 7-5, 3-7, 5-3-4 — kein reines 50/50
  - ✅ Bewusste vertikale Versätze: translate-y-7.5, -translate-y-4.5
  - ✅ Überlappende Elemente mit z-index und negative margin

### Hintergrund
  - ✅ Gradient Mesh: min. 2 radiale Gradienten überlagert
  - ✅ Noise-Overlay: SVG-Turbulenz-Filter, opacity 4-8%, mix-blend-mode overlay
  - ✅ Kein bg-white oder bg-gray-100 ohne weitere Schicht

### Mikrointeraktionen (GPU-konform)
  - ✅ Nur transform und opacity animieren — niemals width/height/top/margin
  - ✅ will-change: transform für alle :hover-Elemente
  - ✅ translate3d(0, 0, 0) für GPU-Layer-Erstellung
  - ✅ Bézier-Kurven: spring, smooth-out, anticipate — kein einfaches ease
  - ✅ Transition-Dauer: 150–350ms (nie länger für Hover-States)

## PRÜFFRAGEN (vor jedem Visuellen Review)
  ? Könnte das auch ein ChatGPT-Prompt ohne Kontext erzeugt haben?  → Wenn ja: überarbeiten
  ? Sind alle Hintergründe flat? → Noise/Mesh hinzufügen
  ? Verwendet es Inter oder Roboto? → Schriftart ersetzen
  ? Sind alle Abstände identisch? → Rhythmus-Variation einbauen
  ? Wirken die Hover-States träge oder unsichtbar? → GPU-Mikrointeraktion ergänzen
"""
    _schreiben(manifest, output)

# =============================================================================
# MODUS 2: TAILWIND CONFIG
# =============================================================================

def modus_tailwind(akzent: str, warm: str, output: str) -> None:
    palette = _farbpalette_generieren(akzent)

    config = f"""/** @type {{import('tailwindcss').Config}} */
// Generiert von ui_design_system.py — {_ts()}
// Design-Manifest: Keine direkten Tailwind-Standard-Farben in Templates verwenden.
// Alle Farben via var(--color-*) CSS Custom Properties referenzieren.

const plugin = require('tailwindcss/plugin')

module.exports = {{
  content: ['./src/**/*.{{html,js,ts,jsx,tsx}}', './components/**/*.{{js,ts,jsx,tsx}}'],
  theme: {{
    extend: {{
      // Marken-Farbpalette — ersetzt direkte Tailwind-Farben in Komponenten
      colors: {{
        brand: {{
          bg:       'var(--color-bg-primary)',
          surface:  'var(--color-bg-secondary)',
          accent:   'var(--color-accent-primary)',
          warm:     'var(--color-accent-warm)',
          text:     'var(--color-text-primary)',
          muted:    'var(--color-text-muted)',
          border:   'var(--color-border-subtle)',
          kompl:    '{palette["komplementaer"]}',
          analog:   '{palette["analog_warm"]}',
        }},
      }},

      // Asymmetrische Spacing-Skala (kein reines 4px-Grid)
      spacing: {{
{chr(10).join(f"        '{k}': '{v}'," for k, v in ASYMMETRISCHE_SPACING.items())}
      }},

      // Design-Manifest-konforme Schriftarten
      fontFamily: {{
        display: ['Clash Display', 'Syne', 'system-ui', 'sans-serif'],
        body:    ['Cabinet Grotesk', 'Space Grotesk', 'system-ui', 'sans-serif'],
        mono:    ['JetBrains Mono', 'Fira Code', 'Menlo', 'monospace'],
      }},

      // Bézier-Kurven für Mikrointeraktionen
      transitionTimingFunction: {{
{chr(10).join(f"        '{k}': '{v}'," for k, v in BEZIER_KURVEN.items())}
      }},

      // Asymmetrische Grid-Layouts — niemals reines grid-cols-2 für Haupt-Layout
      gridTemplateColumns: {{
        '7-5':    '7fr 5fr',
        '3-7':    '3fr 7fr',
        '5-3-4':  '5fr 3fr 4fr',
        '2-1':    '2fr 1fr',
        '1-2':    '1fr 2fr',
      }},

      // Keyframe-Animationen für Mikrointeraktionen
      keyframes: {{
        shimmer: {{
          '0%':   {{ backgroundPosition: '-200% 0' }},
          '100%': {{ backgroundPosition: '200% 0' }},
        }},
        'fade-up': {{
          '0%':   {{ opacity: '0', transform: 'translateY(16px)' }},
          '100%': {{ opacity: '1', transform: 'translateY(0)' }},
        }},
        shake: {{
          '0%, 100%': {{ transform: 'translateX(0)' }},
          '20%, 60%': {{ transform: 'translateX(-4px)' }},
          '40%, 80%': {{ transform: 'translateX(4px)' }},
        }},
        'scale-in': {{
          '0%':   {{ opacity: '0', transform: 'scale(0.92)' }},
          '100%': {{ opacity: '1', transform: 'scale(1)' }},
        }},
      }},
      animation: {{
        shimmer:   'shimmer 1.5s infinite linear',
        'fade-up': 'fade-up 0.4s ease-smooth-out both',
        shake:     'shake 0.3s ease-in-out',
        'scale-in':'scale-in 0.2s ease-smooth-out both',
      }},
    }},
  }},

  plugins: [
    // Mesh-Hintergrund und Noise-Overlay als Utility-Klassen
    plugin(({{ addUtilities }}) => {{
      addUtilities({{
        '.bg-mesh': {{
          backgroundImage: [
            'radial-gradient(ellipse 60% 50% at 10% 15%, rgba(124,58,237,0.35) 0%, transparent 70%)',
            'radial-gradient(ellipse 55% 45% at 90% 85%, rgba(245,158,11,0.20) 0%, transparent 65%)',
            'linear-gradient(135deg, rgba(12,12,20,0.8) 0%, rgba(18,18,30,1) 100%)',
          ].join(', '),
        }},
        '.noise': {{
          position: 'relative',
          isolation: 'isolate',
        }},
        '.noise::after': {{
          content: "''",
          position: 'absolute',
          inset: '0',
          backgroundImage: "url(\\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E\\")",
          backgroundRepeat: 'repeat',
          backgroundSize: '256px 256px',
          pointerEvents: 'none',
          mixBlendMode: 'overlay',
          opacity: '0.6',
          zIndex: '0',
        }},
        '.gpu': {{
          transform: 'translate3d(0, 0, 0)',
          backfaceVisibility: 'hidden',
          willChange: 'transform',
        }},
      }})
    }}),
  ],
}}
"""
    _schreiben(config, output)

# =============================================================================
# MODUS 3: CSS CUSTOM PROPERTIES
# =============================================================================

def modus_css(akzent: str, bg: str, output: str) -> None:
    palette = _farbpalette_generieren(akzent)
    r, g, b = _hex_zu_rgb(akzent)

    css = f"""/* =============================================================================
   CSS CUSTOM PROPERTIES — Design-System
   Generiert von ui_design_system.py — {_ts()}
   Basis-Akzent: {akzent}  |  Hintergrund: {bg}
   Komplementärfarbe: {palette['komplementaer']}
   ============================================================================= */

:root {{
  /* ---- Farbpalette ---- */
  --color-bg-primary:      {bg};
  --color-bg-secondary:    {palette['dunkel']};
  --color-bg-elevated:     rgba(255,255,255,0.04);

  --color-accent-primary:  {akzent};
  --color-accent-warm:     {palette['analog_warm']};
  --color-accent-kompl:    {palette['komplementaer']};
  --color-accent-muted:    {akzent}66;   /* 40% Opacity */

  --color-text-primary:    #fafaf9;
  --color-text-secondary:  #d4d4d8;
  --color-text-muted:      #71717a;
  --color-text-disabled:   #3f3f46;

  --color-border-subtle:   rgba(255,255,255,0.08);
  --color-border-default:  rgba(255,255,255,0.14);
  --color-border-strong:   rgba(255,255,255,0.22);

  /* ---- Asymmetrisches Spacing (kein reines 4px-Grid) ---- */
  --space-1:    0.25rem;   /*  4px */
  --space-xs:   0.375rem;  /*  6px */
  --space-2:    0.5rem;    /*  8px */
  --space-sm:   0.625rem;  /* 10px */
  --space-3:    0.75rem;   /* 12px */
  --space-4:    1rem;      /* 16px */
  --space-md:   1.125rem;  /* 18px */
  --space-5:    1.25rem;   /* 20px */
  --space-6:    1.5rem;    /* 24px */
  --space-lg:   1.875rem;  /* 30px */
  --space-8:    2rem;      /* 32px */
  --space-xl:   3.25rem;   /* 52px */
  --space-2xl:  5.5rem;    /* 88px */
  --space-3xl:  8.25rem;   /* 132px */

  /* ---- Typografie ---- */
  --font-display: 'Clash Display', 'Syne', system-ui, sans-serif;
  --font-body:    'Cabinet Grotesk', 'Space Grotesk', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', monospace;

  --text-xs:   0.75rem;   /* 12px */
  --text-sm:   0.875rem;  /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.125rem;  /* 18px */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px */
  --text-3xl:  1.875rem;  /* 30px */
  --text-4xl:  2.25rem;   /* 36px */
  --text-5xl:  3rem;      /* 48px */
  --text-6xl:  3.75rem;   /* 60px */
  --text-display: clamp(3rem, 8vw, 6rem);  /* Fluid Display-Größe */

  --leading-tight:  1.2;
  --leading-snug:   1.35;
  --leading-normal: 1.6;
  --leading-loose:  1.8;

  /* ---- Border Radius ---- */
  --radius-none: 0;
  --radius-sm:   2px;   /* Fast eckig — kein Standard-rounded */
  --radius-md:   4px;
  --radius-lg:   8px;
  --radius-xl:   12px;
  --radius-full: 9999px;

  /* ---- Shadows (mit Akzentfarbe) ---- */
  --shadow-sm:    0 2px 8px rgba(0,0,0,0.2);
  --shadow-md:    0 4px 20px rgba(0,0,0,0.3);
  --shadow-lg:    0 8px 40px rgba(0,0,0,0.4);
  --shadow-glow:  0 0 30px {akzent}4d;   /* Akzentfarbe-Glow, 30% */
  --shadow-warm:  0 8px 30px {palette['analog_warm']}33;

  /* ---- Bézier-Kurven für Transitions ---- */
  --ease-spring:     cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-smooth-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-anticipate: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-back:       cubic-bezier(0.34, 1.56, 0.64, 1);

  /* ---- Transition-Dauern ---- */
  --duration-fast:   150ms;
  --duration-base:   200ms;
  --duration-slow:   350ms;
  --duration-xslow:  500ms;

  /* ---- Z-Index-Skala ---- */
  --z-below:   -1;
  --z-base:     0;
  --z-raised:   10;
  --z-dropdown: 100;
  --z-sticky:   200;
  --z-modal:    300;
  --z-toast:    400;
  --z-tooltip:  500;
}}

/* =============================================================================
   GRADIENT MESH — Hintergrundtextur
   ============================================================================= */

.bg-mesh {{
  background-color: var(--color-bg-primary);
  background-image:
    radial-gradient(ellipse 60% 50% at 10% 15%, {akzent}59 0%, transparent 70%),
    radial-gradient(ellipse 55% 45% at 90% 85%, {palette['analog_warm']}33 0%, transparent 65%),
    radial-gradient(ellipse 40% 35% at 50% 50%, {palette['komplementaer']}1a 0%, transparent 60%),
    linear-gradient(135deg, rgba(12,12,20,0.8) 0%, rgba(18,18,30,1) 100%);
}}

/* =============================================================================
   NOISE OVERLAY — organische Textur
   ============================================================================= */

.noise {{
  position: relative;
  isolation: isolate;
}}

.noise::after {{
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px 256px;
  pointer-events: none;
  mix-blend-mode: overlay;
  opacity: 0.6;
  z-index: 0;
}}

/* =============================================================================
   GPU-MIKROINTERAKTIONEN — Basis-Klassen
   ============================================================================= */

/* Pflicht-Basis für alle interaktiven Elemente */
.gpu {{
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
  will-change: transform;
}}

/* Karten-Hover: Elevation + subtile Rotation */
.card-interactive {{
  transform: translate3d(0, 0, 0);
  transition:
    transform var(--duration-slow) var(--ease-smooth-out),
    box-shadow var(--duration-slow) var(--ease-smooth-out);
  will-change: transform;
}}
.card-interactive:hover {{
  transform: translate3d(0, -4px, 0) rotate(-0.3deg);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}}

/* Link-Underline: Slide-In */
.link-fancy {{
  position: relative;
  text-decoration: none;
}}
.link-fancy::after {{
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 1px;
  background: var(--color-accent-primary);
  transform: scaleX(0);
  transform-origin: right;
  transition: transform var(--duration-base) var(--ease-smooth-out);
}}
.link-fancy:hover::after {{
  transform: scaleX(1);
  transform-origin: left;
}}

/* Icon-Mikrointeraktion */
.icon-bounce:hover {{
  transform: rotate(12deg) scale(1.15);
  transition: transform var(--duration-slow) var(--ease-spring);
}}

/* Focus-Ring (a11y-konform, nicht generisch) */
:focus-visible {{
  outline: 2px solid var(--color-accent-primary);
  outline-offset: 3px;
  border-radius: var(--radius-sm);
}}
"""
    _schreiben(css, output)

# =============================================================================
# MODUS 4: HTML STARTER
# =============================================================================

def modus_html(titel: str, akzent: str, output: str) -> None:
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titel}</title>
  <!-- Design-Manifest: Keine Inter/Roboto. Clash Display + Cabinet Grotesk. -->
  <link rel="preconnect" href="https://api.fontshare.com">
  <link href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=cabinet-grotesk@400,500,700&display=swap" rel="stylesheet">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    // Tailwind-Konfiguration inline (Produktion: tailwind.config.js verwenden)
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            display: ['Clash Display', 'system-ui'],
            body:    ['Cabinet Grotesk', 'system-ui'],
            mono:    ['JetBrains Mono', 'monospace'],
          }},
          transitionTimingFunction: {{
            'spring':     'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
            'smooth-out': 'cubic-bezier(0.16, 1, 0.3, 1)',
          }},
        }},
      }},
    }}
  </script>
  <style>
    /* CSS Custom Properties (vollständig: python ui_design_system.py css) */
    :root {{
      --color-bg-primary:     #0a0a0f;
      --color-bg-secondary:   #12121a;
      --color-accent-primary: {akzent};
      --color-accent-warm:    #f59e0b;
      --color-text-primary:   #fafaf9;
      --color-text-muted:     #71717a;
      --color-border-subtle:  rgba(255,255,255,0.08);
      --ease-smooth-out:      cubic-bezier(0.16, 1, 0.3, 1);
      --ease-spring:          cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    body {{
      background-color: var(--color-bg-primary);
      color: var(--color-text-primary);
      font-family: 'Cabinet Grotesk', system-ui, sans-serif;
    }}
    .bg-mesh {{
      background-image:
        radial-gradient(ellipse 60% 50% at 10% 15%, {akzent}59 0%, transparent 70%),
        radial-gradient(ellipse 55% 45% at 90% 85%, rgba(245,158,11,0.20) 0%, transparent 65%);
    }}
    .noise {{ position: relative; isolation: isolate; }}
    .noise::after {{
      content: '';
      position: absolute;
      inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
      background-size: 256px;
      pointer-events: none;
      mix-blend-mode: overlay;
      opacity: .6;
    }}
    .card-interactive {{
      transition: transform 350ms var(--ease-smooth-out), box-shadow 350ms var(--ease-smooth-out);
      will-change: transform;
    }}
    .card-interactive:hover {{
      transform: translate3d(0, -4px, 0) rotate(-0.3deg);
      box-shadow: 0 12px 40px rgba(0,0,0,.4), 0 4px 12px {akzent}33;
    }}
  </style>
</head>
<body class="min-h-screen bg-mesh noise">

  <!-- Hero — asymmetrisches Layout -->
  <section class="min-h-screen flex items-center px-13 max-lg:px-6">
    <div class="w-full grid" style="grid-template-columns: 7fr 5fr; gap: 3.25rem;">

      <!-- Links: Haupt-Content, leicht nach unten versetzt -->
      <div class="translate-y-7 max-lg:translate-y-0">
        <p class="font-mono text-sm tracking-widest uppercase mb-6"
           style="color: var(--color-accent-primary);">
          Design-System-Starter
        </p>
        <h1 class="font-display font-bold leading-tight mb-7"
            style="font-size: var(--text-display, clamp(3rem,8vw,6rem));">
          {titel}
        </h1>
        <p class="text-xl leading-loose max-w-xl mb-13"
           style="color: var(--color-text-muted);">
          Kein Inter. Kein Roboto. Kein generisches KI-Layout.
          Asymmetrisch, texturiert, eigenwillig.
        </p>
        <div class="flex gap-6 flex-wrap">
          <button class="card-interactive px-9 py-4 rounded-sm font-body font-medium text-white"
                  style="background: linear-gradient(135deg, {akzent}, {akzent}cc);">
            Primär-Button
          </button>
          <button class="card-interactive px-8 py-4 rounded-sm font-body font-medium"
                  style="border: 1px solid var(--color-border-default); color: var(--color-text-primary);">
            Ghost-Button
          </button>
        </div>
      </div>

      <!-- Rechts: Visuelle Karte, nach oben versetzt -->
      <div class="-translate-y-7 max-lg:translate-y-0 max-lg:hidden">
        <div class="card-interactive rounded-lg p-7"
             style="background: var(--color-bg-secondary); border: 1px solid var(--color-border-subtle);">
          <p class="font-mono text-xs mb-4" style="color: var(--color-text-muted);">
            design-manifest.json
          </p>
          <pre class="font-mono text-sm leading-loose" style="color: var(--color-accent-primary);">
{{
  "fonts": ["Clash Display", "Cabinet Grotesk"],
  "verboten": ["Inter", "Roboto"],
  "layout": "asymmetrisch",
  "textur": "gradient-mesh + noise",
  "mikrointeraktionen": "GPU-only"
}}</pre>
        </div>
      </div>

    </div>
  </section>

</body>
</html>
"""
    _schreiben(html, output)

# =============================================================================
# MODUS 5: KOMPONENTEN
# =============================================================================

KOMPONENTEN: dict[str, str] = {
    "button": """/* KOMPONENTE: Button — Design-Manifest-konform
   Generiert von ui_design_system.py */

/* Basis-Reset */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-body, 'Cabinet Grotesk', system-ui);
  font-weight: 500;
  cursor: pointer;
  border: none;
  text-decoration: none;
  /* GPU-Layer */
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
  will-change: transform;
  /* Transition: nur transform + opacity + shadow */
  transition:
    transform    200ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow   200ms cubic-bezier(0.16, 1, 0.3, 1),
    opacity      150ms linear;
}

/* Varianten */
.btn-primary {
  padding: 0.875rem 2.25rem;
  background: linear-gradient(135deg, var(--color-accent-primary), var(--color-accent-primary)cc);
  color: #fff;
  border-radius: 3px;   /* Fast eckig — bewusste Entscheidung */
}
.btn-primary:hover {
  transform: translate3d(0, -2px, 0) scale(1.02);
  box-shadow: 0 8px 30px var(--color-accent-muted, rgba(124,58,237,0.4));
}
.btn-primary:active {
  transform: translate3d(0, 0, 0) scale(0.98);
  box-shadow: none;
}

.btn-ghost {
  padding: 0.875rem 2rem;
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-default);
  border-radius: 3px;
}
.btn-ghost:hover {
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  background: var(--color-accent-muted, rgba(124,58,237,0.05));
  transform: translate3d(0, -1px, 0);
}

/* Größen */
.btn-sm  { padding: 0.5rem 1rem;    font-size: 0.875rem; }
.btn-lg  { padding: 1.125rem 2.75rem; font-size: 1.125rem; }
.btn-icon { width: 2.75rem; height: 2.75rem; padding: 0; border-radius: 3px; }
""",

    "card": """/* KOMPONENTE: Card — Design-Manifest-konform
   Generiert von ui_design_system.py */

.card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-subtle);
  border-radius: 6px;
  padding: var(--space-lg, 1.875rem);
  position: relative;
  isolation: isolate;
  /* GPU */
  transform: translate3d(0, 0, 0);
  will-change: transform;
  transition:
    transform    350ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow   350ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 250ms ease;
}

/* Noise-Textur auf Karte */
.card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  mix-blend-mode: overlay;
  opacity: 0.4;
  z-index: 0;
}

.card > * { position: relative; z-index: 1; }

/* Interaktive Variante */
.card-interactive {
  cursor: pointer;
}
.card-interactive:hover {
  transform: translate3d(0, -4px, 0) rotate(-0.25deg);
  box-shadow:
    0 12px 40px rgba(0,0,0,0.35),
    0 4px 12px var(--color-accent-muted, rgba(124,58,237,0.2));
  border-color: var(--color-border-default);
}

/* Akzent-Variante (linker Balken) */
.card-accented {
  border-left: 2px solid var(--color-accent-primary);
  border-left-width: 2px;
}
""",

    "input": """/* KOMPONENTE: Input — Design-Manifest-konform
   Generiert von ui_design_system.py */

.input {
  width: 100%;
  padding: 0.875rem 1.125rem;
  background: var(--color-bg-elevated, rgba(255,255,255,0.04));
  border: 1px solid var(--color-border-subtle);
  border-radius: 3px;
  color: var(--color-text-primary);
  font-family: var(--font-body, system-ui);
  font-size: 1rem;
  outline: none;
  transition:
    border-color 150ms ease,
    box-shadow   150ms ease,
    background   150ms ease;
}

.input::placeholder { color: var(--color-text-muted); }

.input:hover {
  border-color: var(--color-border-default);
  background: rgba(255,255,255,0.06);
}

.input:focus {
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 3px var(--color-accent-muted, rgba(124,58,237,0.15));
  background: rgba(255,255,255,0.06);
}

.input-error { border-color: #ef4444; }
.input-error:focus { box-shadow: 0 0 0 3px rgba(239,68,68,0.15); }
""",

    "badge": """/* KOMPONENTE: Badge — Design-Manifest-konform
   Generiert von ui_design_system.py */

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  font-family: var(--font-mono, monospace);
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-radius: 2px;   /* Bewusst fast eckig */
  border: 1px solid transparent;
}

.badge-default {
  background: var(--color-bg-elevated, rgba(255,255,255,0.06));
  color: var(--color-text-muted);
  border-color: var(--color-border-subtle);
}

.badge-accent {
  background: var(--color-accent-muted, rgba(124,58,237,0.15));
  color: var(--color-accent-primary);
  border-color: var(--color-accent-primary)33;
}

.badge-warm {
  background: rgba(245,158,11,0.12);
  color: #f59e0b;
  border-color: rgba(245,158,11,0.25);
}

.badge-success {
  background: rgba(34,197,94,0.12);
  color: #22c55e;
  border-color: rgba(34,197,94,0.25);
}

.badge-error {
  background: rgba(239,68,68,0.12);
  color: #ef4444;
  border-color: rgba(239,68,68,0.25);
}
""",
}

def modus_komponente(typ: str, output: str) -> None:
    if typ not in KOMPONENTEN:
        _err(f"Unbekannte Komponente: {typ}\nErlaubt: {', '.join(KOMPONENTEN)}")
    _schreiben(KOMPONENTEN[typ], output)

# =============================================================================
# MODUS 6: PALETTE
# =============================================================================

def modus_palette(basis: str, output: str) -> None:
    palette = _farbpalette_generieren(basis)
    _schreiben(json.dumps({
        "basis": basis,
        "palette": palette,
        "css_vars": {
            f"--color-{k.replace('_', '-')}": v
            for k, v in palette.items()
        },
        "tailwind": {
            f"brand-{k.replace('_', '-')}": v
            for k, v in palette.items()
        },
        "hinweis": (
            "Alle Farben in :root als CSS Custom Properties einbinden. "
            "Tailwind-Klassen nur als Wrapper (brand.*) — nie direkte "
            "blue-500 o.ä. Klassen im Template."
        ),
    }, ensure_ascii=False, indent=2), output)

# =============================================================================
# MODUS 7: FONTS
# =============================================================================

def modus_fonts(output: str) -> None:
    ergebnis = {
        "verboten": VERBOTENE_FONTS,
        "empfohlen": EMPFOHLENE_FONTS,
        "css_font_face_vorlage": (
            "@font-face {\n"
            "  font-family: 'Clash Display';\n"
            "  src: url('/fonts/ClashDisplay-Variable.woff2') format('woff2');\n"
            "  font-weight: 100 900;\n"
            "  font-style: normal;\n"
            "  font-display: swap;\n"
            "}"
        ),
        "hinweis": (
            "In Produktion: woff2-Dateien lokal hosten, kein externes CDN. "
            "font-display: swap verhindert unsichtbaren Text (FOIT). "
            "Variable Fonts (Clash Display Variable) reduzieren HTTP-Requests."
        ),
    }
    _schreiben(json.dumps(ergebnis, ensure_ascii=False, indent=2), output)

# =============================================================================
# MODUS 8: VOLLSTÄNDIG — alle Dateien in ein Verzeichnis schreiben
# =============================================================================

def modus_vollstaendig(projektname: str, verzeichnis: str, akzent: str) -> None:
    basisdir = Path(verzeichnis)
    basisdir.mkdir(parents=True, exist_ok=True)

    dateien = {
        "tailwind.config.js":       lambda: modus_tailwind(akzent, "#f59e0b", str(basisdir / "tailwind.config.js")),
        "styles/design-tokens.css": lambda: modus_css(akzent, "#0a0a0f", str(basisdir / "styles" / "design-tokens.css")),
        "index.html":               lambda: modus_html(projektname, akzent, str(basisdir / "index.html")),
        "styles/button.css":        lambda: modus_komponente("button", str(basisdir / "styles" / "button.css")),
        "styles/card.css":          lambda: modus_komponente("card", str(basisdir / "styles" / "card.css")),
        "styles/input.css":         lambda: modus_komponente("input", str(basisdir / "styles" / "input.css")),
        "styles/badge.css":         lambda: modus_komponente("badge", str(basisdir / "styles" / "badge.css")),
        "DESIGN-MANIFEST.md":       lambda: modus_manifest(str(basisdir / "DESIGN-MANIFEST.md")),
    }

    for name, fn in dateien.items():
        fn()

    _log(f"Design-System vollständig generiert: {basisdir}")
    print(json.dumps({
        "status": "ok",
        "projektname": projektname,
        "verzeichnis": str(basisdir),
        "dateien": list(dateien.keys()),
        "akzentfarbe": akzent,
        "naechste_schritte": [
            "1. DESIGN-MANIFEST.md lesen — Regeln verinnerlichen",
            "2. Schriftarten aus fonts-Modus in /fonts/ ablegen",
            "3. tailwind.config.js in Build-Prozess einbinden",
            "4. styles/design-tokens.css als erste Zeile importieren",
            "5. Komponenten aus styles/*.css nach Bedarf einbinden",
        ],
    }, ensure_ascii=False, indent=2))

# =============================================================================
# HILFE
# =============================================================================

HILFE = """
VERWENDUNG:
  python ui_design_system.py manifest   [--output stdout|PFAD]
  python ui_design_system.py tailwind   [--akzent HEX] [--warm HEX] [--output PFAD]
  python ui_design_system.py css        [--akzent HEX] [--bg HEX] [--output PFAD]
  python ui_design_system.py html       [--titel TEXT] [--akzent HEX] [--output PFAD]
  python ui_design_system.py komponente button|card|input|badge [--output stdout|PFAD]
  python ui_design_system.py palette    [--basis HEX] [--output stdout]
  python ui_design_system.py fonts      [--output stdout]
  python ui_design_system.py vollstaendig [--projektname NAME] [--verzeichnis PFAD] [--akzent HEX]

DEFAULTS:
  --akzent    #7c3aed   (Violett — Basis-Akzentfarbe)
  --warm      #f59e0b   (Amber — Komplementär-Warm-Akzent)
  --bg        #0a0a0f   (Fast-Schwarz — Hintergrund)
  --output    stdout
  --projektname   Mein Projekt
  --verzeichnis   ./design-system

DESIGN-MANIFEST (Kurzfassung):
  VERBOTEN: Inter, Roboto, DM Sans, Plus Jakarta Sans, Nunito, Poppins
  VERBOTEN: Symmetrische Layouts, Flat-Backgrounds, direkte Tailwind-Farben
  PFLICHT:  CSS Custom Properties, Gradient Mesh, Noise-Overlay
  PFLICHT:  Hardware-beschleunigte Mikrointeraktionen (nur transform/opacity)
  PFLICHT:  Asymmetrische Grids (7-5, 3-7), bewusste Rhythmus-Brüche

BEISPIELE:
  # Design-Manifest ausgeben
  python ui_design_system.py manifest

  # Tailwind-Config mit eigenem Akzent
  python ui_design_system.py tailwind --akzent "#e11d48" --output tailwind.config.js

  # CSS Custom Properties generieren
  python ui_design_system.py css --akzent "#0ea5e9" --bg "#030712" --output styles/tokens.css

  # HTML-Starter mit eigenem Titel
  python ui_design_system.py html --titel "Mein Produkt" --akzent "#8b5cf6" --output index.html

  # Button-Komponente ausgeben
  python ui_design_system.py komponente button --output styles/button.css

  # Farbpalette aus Basisfarbe generieren
  python ui_design_system.py palette --basis "#e11d48"

  # Vollständiges Design-System in ./mein-projekt/ erzeugen
  python ui_design_system.py vollstaendig --projektname "StartupX" \\
    --verzeichnis ./startupx-design --akzent "#7c3aed"
"""

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HILFE); sys.exit(0)

    args = sys.argv[1:]

    def _opt(name: str, default: str) -> str:
        for i, a in enumerate(args):
            if a == name and i + 1 < len(args):
                return args[i + 1]
        return default

    modus = args[0]
    output  = _opt("--output",     "stdout")
    akzent  = _opt("--akzent",     "#7c3aed")
    warm    = _opt("--warm",       "#f59e0b")
    bg      = _opt("--bg",         "#0a0a0f")
    titel   = _opt("--titel",      "Mein Projekt")
    basis   = _opt("--basis",      "#7c3aed")
    projekt = _opt("--projektname","Mein Projekt")
    verz    = _opt("--verzeichnis","./design-system")

    if modus == "manifest":
        modus_manifest(output)
    elif modus == "tailwind":
        modus_tailwind(akzent, warm, output)
    elif modus == "css":
        modus_css(akzent, bg, output)
    elif modus == "html":
        modus_html(titel, akzent, output)
    elif modus == "komponente":
        typ = args[1] if len(args) > 1 and not args[1].startswith("--") else ""
        if not typ:
            _err("VERWENDUNG: komponente button|card|input|badge")
        modus_komponente(typ, output)
    elif modus == "palette":
        modus_palette(basis, output)
    elif modus == "fonts":
        modus_fonts(output)
    elif modus == "vollstaendig":
        modus_vollstaendig(projekt, verz, akzent)
    else:
        print(f"ERR | Unbekannter Modus: '{modus}'\n{HILFE}", file=sys.stderr)
        sys.exit(1)
