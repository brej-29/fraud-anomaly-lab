---
name: Clearcut
description: A calm, precise workbench for fraud review capacity decisions.
colors:
  paper: "#f7f8f2"
  white: "#fff"
  text: "#233c33"
  ink: "#213d34"
  muted: "#50634f"
  forest: "#173c35"
  green: "#24745e"
  lime: "#d5ee96"
  line: "#dfe5dc"
  warm: "#f0f2e9"
  primary-hover: "#2b5746"
  quiet: "#edf1e8"
  quiet-ink: "#2a4f3d"
  quiet-hover: "#e0e8d8"
  origin: "#edf1e7"
  selected-row: "#eff5e8"
  ochre: "#a26c25"
  random: "#78847f"
  focus: "#387cbd"
  error: "#8a3f29"
typography:
  display:
    fontFamily: "DM Sans Variable, sans-serif"
    fontSize: "clamp(28px, 3vw, 40px)"
    fontWeight: 560
    lineHeight: 1.17
    letterSpacing: "-.035em"
  headline:
    fontFamily: "DM Sans Variable, sans-serif"
    fontSize: "18px"
    fontWeight: 620
    lineHeight: 1.35
    letterSpacing: "-.02em"
  section-title:
    fontFamily: "DM Sans Variable, sans-serif"
    fontSize: "17px"
    fontWeight: 620
    lineHeight: 1.35
    letterSpacing: "-.02em"
  body:
    fontFamily: "DM Sans Variable, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  supporting:
    fontFamily: "DM Sans Variable, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.8
  metric:
    fontFamily: "DM Sans Variable, sans-serif"
    fontSize: "30px"
    fontWeight: 520
    lineHeight: 1.3
    letterSpacing: "-.035em"
  capacity:
    fontFamily: "DM Sans Variable, sans-serif"
    fontSize: "43px"
    fontWeight: 510
    lineHeight: 1
    letterSpacing: "-.04em"
  button:
    fontFamily: "DM Sans Variable, sans-serif"
    fontSize: "12px"
    fontWeight: 580
    lineHeight: 1.5
rounded:
  tag: "4px"
  field: "5px"
  button: "6px"
  navigation: "7px"
  strip: "9px"
  panel: "14px"
spacing:
  compact: "6px"
  icon-gap: "8px"
  related: "12px"
  group: "20px"
  panel: "24px"
  section: "27px"
  canvas: "37px"
components:
  button-primary:
    backgroundColor: "{colors.forest}"
    textColor: "{colors.white}"
    typography: "{typography.button}"
    rounded: "{rounded.button}"
    padding: "9px 15px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-quiet:
    backgroundColor: "{colors.quiet}"
    textColor: "{colors.quiet-ink}"
    typography: "{typography.button}"
    rounded: "{rounded.button}"
    padding: "9px 15px"
  button-quiet-hover:
    backgroundColor: "{colors.quiet-hover}"
  navigation-active:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.forest}"
    rounded: "{rounded.navigation}"
    padding: "12px 13px"
  panel:
    backgroundColor: "{colors.white}"
    rounded: "{rounded.panel}"
  strategy-select:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "9px 8px"
    width: "100%"
  origin-strip:
    backgroundColor: "{colors.origin}"
    rounded: "{rounded.strip}"
    padding: "13px 17px"
  budget-preset:
    backgroundColor: "#f1f3ec"
    rounded: "{rounded.tag}"
    padding: "5px 2px"
  budget-preset-selected:
    backgroundColor: "{colors.lime}"
    textColor: "#29451e"
  outcome-tag:
    backgroundColor: "#edf1e6"
    textColor: "#4b6346"
    rounded: "{rounded.tag}"
    padding: "4px 7px"
  outcome-tag-fraud:
    backgroundColor: "#f4e5dd"
    textColor: "#8c4328"
---

# Design System: Clearcut

## Overview

**Creative North Star: "Environmental Wayfinding"**

Clearcut treats a capacity decision as a place to navigate with confidence. Warm paper, forest ink, acid-green selection, fine dividers, and humanist letterforms establish a quiet working environment. The chart receives generous space; compact observations and controls keep the decision in view.

The system is measured and direct. Counts, denominators, source identity, and uncertainty sit beside the result they qualify. Flat surfaces and familiar native controls support inspection; visual emphasis follows the selected state and the analyst's next action.

**Key Characteristics:**

- Warm paper with forest anchors and a restrained lime selection signal.
- Spacious charts paired with compact, precise controls.
- Humanist text and tabular figures for comparisons.
- Explicit source, outcome, and uncertainty context.
- Responsive navigation and independently scrollable data tables.

## Colors

A natural neutral field carries dark green structure, with distinct colors for selection, observed capture, comparison, focus, and errors. Frontmatter values are normative.

### Primary

- **Forest:** navigation rail, primary import/export actions, chart callout, and standard toast.
- **Capture green:** selected capture curve, observed recall, native control accent, and the outcome bar.
- **Acid lime:** current navigation destination, selected budget preset, brand accent, and text selection.

### Secondary

- **Ochre:** comparison baseline; the dashed stroke distinguishes it from the selected curve.
- **Random gray:** expected random-selection line, with its own shorter dash pattern.
- **Focus blue:** visible keyboard outline, independent of selected state.
- **Error earth:** validation errors and error toast; known fraud tags use a softer earth-tinted surface.

### Neutral

- **Paper / white / warm:** canvas, bounded panels, and subordinate surface layering.
- **Text / ink / muted:** default text, field or emphasized text, and supporting explanations. The final muted value comes from the later base override.
- **Line:** thin panel borders, column dividers, and section separators.
- **Origin / selected row:** quiet dataset context and the current comparison row.

**The Selection Rule.** Lime identifies active location or chosen capacity. Observed fraud capture uses green and retains a numeric label.

**The Evidence Rule.** Chart series combine color, stroke pattern, and a text legend; exact counts remain available in a table.

## Typography

**Display and Body Font:** DM Sans Variable with sans-serif fallback. The same loaded family handles headings, prose, labels, and figures; no separate mono face is used.

The variable weight range gives headings a firm but conversational character. Tight tracking belongs to large headings and figures. Ordinary prose keeps normal tracking and generous leading.

### Hierarchy

- **Display:** the page heading uses the frontmatter clamp. On phones it becomes a fixed size (31px), with line height (1.18) and a short measure (15ch).
- **Headline and section title:** general headings and panel headings use their corresponding frontmatter roles. Panel titles reduce slightly on phones (16px).
- **Body and supporting text:** the base is the body role; explanatory blocks commonly use supporting text, with measures around (65–75ch). Page subtitles use (13px), reducing to (12px) on phones.
- **Metrics:** the four observations use the metric role; compact desktop reduces them to (26px), phones use (27px). Labels are (12px) and qualifiers (11px), reducing to (11px) and (10px) on phones.
- **Capacity:** the large output uses the capacity role; the percent suffix is smaller (24px). Phone output grows to (45px).
- **Tables:** final table text is (12px), including phones. Header labels remain smaller (10px desktop, 9px phone).
- **Utility text:** chart legends use (11px desktop, 10px phone); chart notes use (11px desktop, 10px phone). Fine metadata is subordinate to the decision content.

**The Stable Figures Rule.** Tables, outputs, and metric values use tabular numerals so changing capacity does not disturb comparisons.

## Layout

The desktop shell has a fixed forest rail (208px), a topbar (80px), and a centered content region capped at (1620px). Canvas padding uses the canvas token. Four observations align in equal columns with fine vertical dividers. The main workbench pairs a flexible chart with an inspector (300px) across a gap (20px). Comparison tables span the available width beneath.

Repeated spacing follows compact control gaps (6–8px), related content gaps (12px), group gaps (20px), panel padding near (23–25px), and section separation near (27px). Import pairs a large upload panel with a file-contract column in a (1.2fr / 1fr) grid, with a wider gap (45px). Supporting reading surfaces use restrained text measures rather than stretching prose across the canvas.

Responsive rules follow the implemented breakpoints:

- **Wide, at least 1600px:** inspector grows to (330px), chart receives more top breathing room, and top canvas padding becomes (45px).
- **At most 1200px:** rail becomes (180px), canvas padding (28px), inspector (270px), and workbench gap (16px). Dataset context may wrap while its source badge remains visible.
- **At most 980px:** rail becomes (165px); chart and inspector stack. The inspector internally uses two columns for controls and outcomes. Import becomes one column; schema definitions briefly use two columns.
- **At most 700px:** rail becomes a static horizontal header; all three navigation destinations retain icons and visible compact labels. The topbar becomes (61px), canvas uses (26px 20px), observations become two columns, and the inspector returns to one column. Import schema and supporting reading layouts stack. Sample actions fill available width.

The body supports a minimum width (320px). Tables keep their columns and scroll within keyboard-focusable regions. A visible phone hint explains sideways scrolling. The chart switches from a (740 × 300) viewBox to (360 × 270) on phones so axes and the selected point stay readable.

## Elevation & Depth

The working canvas is flat. White panels, pale context strips, and fine borders provide separation; cards do not cast shadows at rest. Only the floating toast uses a soft shadow (`0 6px 24px #173c3526`) to distinguish temporary feedback from document content.

**The Flat Workspace Rule.** Preserve tonal layering and hairline separation for persistent surfaces; reserve floating elevation for transient feedback.

## Shapes

Panels use the large, gently rounded panel token; controls have tighter corners. Tags and presets use the smallest radius, navigation slightly larger corners, and context strips an intermediate radius. One-pixel borders contain panels and native selects. Small circular dots support status and strategy labels; the chart marker has a white halo. Stroke icons are simple inline geometry with rounded caps and joins, generally (15–19px) within controls and navigation.

## Components

### Buttons

Confident, compact actions. Primary and quiet variants share the frontmatter padding, radius, and type with minimum height (39px), inline icon gap (8px), and icons (15px). Primary actions shift to the primary-hover color; quiet actions shift to quiet-hover. Background and text transitions last (.18s). The export action spans its inspector and uses its own darker hover surface. Disabled buttons reduce opacity (.45) and use a not-allowed cursor. All keyboard-focusable controls keep a blue outline (3px) with offset (4px).

### Inputs / Fields

The capacity range is a familiar native control spanning its container with a green accent and a clear accessible label. Its values run from (0–5%) at increments of (0.1%). Presets are equal-width compact buttons; pressed state is conveyed with lime and heavier text. The native strategy select uses a thin pale border, tight field radius, and full width; on phones its text and padding increase to (12px). File input remains behind an explicit choose-file button. The upload panel shifts to a pale green fill and green border while dragging. Validation is rendered as text and announced as an alert.

### Navigation

The forest rail uses light text and line icons. Active navigation has lime fill, forest text, and stronger weight. Hover uses a lighter forest surface (`#284d42`) with a background transition (.2s). Phone navigation stays inside the header with visible labels, while auxiliary privacy and version copy leaves the compact rail. Route changes move focus to the main region; the skip link becomes visible on keyboard focus.

### Cards / Containers

White bordered panels hold charts, capacity controls, comparisons, queues, and upload actions. Chart padding is asymmetric to support a full-width contextual note at the bottom. Context strips carry dataset provenance; selected comparison rows use a light green fill and a written selected marker on wider views. Table rows use fine horizontal rules, never alternating heavy cards. Queue outcomes use a muted tag; confirmed fraud receives an earth tint and a written label.

### Capture Chart

The selected series is a solid green line (3px) with a pale green vertical fade beneath it. The comparison baseline is ochre (2px), dashed (6 5). Expected random selection is gray (1.4px), dashed (3 5). A thin dashed vertical guide, white-ringed marker, and forest numeric callout identify the chosen capacity. Horizontal grid lines are pale and unobtrusive. The x-axis always represents capacity (0–5%); the y-axis represents observed fraud capture (0–100%). An accessible title and description accompany the chart. Missing or zero positive labels replace the curve with a plain explanatory state.

### Capacity Outcomes and Tables

Place caught fraud, legitimate reviews, missed fraud, and uncertainty close to the capacity control. The outcome bar shows precision, while written counts supply meaning. Strategy comparisons use one shared capacity; selection is identified through both fill and text. Keep exact data in the table and make overflow explicit on phones. Source badges distinguish benchmark, synthetic, and private data without implying that synthetic outcomes are evidence.

### Feedback and Motion

State changes use short, calm transitions: chart path (.3s) and outcome width (.4s) use `cubic-bezier(.16,1,.3,1)`. Toast entrance lasts (.3s) with a subtle opacity and blur change. A loading skeleton pulses at (1.5s). Reduced-motion preference disables animations, transitions, and smooth scrolling across the entire interface. Do not make chart meaning depend on motion.

## Do's and Don'ts

### Do:

- **Do** keep active selection, observed capture, comparison, and errors semantically distinct.
- **Do** align changing figures with tabular numerals and preserve shared denominators.
- **Do** retain source, uncertainty, and legitimate-review cost beside the decision.
- **Do** preserve visible phone navigation labels and the table overflow hint.
- **Do** use inline stroke icons, native range/select behavior, and visible keyboard focus.
- **Do** honor reduced motion and provide meaningful empty and validation states.

### Don't:

- **Don't** use color alone to identify a series, selection, or known outcome.
- **Don't** add persistent card shadows where tonal layering and fine borders already separate content.
- **Don't** shrink table data to fit a phone; preserve legibility and contained scrolling.
- **Don't** imply observed capture when labels are absent, or present a synthetic batch as benchmark evidence.
- **Don't** hide the legitimate workload or uncertainty behind the headline result.
