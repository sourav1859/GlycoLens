# Dataset Adapters

Store dataset adapters, schema mappings, and provenance metadata here. Dataset contents belong in ignored local data directories.

`t1d_uom.py` pins T1D-UOM V1.0.4, validates the four core modalities, loads complete rows, converts glucose from mmol/L to mg/dL at the model boundary, and constructs leakage-safe meal windows. Exact duplicate CGM values collapse; conflicting values at the same timestamp are excluded rather than averaged. Nutrition rows sharing a timestamp are treated as components of one meal and aggregated.
