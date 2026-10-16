# Ripple Calcium Battery Lab v1.0

**Goal:** convert the historical calcium-battery equations into **executable, auditable engineering and real-measurement analysis**, benchmarked to published calcium battery research. This is software plus a documented laboratory test architecture. No calcium cell has been made in this environment.

## Quick start

### Samsung Android
Open `index.html` locally in the browser for atomic charge and bulk ionic resistance calculations; for actual measured I/V data, use the **Import CSV** control to process exported measurement data. For best mobile compatibility, host this static file on an HTTPS domain or public GitHub Pages instance. It never uploads imported data.

### Dell or other computer
Requires Python 3.10+ and the standard library only:

```bash
python battery_core.py calcium --grams 0.1
python battery_core.py literature
python battery_core.py ionic --length-m 0.0001 --area-m2 0.0001 --kappa-s-m 0.53
python battery_core.py measure data/SYNTHETIC_DEMO_NOT_MEASURED.csv
python -m unittest discover -s tests -v
```

## Files

- `battery_core.py` — Faraday, Nernst, ΔG, homogeneous ionic R, Fick planar flux current, Butler–Volmer, real-CSV integration.
- `index.html` — offline practical calculator and real measurement CSV importer with voltage chart and JSON export.
- `ATOMIC_TO_CELL_ENGINEERING.md` — atomic chemistry, paper-backed results, experimental gates, proven/unknown boundaries.
- `data/REPORTED_EXPERIMENTS.json` — verifiable literature *reported* numerical values; not full time-series measurements.
- `data/SYNTHETIC_DEMO_NOT_MEASURED.csv` — deliberately synthetic fixture to exercise import, not a real calcium battery.
- `tests/test_battery.py` — correctness, units, errors, exact charge integration and real-data ingestion behavior tests.

## Measurement requirements

CSV header: `time_s,voltage_v,current_a,phase`; phases `charge,discharge,rest`. Positive current means discharge, negative charge, zero rest. Analyzer excludes intervals crossing phase transitions. Coulombic efficiency only meaningful when charge/discharge correspond to the same verified cycle and state-of-charge window. This software is **measurement analysis**, not a charger or safety BMS.

## Research distinction

- **Physically established science:** Faraday charge, chemical ΔG to voltage, Nernst correction, Fick and bulk conductivity under assumptions.
- **Real published experiments:** identified peer-reviewed calcium cells, separately reported.
- **Calculated:** charge/capacity bound and voltage×capacity illustration, not Ripple battery measurements.
- **Measurement-enabled:** logging external instrument data; this build cannot read an instrument until a logger supplies CSV.
- **Unperformed:** actual electrolyte synthesis, Ca metal interface experiments, cell fabrication, hardware integration, charged/discharged Ripple calcium pack.

Do not mix calcium battery chemistry and wet/ionic hydrogel sensor electronics without properly separated controlled engineering work. Use a professionally built battery or isolated power supply for immediate Ripple hardware experiments while Ca research continues.
