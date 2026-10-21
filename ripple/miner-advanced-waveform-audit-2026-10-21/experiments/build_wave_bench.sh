#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
cc -O3 -fPIC -shared -o native/libripple_baseline.so native/sha256d_scan_original.c -lcrypto
cc -O3 -fPIC -shared -Wno-deprecated-declarations -o native/libripple_midstate.so native/sha256d_scan.c -lcrypto
python experiments/waveform/benchmark_midstate.py
python experiments/waveform/advanced_wave_control.py