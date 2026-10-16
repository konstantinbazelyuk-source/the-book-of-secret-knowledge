"""Ripple Calcium Battery Lab: unit-conscious, independently testable measurements.

No electrochemical cell is controlled/charged by this software. CSV inputs are
measurements supplied by a logger, not generated or certified physical data.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import csv
import json
import math
import sys

ELEMENTARY_CHARGE_C = 1.602176634e-19  # exact, SI
AVOGADRO_PER_MOL = 6.02214076e23      # exact, SI
FARADAY_C_PER_MOL = ELEMENTARY_CHARGE_C * AVOGADRO_PER_MOL
GAS_CONSTANT_J_PER_MOL_K = 8.31446261815324
CALCIUM_MOLAR_MASS_G_PER_MOL = 40.078  # conventional standard atomic weight
Z_CALCIUM = 2


def _positive(name: str, x: float) -> float:
    x = float(x)
    if not math.isfinite(x) or x <= 0:
        raise ValueError(f"{name} must be positive finite")
    return x


def theoretical_calcium_charge(mass_g: float) -> dict:
    """Upper bound IF all Ca metal reacts Ca -> Ca2+ + 2e-.

    Does not incorporate the mass of cathode/electrolyte/case, reversibility,
    electrochemical voltage or usable capacity.
    """
    mass_g = _positive("mass_g", mass_g)
    moles = mass_g / CALCIUM_MOLAR_MASS_G_PER_MOL
    charge = moles * Z_CALCIUM * FARADAY_C_PER_MOL
    return {
        "mass_g": mass_g,
        "ca_mol": moles,
        "electron_mol": Z_CALCIUM * moles,
        "charge_coulomb_theoretical": charge,
        "capacity_mAh_theoretical": charge / 3.6,
        "specific_mAh_g_theoretical": Z_CALCIUM * FARADAY_C_PER_MOL / 3.6 / CALCIUM_MOLAR_MASS_G_PER_MOL,
        "scope": "Ca-metal active-material theoretical upper bound; not a constructed full cell",
    }


def reversible_chemical_energy(delta_g_j_per_mol: float, electron_mol_per_reaction: float) -> dict:
    """Thermodynamic E_rev = -DeltaG / (n F), if a full reaction is supplied."""
    n = _positive("electron_mol_per_reaction", electron_mol_per_reaction)
    dg = float(delta_g_j_per_mol)
    if not math.isfinite(dg):
        raise ValueError("delta_g_j_per_mol must be finite")
    return {"reversible_voltage_V": -dg / (n * FARADAY_C_PER_MOL),
            "scope": "Only valid for the specified complete balanced cell reaction and thermodynamic conditions"}


def nernst_voltage(e_standard_v: float, n_electrons: int, temperature_k: float, reaction_quotient: float) -> float:
    n = _positive("n_electrons", n_electrons)
    t = _positive("temperature_k", temperature_k)
    q = _positive("reaction_quotient", reaction_quotient)
    e0 = float(e_standard_v)
    if not math.isfinite(e0):
        raise ValueError("e_standard_v must be finite")
    return e0 - GAS_CONSTANT_J_PER_MOL_K * t / (n * FARADAY_C_PER_MOL) * math.log(q)


def ionic_resistance(length_m: float, area_m2: float, conductivity_s_m: float) -> dict:
    """R=L/(kappa*A) for a homogeneous ohmic ionic conductor.

    No electrode contact, double layer, desolvation or interfacial loss included.
    """
    length_m = _positive("length_m", length_m)
    area_m2 = _positive("area_m2", area_m2)
    k = _positive("conductivity_s_m", conductivity_s_m)
    return {"ohm": length_m / (k * area_m2), "scope": "Homogeneous bulk-electrolyte component ONLY"}


def diffusion_current_ceiling(area_m2: float, diffusion_m2_s: float,
                              concentration_mol_m3: float, thickness_m: float, valence: float = 2) -> dict:
    """Planar steady concentration-gradient estimate, ignoring migration and convection."""
    a = _positive("area_m2", area_m2)
    d = _positive("diffusion_m2_s", diffusion_m2_s)
    c = _positive("concentration_mol_m3", concentration_mol_m3)
    l = _positive("thickness_m", thickness_m)
    z = _positive("valence", valence)
    flux = d * c / l
    return {"max_flux_mol_m2_s_model": flux,
            "max_current_A_model": z * FARADAY_C_PER_MOL * a * flux,
            "scope": "Steady, one-sided Fick approximation, not validated calcium-cell current limit"}


def symmetric_butler_volmer_overpotential(current_density_a_m2: float,
                                           exchange_current_density_a_m2: float,
                                           temperature_k: float, electrons: int = 2) -> float:
    """Eta=2RT/(nF) asinh(j/(2j0)) for alpha_a=alpha_c=0.5."""
    j = float(current_density_a_m2)
    if not math.isfinite(j):
        raise ValueError("current_density_a_m2 must be finite")
    j0 = _positive("exchange_current_density_a_m2", exchange_current_density_a_m2)
    t = _positive("temperature_k", temperature_k)
    n = _positive("electrons", electrons)
    return 2 * GAS_CONSTANT_J_PER_MOL_K * t / (n * FARADAY_C_PER_MOL) * math.asinh(j / (2 * j0))


@dataclass(frozen=True)
class Sample:
    time_s: float
    voltage_v: float
    current_a: float
    phase: str  # discharge, charge, rest


def read_measurements(path: str | Path) -> list[Sample]:
    """CSV required: time_s,voltage_v,current_a,phase.

    Sign convention: discharge current POSITIVE, charge current NEGATIVE.
    Time must increase. Adjacent pairs crossing phases are excluded from
    trapezoid integration to avoid treating interruptions as long plateaus.
    """
    out = []
    with open(path, newline="", encoding="utf-8-sig") as fp:
        r = csv.DictReader(fp)
        cols = {"time_s", "voltage_v", "current_a", "phase"}
        if not cols.issubset(r.fieldnames or []):
            raise ValueError("CSV requires columns: time_s,voltage_v,current_a,phase")
        for no, row in enumerate(r, start=2):
            try:
                s = Sample(float(row["time_s"]), float(row["voltage_v"]), float(row["current_a"]), row["phase"].strip().lower())
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid measurement at CSV line {no}") from exc
            if not all(math.isfinite(v) for v in (s.time_s, s.voltage_v, s.current_a)):
                raise ValueError(f"Nonfinite reading at line {no}")
            if s.voltage_v < 0 or s.phase not in {"discharge", "charge", "rest"}:
                raise ValueError(f"Invalid voltage or phase at line {no}")
            if s.phase == "discharge" and s.current_a < 0:
                raise ValueError(f"Discharge current must be >=0 at line {no}")
            if s.phase == "charge" and s.current_a > 0:
                raise ValueError(f"Charge current must be <=0 at line {no}")
            if s.phase == "rest" and abs(s.current_a) > 1e-12:
                raise ValueError(f"Rest current must equal zero at line {no}")
            if out and s.time_s <= out[-1].time_s:
                raise ValueError(f"Time must strictly increase at line {no}")
            out.append(s)
    if len(out) < 2:
        raise ValueError("At least two timestamped measurements are needed")
    return out


def analyze_measurements(samples: list[Sample]) -> dict:
    """Integrate time series using trapezoids within contiguous same-phase records.

    Charge/discharge counters exclude transition gaps. No model extrapolation
    across missing logger intervals. If logger contains gaps inside same phase,
    resulting integration can bias: verify logging completeness independently.
    """
    if len(samples) < 2:
        raise ValueError("At least two readings needed")
    phase = {"discharge": {"Ah": 0.0, "Wh": 0.0, "duration_s": 0.0, "segments": 0},
             "charge": {"Ah": 0.0, "Wh": 0.0, "duration_s": 0.0, "segments": 0}}
    for x, y in zip(samples, samples[1:]):
        if y.time_s <= x.time_s:
            raise ValueError("Time must increase")
        if x.phase == y.phase and x.phase in phase:
            dth = (y.time_s - x.time_s) / 3600.0
            a = (abs(x.current_a) + abs(y.current_a)) / 2.0 * dth
            energy = (abs(x.current_a) * x.voltage_v + abs(y.current_a) * y.voltage_v) / 2.0 * dth
            t = phase[x.phase]
            t["Ah"] += a
            t["Wh"] += energy
            t["duration_s"] += y.time_s - x.time_s
            t["segments"] += 1
    dis, chg = phase["discharge"], phase["charge"]
    out = {"sample_count": len(samples), "discharge": dis, "charge": chg,
           "coulombic_efficiency": dis["Ah"] / chg["Ah"] if chg["Ah"] else None,
           "energy_efficiency": dis["Wh"] / chg["Wh"] if chg["Wh"] else None,
           "sign_convention": "discharge current >=0; charge <=0; phase changes excluded",
           "provenance": "computed from user-supplied CSV, not a certified physical cell test"}
    return out


def literature_proxy(capacity_mAh_g: float, voltage_v: float) -> dict:
    """Numerical rectangular approximation E~V_nom*C, not integrated V(Q)."""
    c = _positive("capacity_mAh_g", capacity_mAh_g)
    v = _positive("voltage_v", voltage_v)
    return {"voltage_v_reported": v, "capacity_mAh_g_reported": c,
            "cathode_active_specific_energy_Wh_kg_rectangular_estimate": c * v,
            "scope": "cathode active mass only; nominal V*Q proxy, NOT reported measured full-cell Wh/kg"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    c = sub.add_parser("calcium", help="Faraday theoretical Ca-metal active-mass upper bound")
    c.add_argument("--grams", type=float, required=True)
    m = sub.add_parser("measure", help="Integrate actual, user-supplied cell I/V measurements")
    m.add_argument("csv", type=Path)
    l = sub.add_parser("literature", help="Published Ca/PTCDI nominal-voltage capacity calculation")
    p = sub.add_parser("ionic", help="Conductivity/geometry ohmic estimate; requires measured kappa")
    p.add_argument("--length-m", type=float, required=True)
    p.add_argument("--area-m2", type=float, required=True)
    p.add_argument("--kappa-s-m", type=float, required=True)
    args = ap.parse_args(argv)
    if args.command == "calcium": result = theoretical_calcium_charge(args.grams)
    elif args.command == "measure": result = analyze_measurements(read_measurements(args.csv))
    elif args.command == "literature": result = literature_proxy(105, 1.7)
    elif args.command == "ionic": result = ionic_resistance(args.length_m, args.area_m2, args.kappa_s_m)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try: main()
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)