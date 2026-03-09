---
# LADESTUFE 1 — METADATEN
# Wird initial beim Start der Agenten-Session geladen (~100 Token).
# Dient als Trigger-Mechanismus: Das Modell entscheidet hier,
# ob dieser Skill für die aktuelle Aufgabe relevant ist.

name: frontend-skill
description: >
  Tailwind CSS v3/v4 (CSS-First @theme, @import-Migration, gap statt Margin-Hacks),
  shadcn/ui und Radix UI Komponentenbibliotheken,
  Anti-generische-KI-Ästhetik (Design-Manifest: verbotene Fonts, Pflicht-Asymmetrien),
  CSS Custom Properties für kohärente Farbpaletten, hardware-beschleunigte
  Mikrointeraktionen (transform/opacity/will-change), Gradient Meshes, Noise-Overlays,
  Subagenten-Orchestrierung (component-composition-reviewer, design-verification,
  a11y-wcag-compliance-auditor) für WCAG 2.1 AA und Figma-Token-Abgleich.
  Keine Dateien oder Pfade werden ohne ausdrückliche Nutzerfreigabe geöffnet oder verändert.

categories:
  - name: Frontend / CSS-Framework / Design-System
    description: >
      Tailwind CSS v3/v4 (CSS-First @theme, @import-Migration, gap statt Margin-Hacks),
      shadcn/ui und Radix UI Komponentenbibliotheken,
      Anti-generische-KI-Ästhetik (Design-Manifest: verbotene Fonts, Pflicht-Asymmetrien),
      CSS Custom Properties für kohärente Farbpaletten, hardware-beschleunigte
      Mikrointeraktionen (transform/opacity/will-change), Gradient Meshes, Noise-Overlays,
      Subagenten-Orchestrierung (component-composition-reviewer, design-verification,
      a11y-wcag-compliance-auditor) für WCAG 2.1 AA und Figma-Token-Abgleich

triggers:
  # Frontend / CSS-Framework / Design-System / UI/UX
  - Tailwind CSS Utility-First-Komponenten implementieren
  - shadcn/ui oder Radix UI Komponentenbibliothek einrichten und nutzen
  - "Generische KI-Ästhetik" im Frontend vermeiden
  - Design-Manifest mit verbotenen Fonts und Pflicht-Design-Patterns erstellen
  - Inter, Roboto oder andere übernutzte Systemschriftarten durch Alternativen ersetzen
  - Asymmetrische, nicht-uniforme Layouts mit Tailwind CSS bauen
  - Überlappende Elemente (negative margins, z-index, translate) umsetzen
  - Gradient Mesh als Hintergrundtextur implementieren (CSS / SVG)
  - Noise-Overlay für organische Hintergrundtexturen hinzufügen
  - CSS Custom Properties (--color-*, --spacing-*) für kohärente Farbpalette definieren
  - Hardware-beschleunigte Mikrointeraktionen mit transform und opacity umsetzen
  - will-change, translate3d, backface-visibility für GPU-Rendering optimieren
  - Hover-, Focus- und Active-States als feinkörnige Mikrointeraktionen gestalten
  - Komponentensystem aus shadcn/ui-Primitives zusammenbauen
  - UI-Komponenten-Bibliothek (Button, Card, Input, Dialog) konfigurieren
  - Tailwind v4: @tailwind-Direktiven durch @import "tailwindcss" ersetzen
  - Tailwind v4: tailwind.config.js durch @theme-Direktive in CSS migrieren
  - Tailwind v4: Margin-Hacks (mt-/ml- auf Kind) durch gap-Utilities auf Parent ersetzen
  - Dark Mode konsistent via dark:-Klassen implementieren (kein @media-Mix)
  - Subagenten für Frontend: component-composition-reviewer + design-verification + a11y
  - WCAG 2.1 AA: Farbkontrast (4.5:1), ARIA-Attribute, Tastaturnavigation prüfen
  - Figma-Token-Abgleich: Spacing / Farbe / Typografie gegen Design-System verifizieren

resources:
  - resources/ui_design_system.py
  - resources/tabellen.css
---

# LADESTUFE 2 — INSTRUKTIONEN
# Wird on-demand geladen, sobald semantische Übereinstimmung mit den Triggern
# erkannt wird (via `cat SKILL.md` im Hintergrund). Moderat: < 5.000 Token.
# Definiert Prozessschritte, Regeln und Leitplanken — kein vollständiger Code.

## Arbeitsweise (Reihenfolge einhalten)

1. **Anforderung klären** — Zieldatei, Pfad und Umfang mit dem Nutzer bestätigen, bevor irgendetwas geschrieben oder ausgeführt wird.
2. **Ressource auswählen** — Passende Ressource aus `resources/` benennen; der Nutzer entscheidet, ob sie ausgeführt wird.
3. **Dry-Run zuerst** — Destruktive oder schreibende Operationen immer zuerst simulieren (`--dry-run`, `echo`-Modus oder Ausgabe nach stdout).
4. **Freigabe einholen** — Vor jeder Dateiänderung: Zielpfad anzeigen, Bestätigung abwarten.
5. **Ausführen & protokollieren** — Ausgabe (stdout/stderr) dem Nutzer vollständig zeigen.

---

## Ladestufe-Übersicht

| Stufe | Komponente | Zeitpunkt | Token-Belastung | Funktionale Bedeutung |
|---|---|---|---|---|
| 1 | Metadaten (YAML-Frontmatter) | Initial beim Session-Start | ~100 Token | Trigger-Mechanismus: Relevanz-Bewertung durch das Modell |
| 2 | Instruktionen (diese Datei) | On-Demand bei semantischer Übereinstimmung | < 5.000 Token | Prozessschritte, Regeln, Leitplanken |
| 3 | Ressourcen (externe Skripte) | Bei explizitem Aufruf während der Ausführung | Nur stdout wird verrechnet | Skripte laufen in Sandbox; Quellcode belastet Kontextfenster nicht |

---

## CSS-Frameworks, UI/UX-Automatisierung und Frontend-Design-Systeme

Die Frontend-Entwicklung erfordert strikt komponentenbasiertes Design und Utility-First CSS.
Kernaufgabe des Skills: UI-Implementierungen automatisieren und dabei konsequent
**generische KI-Ästhetik** durch programmatische Design-Restriktionen vermeiden.

### Design-Manifest: Anti-Generisch-KI-Ästhetik (Pflicht)

Jedes UI-Projekt beginnt mit einem expliziten Design-Manifest. Es definiert verbotene
Elemente und erzwingt visuelle Differenzierung durch harte Regeln.

**Verbotene Elemente — niemals einsetzen:**

| Element | Verbotene Werte | Erlaubte Alternative |
|---|---|---|
| **Systemschriftarten** | Inter, Roboto, DM Sans, Plus Jakarta Sans | Syne, Fraunces, Space Grotesk, Clash Display, Cabinet Grotesk |
| **Einheitliche Abstände** | `p-4` überall, `gap-4` in jedem Grid | Bewusste Rhythmus-Brüche: `p-3`, `p-7`, `p-12` kombinieren |
| **Flache Hintergründe** | `bg-gray-100`, `bg-white` ohne Textur | Gradient Mesh, Noise-Overlay, radiale Gradienten |
| **Symmetrische Layouts** | Zentrierung überall, gleiche Spaltenbreiten | Asymmetrie: 7/5-Spalten, bewusste Lücken, versetzte Grids |
| **Standard-Hover-States** | `hover:opacity-70` ohne weitere Transition | Mikro-Bewegungen: scale, translate, clip-path-Transitions |
| **Generische Farben** | `blue-500`, `gray-200` als direkte Klassen | CSS Custom Properties: `var(--color-accent-primary)` |

**Pflicht-Design-Elemente — immer umsetzen:**

```css
/* Design-Manifest: Wird in jede CSS/Tailwind-Konfiguration eingebettet */

:root {
  /* Farbpalette via Custom Properties — kein direktes Tailwind-Klassen-Chaos */
  --color-bg-primary:      #0a0a0f;
  --color-bg-secondary:    #12121a;
  --color-accent-primary:  #7c3aed;   /* Nicht "violet-600" — eigene Benennung */
  --color-accent-warm:     #f59e0b;
  --color-text-primary:    #fafaf9;
  --color-text-muted:      #71717a;
  --color-border-subtle:   rgba(255,255,255,0.08);

  /* Bewusste Asymmetrie in Spacing */
  --space-xs:   0.375rem;  /* 6px  — kein Standard-4px-Grid */
  --space-sm:   0.625rem;  /* 10px */
  --space-md:   1.125rem;  /* 18px */
  --space-lg:   1.875rem;  /* 30px */
  --space-xl:   3.25rem;   /* 52px */
  --space-2xl:  5.5rem;    /* 88px */

  /* Typografie-Skala — nicht-uniform */
  --font-display: 'Clash Display', 'Syne', system-ui;
  --font-body:    'Cabinet Grotesk', 'Space Grotesk', system-ui;
  --font-mono:    'JetBrains Mono', 'Fira Code', monospace;
}
```

### Tailwind CSS: Utility-First-Architektur

**Tailwind-Konfiguration für Anti-Generic-Ästhetik (`tailwind.config.js`):**

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          bg:       'var(--color-bg-primary)',
          surface:  'var(--color-bg-secondary)',
          accent:   'var(--color-accent-primary)',
          warm:     'var(--color-accent-warm)',
          text:     'var(--color-text-primary)',
          muted:    'var(--color-text-muted)',
          border:   'var(--color-border-subtle)',
        },
      },
      spacing: {
        '4.5': '1.125rem',
        '7.5': '1.875rem',
        '13':  '3.25rem',
        '22':  '5.5rem',
      },
      fontFamily: {
        display: ['Clash Display', 'Syne', 'system-ui'],
        body:    ['Cabinet Grotesk', 'Space Grotesk', 'system-ui'],
        mono:    ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      transitionTimingFunction: {
        'spring':       'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        'smooth-out':   'cubic-bezier(0.16, 1, 0.3, 1)',
        'anticipate':   'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
      gridTemplateColumns: {
        '7-5':  '7fr 5fr',
        '3-7':  '3fr 7fr',
        '5-3-4':'5fr 3fr 4fr',
      },
    },
  },
}
```

**Layout-Asymmetrie mit Tailwind (Pflicht-Muster):**

```html
<!-- FALSCH: Symmetrisches 2-Spalten-Grid -->
<div class="grid grid-cols-2 gap-4 p-4">...</div>

<!-- RICHTIG: Bewusst asymmetrisch -->
<div class="grid grid-cols-7-5 gap-x-13 gap-y-7 px-13 py-22
            max-lg:grid-cols-1 max-lg:gap-y-13">
  <div class="col-span-1 translate-y-7.5"> <!-- Vertikaler Versatz --> </div>
  <div class="col-span-1 -translate-y-4.5 relative"> <!-- Gegenläufig --> </div>
</div>
```

### shadcn/ui und Radix UI: Komponentenbibliotheken

shadcn/ui und Radix UI bieten zugängliche (a11y-konforme), headless Komponenten-Primitives.
shadcn/ui kopiert Quellcode direkt in das Projekt — kein opaker Abhängigkeitsgraph.

**Setup (Next.js / Vite):**

```bash
# shadcn/ui initialisieren (kopiert Komponenten in ./components/ui/)
npx shadcn@latest init

# Gewünschte Komponenten hinzufügen
npx shadcn@latest add button card dialog input select badge

# Radix UI direkt (für Custom-Primitives ohne shadcn-Wrapper)
npm install @radix-ui/react-dialog @radix-ui/react-popover @radix-ui/react-tooltip
```

### Hintergrundtexturen: Gradient Mesh und Noise-Overlay

Flache Hintergründe sind verboten. Jeder Hintergrund erhält mindestens eine Textur-Schicht.

**Gradient Mesh (CSS):**

```css
.bg-mesh {
  background-color: var(--color-bg-primary);
  background-image:
    radial-gradient(
      ellipse 60% 50% at 10% 15%,
      rgba(124, 58, 237, 0.35) 0%,
      transparent 70%
    ),
    radial-gradient(
      ellipse 55% 45% at 90% 85%,
      rgba(245, 158, 11, 0.20) 0%,
      transparent 65%
    ),
    linear-gradient(
      135deg,
      rgba(12, 12, 20, 0.8) 0%,
      rgba(18, 18, 30, 1) 100%
    );
}

/* Noise-Overlay: organische Textur über jeder Fläche */
.noise-overlay::after {
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
}
```

### Hardware-beschleunigte Mikrointeraktionen

Mikrointeraktionen müssen auf der GPU laufen. Nur `transform` und `opacity` ändern —
niemals `width`, `height`, `top`, `left`, `margin` animieren (triggert Layout-Reflow).

**GPU-konforme CSS-Grundregeln:**

```css
/* Pflicht-Muster für alle interaktiven Elemente */
.interactive {
  will-change: transform, opacity;
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
  transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1),
              opacity   200ms cubic-bezier(0.16, 1, 0.3, 1);
}

.interactive:hover {
  /* Nur transform/opacity — KEIN width/height/top/margin */
  transform: translate3d(0, -2px, 0) scale(1.02);
  opacity: 1;
}
```

**Tailwind-Klassen für GPU-Mikrointeraktionen:**

| Interaktion | Tailwind-Klassen | Anmerkung |
|---|---|---|
| Karten-Hover (Elevation) | `hover:-translate-y-1 hover:shadow-2xl transition-[transform,shadow] duration-200 ease-smooth-out` | `will-change-transform` ergänzen |
| Button-Press-Feedback | `active:scale-[0.97] active:translate-y-[1px]` | Physisches Drück-Gefühl |
| Icon-Bounce | `hover:scale-110 hover:-rotate-3 transition-transform duration-300 ease-spring` | Federnde Bewegung |
| Fade-In-Up (Appearing) | `opacity-0 translate-y-4 → opacity-100 translate-y-0` | Nur mit JS-Toggle oder `@starting-style` |
| Shimmer-Loading | `animate-[shimmer_1.5s_infinite]` | Via Tailwind-Custom-Animation |

### Typografie: Schriftarten-Manifest

**Verbotene Schriftarten (generische KI-Ästhetik):**

```
❌ Inter        — Übernutzt in 90% aller KI-generierten UIs
❌ Roboto       — Google-Standard, uncharakteristisch
❌ DM Sans      — Beliebt aber austauschbar
❌ Plus Jakarta Sans — Verbreitet in Startup-Templates
❌ Nunito       — Kindlich und generisch
❌ Poppins      — Übernutzt, indifferent
```

**Erlaubte und empfohlene Schriftarten:**

| Schriftart | Charakter | Einsatz | Bezug |
|---|---|---|---|
| **Clash Display** | Geometrisch, eigenwillig | Headlines, Display | `fontsource` / CDN |
| **Syne** | Variable, modern-expressiv | Headlines, Akzente | Google Fonts |
| **Fraunces** | Optisch, Retro-Revival | Editorial, Long-form | Google Fonts |
| **Cabinet Grotesk** | Charakterstarke Grotesque | Body, UI | `fontsource` |
| **Space Grotesk** | Technisch, präzise | Code-nahe UIs, SaaS | Google Fonts |
| **Gambarino** | Hochkontrast-Serif | Display, Hero | CDN |
| **JetBrains Mono** | Lesbar, Developer-Ästhetik | Code, Terminal | CDN / `fontsource` |

**Font-Einbindung via CSS `@font-face` (Pflicht: kein externes CDN in Produktion):**

```css
@font-face {
  font-family: 'Clash Display';
  src: url('/fonts/ClashDisplay-Variable.woff2') format('woff2');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

### Tailwind CSS v4 — Neue Konfigurationsparadigmen (CSS-First)

**Erkennungsmerkmal v3 vs. v4:**

```bash
# v3-Projekt:
cat tailwind.config.js   # → Datei existiert, enthält module.exports = {...}
grep "@tailwind" src/    # → @tailwind base; @tailwind components; @tailwind utilities

# v4-Projekt:
cat package.json | grep tailwind   # → "tailwindcss": "^4.0.0"
grep "@import" src/     # → @import "tailwindcss";
```

**Migration v3 → v4 (Agent-Pflichtschritte):**

```
1. @tailwind-Direktiven ersetzen:
   VORHER:  @tailwind base;
            @tailwind components;
            @tailwind utilities;
   NACHHER: @import "tailwindcss";

2. tailwind.config.js → @theme-Direktive:
   VORHER:  module.exports = { theme: { extend: { colors: { brand: '#7c3aed' } } } }
   NACHHER: In CSS-Datei:
            @theme {
              --color-brand: #7c3aed;
              --font-display: 'Clash Display', system-ui;
              --spacing-13: 3.25rem;
            }

3. Margin-Hacks durch gap ersetzen:
   VORHER:  <div class="flex"><div class="mt-4 ml-6">...</div></div>
   NACHHER: <div class="flex gap-x-6 gap-y-4">...</div>

4. Dark Mode: Klassen-Varianten statt media-query:
   VORHER:  @media (prefers-color-scheme: dark) { ... }
   NACHHER: dark:bg-brand-bg dark:text-brand-text
            (konsistent durch gesamte App — kein Mix aus beiden Methoden)
```

**Verbotene v4-Muster:**

| Verboten | Grund | Korrekt |
|---|---|---|
| `@tailwind base/components/utilities` | v3-Syntax, in v4 deprecated | `@import "tailwindcss"` |
| `module.exports` in tailwind.config.js | v3-API | `@theme { ... }` in CSS |
| `mt-4 ml-6` auf Kindelementen | Margin-Hacks — fragil, wartungsarm | `gap-x-6 gap-y-4` auf Parent |
| Mix aus `@media dark` + `dark:` Klassen | Inkonsistentes Dark-Mode-Verhalten | Ausschließlich `dark:` Klassen |

### Subagenten-Orchestrierung für große Frontend-Projekte

```
Orchestrierer (Haupt-Agent)
    ├── component-composition-reviewer  → React-Logik + Komponentenstruktur
    ├── design-verification             → Figma-Token-Abgleich
    └── a11y-wcag-compliance-auditor    → Barrierefreiheit + WCAG 2.1
```

**WCAG 2.1 AA — Prüfkriterien:**

| WCAG-Kriterium | Prüfung | Mindest-Anforderung |
|---|---|---|
| **1.4.3 Kontrastverhältnis** | Textfarbe vs. Hintergrund | AA: 4.5:1 (normal), 3:1 (groß) |
| **1.4.11 Nicht-Text-Kontrast** | Buttons, Formulare, Icons | 3:1 gegen Umgebung |
| **2.1.1 Tastaturnavigation** | Alle Funktionen per Tab erreichbar? | Vollständig |
| **2.4.7 Fokus sichtbar** | `focus-visible` vorhanden und sichtbar? | Pflicht |
| **4.1.2 ARIA-Attribute** | role, aria-label, aria-describedby korrekt? | Fehlerlos |
| **1.3.1 Semantische Struktur** | h1–h6-Hierarchie korrekt? Landmarks? | Vollständig |

### Pflicht-Ablauf für UI/UX-Jobs

1. **Design-Manifest erstellen** — Verbotene Fonts und Pflicht-Muster festlegen, bevor eine Zeile CSS geschrieben wird.
2. **Tailwind-Version prüfen** — v3 oder v4? `@tailwind`-Direktiven (v3) vs. `@import "tailwindcss"` + `@theme` (v4).
3. **CSS Custom Properties definieren** — Farbpalette, Spacing-Skala, Schriftarten in `:root` oder `@theme` zentralisieren.
4. **Tailwind konfigurieren** — v3: `tailwind.config.js`; v4: `@theme { ... }` in CSS. Asymmetrische Grids, Kurven, Keyframes.
5. **Hintergrundtextur wählen** — Gradient Mesh und/oder Noise-Overlay definieren; kein Flat-Color-Hintergrund.
6. **Komponenten customizen** — shadcn/ui-Kopien im Projekt anpassen; Standard-Varianten durch Design-Manifest-konforme ersetzen.
7. **Mikrointeraktionen prüfen** — Nur `transform`/`opacity` in Transitions; `will-change` und `translate3d(0,0,0)` setzen.
8. **Dark-Mode konsistent** — Ausschließlich `dark:` Tailwind-Klassen; kein Mix mit `@media prefers-color-scheme`.
9. **Margin-Hacks eliminieren** — Alle `mt-/ml-/mr-/mb-` auf Kindelementen durch `gap-` auf Parent ersetzen.
10. **Subagenten-Qualitätssicherung** (bei komplexen Projekten) — design-verification + a11y-wcag-compliance-auditor einsetzen.
11. **Visuellen Review** — Screenshot oder Live-Preview; explizit prüfen: Sieht es nach "generischer KI" aus? Wenn ja → Schritt 1.

---

## Sicherheitsregeln — niemals verletzen

- **Kein Dateizugriff ohne Freigabe**: Keine Datei öffnen, lesen oder schreiben ohne explizite Nutzererlaubnis.
- **Keine hardcodierten absoluten Pfade** außer `/tmp` — immer relative Pfade oder konfigurierbare Variablen.
- **Kein `rm -rf` ohne Guard** — immer `confirm()`-Pattern oder `--dry-run` vorschalten.
- **Variablen immer quoten**: `"$var"` statt `$var` (verhindert Wordsplitting und Globbing).
- **`set -euo pipefail` + `IFS=$'\n\t'`** in jedem Bash-Skript als erste ausführbare Zeile.
- **Temp-Files**: Nur via `mktemp` + `trap 'rm -f "$tmp"' EXIT`.

---

## Verwandte Ressourcen

| Ressource | Ladestufe | Kategorie | Inhalt |
|---|---|---|---|
| `resources/ui_design_system.py` | 3 | Frontend | Design-System-Generator: tailwind.config.js, CSS Tokens, HTML-Starter, Button/Card/Input/Badge, Gradient Mesh, Palette |
| `resources/tabellen.css` | 3 | Datenformate | Tabellen-Grundstil + Status-Badges (BEM) |
