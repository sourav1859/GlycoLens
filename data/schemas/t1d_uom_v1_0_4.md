# T1D-UOM V1.0.4 Provenance and Core Schema

## Release pin

| Field | Value |
|---|---|
| Dataset | T1D-UOM - A Longitudinal Multimodal Dataset of Type 1 Diabetes |
| Version | V1.0.4 |
| Version DOI | `10.5281/zenodo.17361905` |
| Git release commit | `ea52718b41cd27286df46acf87825555d4ec0463` |
| License | CC BY 4.0 |
| Expected extracted suffix | `ea52718` |

Downloaded files are research data and must remain outside Git. Configure the extraction with `GLYCOLENS_T1D_UOM_ROOT` or place it under an ignored `data/raw/` path.

## Core files

| Modality | Filename pattern | Required fields | Source units |
|---|---|---|---|
| CGM | `Glucose Data/UoMGlucose<ID>.csv` | `bg_ts`, `value` | mmol/L |
| Nutrition | `Nutrition Data/UoMNutrition<ID>.csv` | `meal_ts`, `meal_type`, `carbs_g`, `prot_g`, `fat_g`, `fibre_g` | grams |
| Bolus insulin | `Insulin Data/Bolus Data/UoMBolus<ID>.csv` | `bolus_ts`, `bolus_dose` | units |
| Basal insulin | `Insulin Data/Basal Data/UoMBasal<ID>.csv` | `basal_ts`, `basal_dose`, `insulin_kind` | units or units/hour per upstream metadata |

The adapter derives the participant identifier from each filename. It converts glucose to mg/dL with `mg/dL = mmol/L * 18.0182` while retaining the source mmol/L value in memory.

## Timestamp interpretation

The V1.0.4 CSV values use day-first timestamps such as `DD/MM/YYYY HH:MM`, despite the upstream README describing `MM/DD/YYYY`. The adapter therefore parses day-first formats before month-first fallback formats. Source timestamps do not include timezone offsets and remain timezone-naive during this Milestone 1 slice; DST interpretation requires a later explicit decision before cross-source integration.

## Data-quality policy

- Rows missing a required model field are reported by the audit and excluded from model-ready loading.
- Nutrition rows without a meal time are reported as insufficient precision and excluded rather than assigned to midnight.
- Exact duplicate CGM readings at one timestamp collapse to one point.
- Conflicting CGM values at one timestamp are excluded rather than selected or averaged.
- Multiple valid nutrition rows at the same timestamp are aggregated as components of one meal.
- Insulin events after the meal timestamp never enter inference context.
- A window is rejected when CGM gaps cannot be filled without crossing the configured 15-minute interpolation limit.
- A window is rejected when another meal occurs during the two-hour forecast horizon.

## Known upstream metadata inconsistencies

The V1.0.4 archive contains stale embedded metadata: `CITATION.cff` identifies `0.1.0`, and `Dataset Metadata DataCite.xml` identifies V1.0.2. GlycoLens uses the official Zenodo V1.0.4 record and matching Git tag/commit above as authoritative provenance.
