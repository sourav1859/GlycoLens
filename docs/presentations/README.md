# Presentation Assets

This directory contains approved presentation source assets copied without altering their originals.

## Bootstrap inventory

- `02_BrandElements_Arrows_HB_L3_NO.potx`: available in the Capstone workspace and copied during bootstrap after validation.
- [`Sourav Patil-GlycoLens_Project_Specification.pptx`](Sourav%20Patil-GlycoLens_Project_Specification.pptx):
  unchanged 10-slide project-specification presentation supplied on September 30, 2026. The file
  passed package-integrity and private-information scans, and every slide rendered successfully.
  Slide 8 retains a minor source-layout issue where the subtitle begins slightly beyond the left
  canvas edge.

## Milestone 2 presentation draft

- [November 3 revised PowerPoint](GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx):
  revised November 3 at the user’s request with a 7–8 minute progress-report speech following the Milestone 1 style,
  targeting 7:30. Ten main slides and four hidden backups retain the current
  RIT masters, artwork, Arial typography, 16:9 dimensions and original chart evidence.
  The earlier v2 and v3 decks remain preserved separately. Slide faces are unchanged from v3.
- [Matching Markdown notes](../reports/GlycoLens_Milestone_2_Presentation_Notes.md):
  875 words of suggested speech, 927 with transitions, brief technical definitions, emphasis points,
  timing, sources, 24 prepared answers and a rehearsal checklist. The same
  slide-specific speech and evidence appear in the embedded PowerPoint notes.

Slides 11–14 are hidden from normal slideshow playback and available for questions.
The deck contains five native editable charts, four native tables, an editable
workflow, and a cropped recorded synthetic-demo screenshot. It separates the original
T1D-UOM negative benchmark from the independent MetaboNet findings, and the current
Chronos app from the LightGBM research candidate. This is a presentation draft, not
full M2 closure or evidence of a new experiment/live verification run.

Package, geometry, Arial reference-font, native chart/data-workbook and re-import
checks passed. Final slides were rendered and reviewed. The preview renderer clips
some inherited footer graphics on table-only backup slides, although the original
master graphics remain in the package. Native PowerPoint review could not complete
because app-access approval timed out. Keep this target-application check explicit.
The private build, validation receipts and previews are under
`.cache/m2-presentation-2026-11-03/`. Revision evidence is in
`.cache/m2-presentation-revision-2026-11-03/`. The three revised slide faces were
reviewed at full size and the complete deck was rendered. Original chart XML and
workbook bytes were retained during the targeted edit. The subsequent notes-only
v4 revision and checks are in `.cache/m2-notes-refinement-2026-11-03/`.

## Current Milestone 1 presentation

- [`GlycoLens_Milestone_1_Presentation_v2.pptx`](GlycoLens_Milestone_1_Presentation_v2.pptx):
  eight-slide RIT presentation revised on October 5, 2026. It gives a brief project reminder,
  Milestone 1 objectives, literature-informed method choices, quantified feasibility, meal-window
  eligibility, synthetic application and simulation evidence, obstacles and personal assessment,
  and the Milestone 2 schedule and advisor decisions.
- [Detailed notes in Word](../reports/GlycoLens_Milestone_1_Presentation_Notes_v2.docx),
  [PDF reading copy](../reports/GlycoLens_Milestone_1_Presentation_Notes_v2.pdf), and
  [Markdown source](../reports/GlycoLens_Milestone_1_Presentation_Notes_v2.md):
  the same 692-word suggested speech used in the slide speaker notes, with optional transitions
  and a 5:30 rehearsal target. The project-specification notes structure is followed with
  detailed emphasis points, a timing table, 22 prepared answers, short answers, and a rehearsal checklist.

The revised deck contains three native editable charts with embedded data workbooks and one
native runtime table. Its simulation chart contains all 288 five-minute points, with glucose
displayed to two decimals. Runtime values use the final September 29 closure run. The final
package, layout, font, native-evidence, and re-import gates passed, and every slide was inspected.
The PDF notes were rendered and every page inspected. Native Word pagination could not be
verified in this environment; the PDF is a separately typeset reading copy of the authored DOCX.

Local generation sources remain in the ignored `.cache/m1-presentation/revision-v2/` directory:
`content.json` is shared by `build-revised.mjs`, `build-detailed-notes.py`, and
`render-detailed-notes.py`. The build receipt and preview images are private QA artifacts.
The previous eight-slide presentation and notes, and original closure deck below, are preserved as historical evidence.

## Original closure deck

- [`GlycoLens_Milestone_1_Closure.pptx`](GlycoLens_Milestone_1_Closure.pptx): seven-slide,
  RIT-branded Milestone 1 closure presentation with speaker notes, two editable charts, and one
  editable closure-audit table.

The finalization gate reported zero package-integrity findings, zero layout findings or warnings,
valid native charts/table, and a successful first-party re-import. All seven rendered slides were
also inspected individually. The deck contains aggregate and synthetic evidence only; it contains
no private academic addresses, credentials, local endpoints, absolute local paths, or row-level
health data.

Do not add private data or a binary with a presentation extension unless it is a valid, non-empty,
reviewed Office file.
