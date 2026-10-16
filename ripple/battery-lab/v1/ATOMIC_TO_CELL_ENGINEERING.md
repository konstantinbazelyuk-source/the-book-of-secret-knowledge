# Ripple calcium battery: atomic-to-cell engineering dossier

**Status 2026-10-16:** runnable mathematical and data-ingestion software, grounded in peer-reviewed cell demonstrations. **No Ripple-made physical calcium cell or Samsung hardware recording has been performed.**

## 1. What changed from the original 2024 equations

Original historical idea: ion diffusion, ionic resistance, charge and resonance. The historical expression `Q=nF` lacks a charge-number factor if `n` is moles of Ca²⁺. `Q = ∫J A dt` counts transported **moles** (when J is mol/m²/s), not coulombs. `R=L/(ADC)` is dimensionally not ohms for D diffusivity and C molar density. Mechanical/LC resonance shifts or stores energy, but does not produce battery chemical free energy.

Physically grounded reference chain:

1. **Atomic electron transfer:** neutral Ca = [Ar]4s²; oxidation `Ca → Ca²⁺ + 2e⁻`. Ca²⁺ has +2 ionic charge. Reversible storage requires the reverse electrode reaction and an independently balanced cathode reaction.
2. **Charge count:** `Q_C=z n_mol F` (`z=2` for Ca²⁺), with F = N_A e = 96485.332123... C/mol; for Ca metal `q_theory = zF/(3.6 M)` = **1337.466 mAh/g of Ca metal**, NOT a cell-level capacity.
3. **Voltage & free energy:** `ΔG_cell = -n_electrons F E_rev`. One must specify **both half-reactions**, chemical activities, temperature and state of charge. `E = E° - RT/(nF) ln Q_reaction` is the Nernst equilibrium relation, not a discharge curve under load.
4. **Transport:** `J = -D∇c` is the concentration-only approximation; migration under electric fields, concentrated-solution correlations and interfaces can dominate real calcium electrochemistry. Single-layer ohmic drop may be estimated with `R_bulk=L/(κ A)` for measured conductivity κ; this omits interfaces.
5. **Kinetics:** symmetric Butler–Volmer approximation `η = 2RT/(nF) asinh(j/(2j0))`, valid only if the electron-transfer step has two symmetric transfer coefficients equal to 0.5 and known exchange current density `j0` (not currently calibrated).
6. **Actual energy:** `Q_dis=∫ I_dis(t)dt`, `E_dis=∫ V_dis(t)I_dis(t)dt`; charge and energy efficiencies compare separate *corresponding* charge/discharge processes. Timestamped real values must be captured with a known-calibrated instrument.
7. **Reversibility:** stable `Ca²⁺` transport through real electrolyte and anode interphase; required tolerable electrode passivation, sufficient cathode kinetics, stable voltage window, suppressed side reactions, and repeatable cycling under measured conditions.

## 2. Specific atomic bottlenecks shown in experimental literature

- **Ca metal surface chemistry:** passivating compounds including CaO, Ca(OH)₂ and CaCO₃ can obstruct divalent ion transport; reactive metal and moisture sensitivity complicate reproducibility. Electrolyte solvent and anion alter passivation chemistry.
- **Ca²⁺ coordination/desolvation:** high ionic charge produces strong interactions with solvent ligands and solid interfaces; successful Ca deposition depends on an ion-conducting surface and controlled desolvation. Solvation numbers, adsorption barriers and surface phases must be demonstrated experimentally or through independently checked atomistic calculations.
- **Cathode hosts:** Ca²⁺ insertion/extraction can be kinetically and structurally difficult. A positive capacity in one test is not evidence that every cathode supports long-lived reversible insertion.
- **Side reactions/cell balance:** two-terminal electrochemical curves may contain electrolyte decomposition or other counter-electrode reactions. Coulombic efficiency and capacity fade are essential, but not sufficient, observables.
- **Atomic-scale modeling:** DFT or validated interatomic potentials can estimate reaction energies/ion migration barriers; NEB estimates transition barriers; spectroscopy/diffraction can confirm chemistry. This package **does not run DFT/NEB** and does not invent atomic coordinates, band structures or migration barriers.

## 3. Experimental references: real measured results, differing designs

1. ACS Materials Letters (2025), DOI **10.1021/acsmaterialslett.5c00892**, Ca-metal/PTCDI cell, initial 105 mAh/g *of cathode* near 1.7 V discharge, approximately 67% CE after stabilizing and about 11 room-temp cycles in reported comparison. The product **178.5 Wh/kg** is calculated as `105 mAh/g × 1.7V` per **cathode active mass only**, not a measured whole-cell energy density.
2. Advanced Science (2025), DOI **10.1002/advs.202512339**, Ca metal with engineered interface + biomass carbon cathode, >500 cycles / 85.4% retention at 25 mA/g. Separate chemistry; results cannot be combined with #1 as one cell.
3. Nature Communications (2024), DOI **10.1038/s41467-024-45347-3**, rechargeable Ca/Cl₂ cell; CALS electrolyte conductivity reported 5.3 mS/cm at 25°C, 3.6 mS/cm at 0°C. The electrolyte conductivity is material/temperature-specific and the chemistry requires professional handling.
4. Joule (2026), DOI **10.1016/j.joule.2026.102401**, critical review covering why many Ca tests are confounded by Ca counter/reference electrodes, passive layers and poor reversibility; advises complementing two-terminal tests with proper electrode characterization.
5. ACS Chemical Reviews (2020), DOI **10.1021/acs.chemrev.9b00339**, extensive interphase and reversible Ca cycling challenges.
6. NIST CODATA 2022 constants, https://physics.nist.gov/constants (Faraday constant from defined e and N_A).

## 4. Experimental route to a genuinely characterized cell

**Stage A — Existing functioning system:** Use a professionally manufactured, certified low-voltage battery/power module and rated test instrument to run Ripple's power load. Log actual I/V/time and analyze with this package. This produces **real battery measurement data** without pretending the device uses calcium. Do not charge cells with an unprotected homemade circuit.

**Stage B — Calcium chemistry laboratory:** Work with a battery research lab able to handle sensitive metal/electrolytes and chemically compatible equipment. Specify full balanced chemistry and accessible electrochemical window. Lab performs electrode fabrication under controlled atmosphere and verified safety procedures, then reference-electrode characterization, CV / impedance (EIS), galvanostatic cycling, phase/compound spectroscopy, and microscopy as scientifically appropriate. This package can analyze the recorded current/voltage data if exported as CSV; it does not operate laboratory equipment.

**Stage C — independent physical verification:** Verify charge reversibility and chemistry (not just voltage), report discharge specific capacity with its *mass denominator*, CE and energy efficiency, voltage under operating current, repeatability across independent cells, cycle fade, temperature rise, safety, and failure conditions. Compare against contemporary published full cells on equal metrics, normalized carefully.

**Stage D — integration:** Only after the Ca cell physically exists with demonstrated repeatable stability should a protected and externally supervised electronics integration be scoped. Ripple receives measured voltage/current/temperature signals through a calibrated data acquisition interface with fail-safe isolation; it may analyze but does not autonomously set charging limits.

## 5. Measurement schema and diagnostics

CSV required `time_s,voltage_v,current_a,phase`, where phases are `charge,discharge,rest`, **current positive on discharge and negative on charge**, voltage nonnegative and time increasing. The program integrates adjacent same-phase samples with trapezoids. Abrupt phase transitions are excluded from integration; missing timestamps within a phase can bias results, so the data logger must maintain reliable sampling and timestamps. Calibrate the shunt/meter, export channel units, and document clock and power boundaries.

A single CSV does not identify side reactions, plating morphology, usable lifetime or electrochemical safety. Adjacent partial cycles should not be compared as CE unless they truly correspond to matched states of charge/cycles.

## 6. Correctness and limits

Run `python -m unittest discover -s tests -v` from the project directory. Standard-library-only Python computational core. Offline web UI uses local browser file import and no cloud upload.

The *physical battery* is **not fabricated** here; the purpose of this verified program is to make the mathematics operational, select real evidence-based experiments, and calculate measurements from a real laboratory instrument without false substitution of simulated for measured quantities.