#!/usr/bin/env python3
"""Ripple Optical Agent Research v0.1: SIMULATED sensor and event routing.

This is a separate experimental adapter, not a modification of Ripple v0.1.
The Ripple neuron equations/parameters follow the public engineering brief
and verified JS simulator. No laser or ADC data were collected.
SPDX-License-Identifier: CC0-1.0
"""
from __future__ import annotations
import csv
import json
import math
import random
from pathlib import Path

PI = math.pi
WAVELENGTH_NM = 635.0
SAMPLE_PERIOD_S = 0.05


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class RippleNeuron:
    """Port of the *approved* v0.1 JS core, including exact threshold crossings.

    New routing logic appears outside this class; fixed input weights are not
    modified or 'learned'. RGB slots can accept normalized derived features,
    but a single 635 nm laser is NOT three physical color sources.
    """

    def __init__(self, adaptive: bool = True, target: float = 1.0):
        self.theta = 0.45
        self.adaptive = adaptive
        self.target = target
        self.tau_v = 0.5
        self.tau_r = 5.0
        self.refractory = 0.1
        self.eta = 0.08
        self.lo = 0.15
        self.hi = 2.5
        self.t = 0.0
        self.u = 0.0
        self.rate = 0.0
        self.rest = 0.0

    def step(self, inputs: tuple[float, float, float], dt: float) -> dict:
        if len(inputs) != 3 or any(not math.isfinite(x) for x in inputs):
            raise ValueError("Need three finite normalized features")
        if not math.isfinite(dt) or not 0 < dt <= 0.5:
            raise ValueError("dt must be in (0, 0.5]")
        red, green, blue = (clamp(x, 0.0, 1.0) for x in inputs)
        drive = 2.0 * red + 1.2 * green - 1.4 * blue
        start = self.t
        events = []
        elapsed = 0.0
        while elapsed < dt - 1e-12:
            left = dt - elapsed
            if self.rest > 1e-12:
                held = min(left, self.rest)
                self.rest = max(0.0, self.rest - held)
                self.u = 0.0
                elapsed += held
                continue
            crossing = math.inf
            if self.u >= self.theta:
                crossing = 0.0
            elif drive > self.theta:
                crossing = self.tau_v * math.log((drive - self.u) / (drive - self.theta))
            if crossing <= left + 1e-12:
                elapsed += max(0.0, min(left, crossing))
                events.append(start + elapsed)
                self.u = 0.0
                self.rest = self.refractory
            else:
                self.u = max(0.0, drive + (self.u - drive) * math.exp(-left / self.tau_v))
                elapsed = dt
        decay = math.exp(-dt / self.tau_r)
        integral = self.rate * self.tau_r * (1.0 - decay)
        self.rate *= decay
        for event in events:
            d = math.exp(-(start + dt - event) / self.tau_r)
            self.rate += d / self.tau_r
            integral += 1.0 - d
        if self.adaptive:
            self.theta = clamp(
                self.theta + self.eta * (integral - self.target * dt), self.lo, self.hi
            )
        self.t = start + dt
        return {
            "t": self.t, "u": self.u, "theta": self.theta,
            "rate_hz": self.rate, "drive": drive,
            "count": len(events), "events": events,
        }


def simulated_mirror_displacement_nm(t: float) -> float:
    """Known test fixture motion, not detected motion or real sensor data."""
    return 50.0 * math.sin(2 * PI * 0.70 * t) + 18.0 * math.sin(2 * PI * 0.17 * t)


def phase_step_intensities(
    displacement_nm: float, rng: random.Random, noise_sigma: float = 0.004,
    signal_power: float = 0.25, reference_power: float = 1.0,
) -> tuple[float, float, float, float]:
    """Four steady-state interferometer intensities with simulated ADC noise.

    Measurement law: I(delta) = Is + Ir + 2 sqrt(Is Ir) cos(phi+delta).
    For reflection geometry phi = 4 pi * displacement / wavelength.
    Four samples are *assumed* to view identical displacement per time step.
    A real experiment needs phase stepping or a calibrated 90-degree hybrid.
    """
    phi = 4 * PI * displacement_nm / WAVELENGTH_NM
    return tuple(
        signal_power + reference_power
        + 2 * math.sqrt(signal_power * reference_power) * math.cos(phi + delta)
        + rng.gauss(0.0, noise_sigma)
        for delta in (0.0, PI / 2, PI, 3 * PI / 2)
    )


def decode_phase(intensities: tuple[float, float, float, float]) -> tuple[float, float, float]:
    """Get wrapped phase and I/Q signed quadratures from 4 raw intensities."""
    a, b, c, d = intensities
    i = a - c
    q = d - b
    return math.atan2(q, i), i, q


def unwrap_phase(current: float, previous_wrapped: float, previous_unwrapped: float) -> float:
    step = (current - previous_wrapped + PI) % (2 * PI) - PI
    return previous_unwrapped + step


def run_demo(output_dir: Path, seed: int = 20261013, seconds: float = 60.0) -> dict:
    """Generate synthetic ADC, decode motion, duplicate nodes, route simple actions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    nodes = {"rising": RippleNeuron(), "falling": RippleNeuron()}
    prev_wrapped = None
    prev_unwrapped = 0.0
    prev_displacement = None
    rows = []
    actions = []
    n_samples = round(seconds / SAMPLE_PERIOD_S)
    if n_samples < 2:
        raise ValueError("seconds must contain at least two samples")
    for index in range(n_samples):
        t = index * SAMPLE_PERIOD_S
        actual = simulated_mirror_displacement_nm(t)
        raw = phase_step_intensities(actual, rng)
        phase, i, q = decode_phase(raw)
        if prev_wrapped is None:
            unwrapped = phase
        else:
            unwrapped = unwrap_phase(phase, prev_wrapped, prev_unwrapped)
        estimate = unwrapped * WAVELENGTH_NM / (4 * PI)
        # IMPORTANT: phase zero has been assumed. Hardware requires reference calibration.
        movement_step = 0.0 if prev_displacement is None else estimate - prev_displacement
        prev_wrapped = phase
        prev_unwrapped = unwrapped
        prev_displacement = estimate
        # PROPOSED adapter: fixed Ripple 'red' slot encodes direction-specific motion.
        # These are NOT actual red/green/blue spectral measurements.
        rise = clamp(movement_step / 10.0, 0.0, 1.0)
        fall = clamp(-movement_step / 10.0, 0.0, 1.0)
        n_rise = nodes["rising"].step((rise, 0.0, 0.0), SAMPLE_PERIOD_S)
        n_fall = nodes["falling"].step((fall, 0.0, 0.0), SAMPLE_PERIOD_S)
        if n_rise["count"]:
            for event in n_rise["events"]:
                actions.append({"time_s": round(event, 6), "action": "LOG_POSITIVE_MOTION"})
        if n_fall["count"]:
            for event in n_fall["events"]:
                actions.append({"time_s": round(event, 6), "action": "LOG_NEGATIVE_MOTION"})
        rows.append({
            "time_s": round(t, 6), "true_displacement_nm_simulated": actual,
            "decoded_displacement_nm_simulated": estimate,
            "adc_0_simulated": raw[0], "adc_90_simulated": raw[1],
            "adc_180_simulated": raw[2], "adc_270_simulated": raw[3],
            "in_phase": i, "quadrature": q, "decoded_phase_rad": phase,
            "rising_feature": rise, "falling_feature": fall,
            "rising_drive": n_rise["drive"], "falling_drive": n_fall["drive"],
            "rising_threshold": n_rise["theta"], "falling_threshold": n_fall["theta"],
            "rising_spikes": n_rise["count"], "falling_spikes": n_fall["count"],
        })
    err = [(r["decoded_displacement_nm_simulated"] - r["true_displacement_nm_simulated"]) for r in rows]
    summary = {
        "classification": "SIMULATION ONLY — no hardware measurement, no quantum computation, no autonomous AI",
        "samples": len(rows), "duration_s": seconds, "sample_period_s": SAMPLE_PERIOD_S,
        "laser_wavelength_nm_assumed": WAVELENGTH_NM,
        "seed": seed, "noise_std_normalized_intensity_assumed": 0.004,
        "displacement_RMSE_nm_simulation": math.sqrt(sum(e * e for e in err) / len(err)),
        "rising_event_count": sum(r["rising_spikes"] for r in rows),
        "falling_event_count": sum(r["falling_spikes"] for r in rows),
        "rising_end_threshold": nodes["rising"].theta,
        "falling_end_threshold": nodes["falling"].theta,
        "routed_actions": len(actions),
    }
    with (output_dir / "simulated_sensor_and_neurons.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    (output_dir / "simulated_agent_events.json").write_text(json.dumps(actions, indent=2) + "\n")
    (output_dir / "simulated_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def original_brightness_step_regression() -> list[dict]:
    """Independent regression run of the archived 2-node *brightness* experiment."""
    adaptive = RippleNeuron()
    fixed = RippleNeuron(adaptive=False)
    ea, eb = [], []
    for index in range(2400):
        t = index * 0.05
        red = 0.35 if t < 40.0 or t >= 80.0 else 0.70
        ra = adaptive.step((red, 0.0, 0.0), 0.05)
        rb = fixed.step((red, 0.0, 0.0), 0.05)
        ea.extend(ra["events"])
        eb.extend(rb["events"])
    return [
        {"start": lo, "end": hi,
         "adaptive_hz": len([x for x in ea if lo <= x < hi]) / (hi - lo),
         "fixed_hz": len([x for x in eb if lo <= x < hi]) / (hi - lo)}
        for lo, hi in ((20, 40), (60, 80), (100, 120))
    ]


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    summary = run_demo(here / "results")
    summary["original_model_regression"] = original_brightness_step_regression()
    print(json.dumps(summary, indent=2))