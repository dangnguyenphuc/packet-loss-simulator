"""
NetEq penalty scoring.

The app logs one line per decode operation to the pulled .txt files (see
appendNetEqMode() in the C++ snippet at the bottom of this file) — the
numeric NetEq Mode (0-10, MODE_KEYS order) for every op, in temporal order.
That's enough to replay the app's actual `plc_accumulate_ratio_.v1` state
machine exactly:
  - kCodecPlc / kExpand ACCUMULATE onto the running v1 (+= weight), so a
    run of N consecutive loss-concealment ops is penalized more than N
    isolated ones would be.
  - Every other mode RESETS v1 to a fixed value (its own weight, or 0).
  - v1 is clamped to [0, MAX_SCORE] after every op.
  - `NetEqImpl::CalculateScore()` — which does the accumulate/reset/clamp
    above — runs once per NetEq `GetAudio()` call, i.e. once per WebRTC's
    standard 10ms output chunk (confirmed from its call site: inside the
    same GetAudio() switch that dispatches kNormal/kExpand/etc., not
    tied to network packet size). That's 100 ops/second — OPS_PER_SECOND
    below — matching the ~100-115 ops seen per 20s test.
  - `NetEqImpl::GetLastNeteqScore()` turns the trailing-150-op window
    (`plc_ratio_history_`) into a single point-in-time score:
        mean_v1 = sum(v1 over the trailing 150 ops) / 150
        score   = (100 - clamp(100 * mean_v1, 0, 100)) / 20
                = clamp(MAX_SCORE - 5 * mean_v1, 0, MAX_SCORE)
    i.e. the score is 5x MORE sensitive to mean_v1 than a plain
    `MAX_SCORE - mean_v1` would suggest, and hits the floor of 0 once
    mean_v1 alone reaches 1.0 (a fifth of v1's own [0, 5] range) — not at
    mean_v1 == MAX_SCORE. An earlier version of this script used the
    plain (wrong) transform, which is why a first calibration pass
    (kCodecPlc=0.59) badly overshot in real testing — see
    calibrate_plc_weights()'s docstring. It also returns a flat MAX_SCORE
    if fewer than 150 ops have happened yet; windowed_score() mirrors
    that.
  - `Peer::_updateStats()` calls GetLastNeteqScore() once per second (a
    1000ms repeating job — `_monitorConfirmedCallJob`/`JobEvent(1000,
    ...)`) and feeds each point-in-time score into a running arithmetic
    mean (`MathFloatStats::writeValue()`: `_avg = _totalValue /
    _totalSample`, equal-weighted, no decay). The final reported score is
    that mean over every one-second sample across the whole call, not a
    single end-of-call snapshot — per_second_average_score() reproduces
    this: sample windowed_score() at op index 100, 200, 300, ... and mean
    the results.

Older pulled .txt files (before per-op logging was added) only have final
aggregate mode counts (`kNormal: 495`, etc., plus a `neteq: X.XXXXX`
line) — no ordered per-op history. Those are still parsed and scored with
a whole-call, count-weighted approximation (`compute_v1_score()`), which
is what this script used exclusively before. It's a strictly worse
approximation, kept only so old archived runs still produce a number.

PLC-off runs are ALWAYS scored with V1_WEIGHTS_ORIGINAL, untouched — the
app's own constants, and the fixed reference everything else is measured
against. PLC-on runs are scored with V1_WEIGHTS_CALIBRATED, a separate
table solved (see --calibrate) so that score_on(calibrated) lands close to
score_off(original) for the same network condition, instead of just
applying one shared table to both sides and reporting whatever gap falls
out.

Usage:
    python3 neteq_eval.py [root_dir] [--csv out.csv] [--sweep-progress] [--calibrate]

    root_dir defaults to scanning both /home/dangnp/workspace/tmp/audio and
    frontend/loss-simulator/public/audio — walks every test-result folder,
    parses its .txt NetEq log, computes neteq.v1, and prints a report
    grouped by network condition so PLC-on and PLC-off runs of the same
    condition sit side by side.
    --sweep-progress reports how much of the current full sweep (see
    SWEEP_NETWORKS/SWEEP_LOSS/SWEEP_DELAY) is done and the exact `full:N`
    to resume an interrupted run, instead of working that out by hand.
    --calibrate re-solves V1_WEIGHTS_CALIBRATED from whatever paired
    PLC-on/PLC-off data is currently pulled, and explains the result. It
    only prints the numbers — copy them into V1_WEIGHTS_CALIBRATED (and,
    to actually change app behavior, into neteq_impl.cc) by hand.
"""

import argparse
import csv
import os
import re
import sys
from collections import Counter

MODE_KEYS = [
    "kNormal", "kCodecPlc", "kExpand", "kMerge",
    "kAccelerateSuccess", "kAccelerateLowEnergy", "kAccelerateFail",
    "kPreemptiveExpandSuccess", "kPreemptiveExpandLowEnergy", "kPreemptiveExpandFail",
    "kDefault",
]
MODE_INDEX = {k: i for i, k in enumerate(MODE_KEYS)}

# Per-mode v1 penalty weights, taken directly from the deployed constants
# in common_types.cc (NeteqScore::neteqPenV1) — NOT the values hardcoded in
# an earlier version of the neteq_impl.cc switch statement, which is now
# stale: kAccelerateLowEnergy is 0.1 in the real deployed struct, not 0.5.
# This is the fixed reference table PLC-off is always scored with —
# scoring PLC-on uses V1_WEIGHTS_CALIBRATED below instead. kMerge is
# included for structural symmetry with the C++ even though it never
# fires in PLC-on data (see calibrate_plc_weights()). kAccelerateSuccess
# is hardcoded to 0.5f directly in the switch (not read from the struct)
# — its struct entry is dead code, but the effective value still matches.
V1_WEIGHTS_ORIGINAL = {
    "kNormal": 0.0,
    "kCodecPlc": 0.25,
    "kExpand": 0.25,
    "kMerge": 0.10,
    "kAccelerateSuccess": 0.5,
    "kAccelerateLowEnergy": 0.1,
    "kAccelerateFail": 0.0,
    "kPreemptiveExpandSuccess": 0.10,
    "kPreemptiveExpandLowEnergy": 0.05,
    "kPreemptiveExpandFail": 0.0,
    "kDefault": 0.0,
}

# PLC-on-only weight table, solved by --calibrate against real paired
# PLC-on/PLC-off sweep data (see calibrate_plc_weights()) so that the
# *windowed* v1 score (not a whole-call average) comes out close to
# PLC-off's for the same network condition. PLC-off always stays on
# V1_WEIGHTS_ORIGINAL, untouched. Update this constant by hand from
# --calibrate's output if the sweep data changes meaningfully.
V1_WEIGHTS_CALIBRATED = {
    "kNormal": 0.0,
    "kCodecPlc": 0.346649,
    "kExpand": 0.25,
    "kMerge": 0.10,
    "kAccelerateSuccess": 0.5,
    "kAccelerateLowEnergy": 0.1,
    "kAccelerateFail": 0.0,
    "kPreemptiveExpandSuccess": 0.10,
    "kPreemptiveExpandLowEnergy": 0.05,
    "kPreemptiveExpandFail": 0.0,
    "kDefault": 0.0,
}

MAX_SCORE = 5.0
WINDOW = 150  # mirrors plc_ratio_history_'s cap in neteq_impl.cc
OPS_PER_SECOND = 100  # CalculateScore() runs once per 10ms GetAudio() call — see module docstring

# Modes whose v1 contribution ACCUMULATES onto the running value instead of
# resetting it — the only two the C++ switch handles with `+=`.
ACCUMULATE_MODES = {"kCodecPlc", "kExpand"}

FOLDER_PATTERN = re.compile(
    r"^en-(?P<complexity>\d+)_dec-(?P<decComplexity>\d+)_"
    r"(?P<plc>plc|normal)_dred-(?P<dredDuration>\d+)_"
    r"(?:(?P<network>.+)_loss-(?P<loss>\d+)_rtt-(?P<rtt>\d+)_)?"
    r"(?P<timestamp>\d{2}-\d{2}-\d{4}_\d{6})$"
)


def parse_mode_sequence(path):
    """
    New log format: one NetEq mode ID (0-10, MODE_KEYS order) per line, in
    the exact order the app processed them. Returns the sequence as mode
    name strings, or None if the file doesn't look like this format (e.g.
    an older aggregate-count file — see parse_neteq_file()).
    """
    modes = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not line.lstrip("-").isdigit():
                return None
            idx = int(line)
            if not (0 <= idx < len(MODE_KEYS)):
                return None
            modes.append(MODE_KEYS[idx])
    return modes


def simulate_v1(mode_sequence, weights):
    """Replay plc_accumulate_ratio_.v1 exactly as neteq_impl.cc does. Returns the full per-op v1 history."""
    v1 = 0.0
    history = []
    for mode in mode_sequence:
        if mode in ACCUMULATE_MODES:
            v1 += weights[mode]
        else:
            v1 = weights[mode]
        if v1 < 0.0:
            v1 = 0.0
        elif v1 > MAX_SCORE:
            v1 = MAX_SCORE
        history.append(v1)
    return history


def windowed_score(history, window=WINDOW):
    """Reproduces GetLastNeteqScore() exactly — see module docstring for the formula/why."""
    if len(history) < window:
        return MAX_SCORE
    tail = history[-window:]
    mean_v1 = sum(tail) / len(tail)
    scaled = max(0.0, min(100.0, 100.0 * mean_v1))
    return (100.0 - scaled) / 20.0


def per_second_average_score(history, ops_per_second=OPS_PER_SECOND, window=WINDOW):
    """
    Reproduces the app's actual reported score: GetLastNeteqScore() sampled
    once a second for the whole call, averaged (plain arithmetic mean, no
    decay — see module docstring). Not the same as windowed_score() on the
    full history, which only reflects the trailing 150 ops at the very end.
    """
    n = len(history)
    num_seconds = n // ops_per_second
    if num_seconds == 0:
        return MAX_SCORE
    total = 0.0
    for k in range(1, num_seconds + 1):
        total += windowed_score(history[:k * ops_per_second], window)
    return total / num_seconds


def parse_neteq_file(path):
    """Older format: read a pulled NetEq .txt stat file into {mode: count, 'neteq': float}."""
    counts = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            try:
                counts[key] = float(value) if key == "neteq" else int(value)
            except ValueError:
                continue
    return counts


def compute_v1_score(counts, weights=V1_WEIGHTS_ORIGINAL):
    """Whole-call, count-weighted v1 penalty score, for older aggregate-only files. Returns (score, per-mode contribution)."""
    total_ops = sum(counts.get(k, 0) for k in MODE_KEYS)
    breakdown = {}
    if total_ops == 0:
        return MAX_SCORE, {k: 0.0 for k in MODE_KEYS}

    penalty = 0.0
    for mode in MODE_KEYS:
        contribution = weights[mode] * counts.get(mode, 0) / total_ops
        breakdown[mode] = contribution
        penalty += contribution

    score = max(0.0, min(MAX_SCORE, MAX_SCORE - penalty))
    return score, breakdown


def find_results(root):
    """Walk root_dir for pulled test-result folders, parsing their name + .txt log."""
    results = []
    if not os.path.isdir(root):
        return results

    for name in sorted(os.listdir(root)):
        folder = os.path.join(root, name)
        if not os.path.isdir(folder):
            continue
        match = FOLDER_PATTERN.match(name)
        if not match:
            continue

        txt_files = [f for f in os.listdir(folder) if f.endswith(".txt")]
        if not txt_files:
            continue

        txt_path = os.path.join(folder, txt_files[0])
        is_plc = match.group("plc") == "plc"
        weights = V1_WEIGHTS_CALIBRATED if is_plc else V1_WEIGHTS_ORIGINAL

        mode_sequence = parse_mode_sequence(txt_path)
        if mode_sequence is not None:
            counts = Counter(mode_sequence)
            score = per_second_average_score(simulate_v1(mode_sequence, weights))
            app_neteq = None
        else:
            counts = parse_neteq_file(txt_path)
            app_neteq = counts.get("neteq")
            score, _ = compute_v1_score(counts, weights)

        info = match.groupdict()
        results.append({
            "folder": name,
            "plc": is_plc,
            "network": info["network"] or "",
            "loss": int(info["loss"]) if info["loss"] else None,
            "rtt": int(info["rtt"]) if info["rtt"] else None,
            "counts": dict(counts),
            "app_neteq": app_neteq,
            "neteq_v1": score,
            "mode_sequence": mode_sequence,
        })
    return results


# Mirrors the frontend's sweep design (ConfigAndRun.vue's
# generateFullSweepConfigs() + constant.js's EVAL_NETWORK_TYPE /
# EVAL_SUBCASE_LOSS / EVAL_SUBCASE_DELAY). Keep these in sync by hand if
# that grid changes — there's no shared source of truth between the JS and
# this script. Order matters: it must match the generator's loop order
# (plc=true block first, then plc=false; network outer, loss, then rtt
# innermost) since sweep_progress() reconstructs each case's index the
# same way generateFullSweepConfigs() assigns it.
SWEEP_NETWORKS = [
    "2G-DevelopingRural", "2G-DevelopingUrban", "3G-Average", "3G-Good", "3G-Poor",
    "4G-Average", "4G-Good", "4G-Poor", "5G-Average", "5G-Good", "5G-Poor",
    "Cable", "DSL", "Edge-Average", "Edge-Good", "Edge-Lossy",
    "Wifi-Average", "Wifi-Good", "Wifi-Poor",
]
SWEEP_LOSS = [0, 5, 10, 15, 20, 30, 40, 50, 70, 90]
SWEEP_DELAY = [50, 160, 400, 1200]

# 5 extra fixed (loss, rtt) pairs tacked onto the cross product per
# network — must mirror ConfigAndRun.vue's EXTRA_CASES exactly (same
# pairs, same order), since sweep_case_index()/sweep_case_from_index()
# reconstruct each case's index by appending these after the cross
# product, same as generateFullSweepConfigs() does.
EXTRA_CASES = [(5, 80), (10, 120), (20, 200), (30, 300), (50, 600)]

# Every (loss, rtt) combo tested per network: the full cross product,
# then the 5 extras — order matters, it's the source of truth for indices.
_SWEEP_COMBOS_FULL = [(loss, rtt) for loss in SWEEP_LOSS for rtt in SWEEP_DELAY] + EXTRA_CASES

# TEMP: shrink "full" to 1/4 size for a quick pass — set back to 1 to
# restore the full sweep. Must match ConfigAndRun.vue's TEMP_SWEEP_STRIDE.
TEMP_SWEEP_STRIDE = 4
SWEEP_COMBOS = _SWEEP_COMBOS_FULL[::TEMP_SWEEP_STRIDE]


def sweep_case_index(plc, network, loss, rtt):
    """Same index a case gets in generateFullSweepConfigs()'s loop order."""
    net_idx = SWEEP_NETWORKS.index(network)
    combo_idx = SWEEP_COMBOS.index((loss, rtt))
    per_network = len(SWEEP_COMBOS)
    plc_offset = 0 if plc else len(SWEEP_NETWORKS) * per_network
    return plc_offset + net_idx * per_network + combo_idx


def sweep_progress(results):
    """
    Compare pulled results against the full expected (plc, network, loss,
    rtt) grid and report what's still missing — for continuing an
    interrupted "full" sweep without re-testing what's already done.

    Returns a dict: total, done (count), missing (sorted list of case-index
    ints), and resume_skip — set only when the missing set is a clean
    contiguous suffix (nothing done past the first gap), in which case
    `full:{resume_skip}` in the UI resumes exactly where it left off. When
    the missing set is scattered instead, resume_skip is None and the
    caller should look at `missing` (or the (network, loss, rtt) form)
    directly.
    """
    combo_set = set(SWEEP_COMBOS)
    total = len(SWEEP_NETWORKS) * len(SWEEP_COMBOS) * 2
    done = set()
    for r in results:
        if r["network"] not in SWEEP_NETWORKS or (r["loss"], r["rtt"]) not in combo_set:
            continue  # not part of the current sweep grid (e.g. an older/ad-hoc test)
        done.add(sweep_case_index(r["plc"], r["network"], r["loss"], r["rtt"]))

    missing = sorted(set(range(total)) - done)
    resume_skip = None
    if missing and all(i not in done for i in range(missing[0], total)):
        resume_skip = missing[0]

    return {"total": total, "done": len(done), "missing": missing, "resume_skip": resume_skip}


def sweep_case_from_index(idx):
    """Inverse of sweep_case_index() — (plc, network, loss, rtt) for a case index."""
    per_network = len(SWEEP_COMBOS)
    per_plc = len(SWEEP_NETWORKS) * per_network
    plc = idx < per_plc
    idx = idx % per_plc
    net_idx, combo_idx = divmod(idx, per_network)
    loss, rtt = SWEEP_COMBOS[combo_idx]
    return plc, SWEEP_NETWORKS[net_idx], loss, rtt


def print_report(results):
    grouped = {}
    for r in results:
        key = (r["network"], r["loss"], r["rtt"])
        grouped.setdefault(key, {}).setdefault(r["plc"], []).append(r)

    header = f"{'network':<20}{'loss':>6}{'rtt':>6}  {'plc.v1':>8}  {'off.v1':>8}  {'delta':>8}"
    print(header)
    print("-" * len(header))

    for (network, loss, rtt), by_plc in sorted(grouped.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)):
        plc_scores = [r["neteq_v1"] for r in by_plc.get(True, [])]
        off_scores = [r["neteq_v1"] for r in by_plc.get(False, [])]
        plc_avg = sum(plc_scores) / len(plc_scores) if plc_scores else None
        off_avg = sum(off_scores) / len(off_scores) if off_scores else None
        delta = (plc_avg - off_avg) if (plc_avg is not None and off_avg is not None) else None

        fmt = lambda v: f"{v:8.3f}" if v is not None else f"{'--':>8}"
        print(f"{network:<20}{loss!s:>6}{rtt!s:>6}  {fmt(plc_avg)}  {fmt(off_avg)}  {fmt(delta)}")


def write_csv(results, path):
    fieldnames = ["folder", "plc", "network", "loss", "rtt", "app_neteq", "neteq_v1"] + MODE_KEYS
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row = {
                "folder": r["folder"], "plc": r["plc"], "network": r["network"],
                "loss": r["loss"], "rtt": r["rtt"],
                "app_neteq": r["app_neteq"], "neteq_v1": round(r["neteq_v1"], 5),
            }
            row.update({k: r["counts"].get(k, 0) for k in MODE_KEYS})
            writer.writerow(row)


# --- Calibration -------------------------------------------------------
#
# kCodecPlc is the only free weight. Why not tune the others too?
#   - kMerge never fires in any pulled PLC-on sample (0/855 files) —
#     WebRTC's own merge-back step doesn't run when the codec's PLC
#     already concealed the loss — so it's structurally unidentifiable
#     from PLC-on data.
#   - kExpand, kAccelerateSuccess/LowEnergy, kPreemptiveExpandSuccess/
#     LowEnergy each fire in only a few dozen to ~100 ops out of ~2000+
#     per PLC-on run (kExpand: 252 occurrences total across all 855
#     PLC-on runs). An earlier attempt at solving all of them jointly via
#     per-sample least squares pushed several of these straight to
#     arbitrary search bounds for barely any improvement in per-sample
#     fit — that's the optimizer chasing sample noise on thin-signal
#     modes, not a real calibration.
#   - kCodecPlc, by contrast, is well identified: it's the dominant mode
#     in essentially every PLC-on run (25-60% of all ops), so its weight
#     alone moves the average windowed score smoothly and predictably.
#
# So instead of a multi-parameter fit, this solves the ONE lever that
# actually matters: the kCodecPlc weight that makes PLC-on's average
# windowed v1 score match PLC-off's average, across the whole sweep.
#
# Two corrections were needed to get here, both found by comparing this
# script's numbers against real app behavior instead of trusting the
# model in isolation:
#   1. A first pass (before GetLastNeteqScore()'s real formula was known)
#      used the wrong score transform — plain `MAX_SCORE - mean_v1`
#      instead of the real `MAX_SCORE - 5*mean_v1` (clamped) — and came
#      out to kCodecPlc=0.59. Applied for real, that overshot badly (PLC
#      scored WORSE than off by ~0.6-0.8 across three spot-check
#      conditions), because the real formula is 5x more sensitive to
#      mean_v1 than the wrong one.
#   2. The score isn't a single end-of-call snapshot either — it's
#      GetLastNeteqScore() sampled once a second for the whole call and
#      averaged (see per_second_average_score()). Re-solving with both
#      fixes against the same 855 paired samples: kCodecPlc=0.346649 (was
#      ~0.37 with fix #1 alone, 0.59 with neither).
CALIBRATION_FREE_MODE = "kCodecPlc"
CALIBRATION_SEARCH_BOUNDS = (0.05, 2.0)


def _weights_to_vector(weights):
    import numpy as np
    v = np.zeros(len(MODE_KEYS))
    for k, val in weights.items():
        v[MODE_INDEX[k]] = val
    return v


def _simulate_scores_vectorized(mode_code_arrays, weight_vector, window=WINDOW, ops_per_second=OPS_PER_SECOND):
    """
    Vectorized re-implementation of simulate_v1() + per_second_average_score(),
    used only because --calibrate needs thousands of full-sweep evaluations
    (grid search) and the plain per-op Python loop is too slow for that.
    Verified to match the plain per-op version to floating-point precision.

    Exploits that v1's raw (unclamped) trajectory within any maximal run of
    consecutive accumulate-type ops is a plain running sum (weights are
    non-negative, so clamping only ever needs applying once at the end, not
    re-derived step by step) — this turns the sequential recurrence into a
    handful of array-wide numpy ops per sample. The per-second sampling is
    then just prefix-sum lookups at each 1-second op index instead of
    re-slicing/re-averaging the tail from scratch every time.
    """
    import numpy as np
    scores = np.empty(len(mode_code_arrays))
    accumulate_ids = {MODE_INDEX[m] for m in ACCUMULATE_MODES}
    for i, codes in enumerate(mode_code_arrays):
        n = len(codes)
        per_pos = weight_vector[codes]
        accumulate_mask = np.isin(codes, list(accumulate_ids))
        reset_mask = ~accumulate_mask
        acc_values = np.where(accumulate_mask, per_pos, 0.0)
        global_cumsum = np.cumsum(acc_values)
        reset_idx = np.where(reset_mask, np.arange(n), -1)
        last_reset_idx = np.maximum.accumulate(reset_idx)
        safe_idx = np.maximum(last_reset_idx, 0)
        base_cumsum = np.where(last_reset_idx >= 0, global_cumsum[safe_idx], 0.0)
        entering_value = np.where(last_reset_idx >= 0, per_pos[safe_idx], 0.0)
        unclamped = entering_value + (global_cumsum - base_cumsum)
        v1_accum = np.clip(unclamped, 0.0, MAX_SCORE)
        v1 = np.where(accumulate_mask, v1_accum, per_pos)
        v1 = np.clip(v1, 0.0, MAX_SCORE)

        num_seconds = n // ops_per_second
        if num_seconds == 0:
            scores[i] = MAX_SCORE
            continue
        prefix = np.concatenate(([0.0], np.cumsum(v1)))
        idxs = np.arange(ops_per_second, num_seconds * ops_per_second + 1, ops_per_second)
        per_second_scores = np.full(len(idxs), MAX_SCORE)
        valid = idxs >= window
        if valid.any():
            vi = idxs[valid]
            mean_v1 = (prefix[vi] - prefix[vi - window]) / window
            scaled = np.clip(100.0 * mean_v1, 0.0, 100.0)
            per_second_scores[valid] = (100.0 - scaled) / 20.0
        scores[i] = per_second_scores.mean()
    return scores


def calibrate_plc_weights(results, window=WINDOW):
    """
    Solve the kCodecPlc weight (see CALIBRATION_FREE_MODE's docstring for
    why it's the only free parameter) so that PLC-on's average *windowed*
    v1 score (simulate_v1() + windowed_score(), not a whole-call average)
    matches PLC-off's average, across every condition in the current
    sweep that has both a PLC-on and PLC-off pull. PLC-off is never
    touched — always scored with V1_WEIGHTS_ORIGINAL.

    This is a 1D monotonic search (more kCodecPlc weight -> strictly lower
    average PLC-on score), done directly on the real clamped simulator via
    _simulate_scores_vectorized() rather than any linear/closed-form
    approximation — the clamp to [0, MAX_SCORE] binds constantly on the
    sweep's higher-loss conditions (long kCodecPlc runs saturate v1 and
    stay there), so the relationship isn't linear in the weight.
    """
    import numpy as np

    off = [r for r in results if not r["plc"] and r["mode_sequence"] is not None]
    plc = [r for r in results if r["plc"] and r["mode_sequence"] is not None]
    if not off or not plc:
        return None

    off_scores = np.array([r["neteq_v1"] for r in off])
    off_mean = float(off_scores.mean())
    mode_code_arrays = [np.array([MODE_INDEX[m] for m in r["mode_sequence"]]) for r in plc]

    def plc_scores_for(codec_plc_weight):
        weights = dict(V1_WEIGHTS_ORIGINAL)
        weights["kCodecPlc"] = codec_plc_weight
        wv = _weights_to_vector(weights)
        return _simulate_scores_vectorized(mode_code_arrays, wv, window)

    baseline_scores = plc_scores_for(V1_WEIGHTS_ORIGINAL["kCodecPlc"])

    # Coarse grid over the full bounds, then a fine grid zoomed into the
    # coarse winner's neighborhood — plc_scores_for() is monotonic in the
    # weight (more kCodecPlc -> strictly lower score, confirmed empirically),
    # so narrowing around the coarse optimum can't skip past a better one.
    # Picks the value with the smallest |gap| to full float precision,
    # not rounded to some fixed number of decimals.
    lo, hi = CALIBRATION_SEARCH_BOUNDS
    best_val, best_gap = None, None
    for val in np.linspace(lo, hi, 400):
        gap = float(plc_scores_for(val).mean()) - off_mean
        if best_gap is None or abs(gap) < abs(best_gap):
            best_val, best_gap = float(val), gap
    coarse_step = (hi - lo) / 399
    fine_lo, fine_hi = max(lo, best_val - coarse_step), min(hi, best_val + coarse_step)
    for val in np.linspace(fine_lo, fine_hi, 2001):
        gap = float(plc_scores_for(val).mean()) - off_mean
        if abs(gap) < abs(best_gap):
            best_val, best_gap = float(val), gap
    final_scores = plc_scores_for(best_val)

    weights = dict(V1_WEIGHTS_ORIGINAL)
    weights["kCodecPlc"] = best_val

    return {
        "weights": weights,
        "n_off": len(off),
        "n_plc": len(plc),
        "off_mean": off_mean,
        "off_std": float(off_scores.std()),
        "baseline_plc_mean": float(baseline_scores.mean()),
        "baseline_plc_std": float(baseline_scores.std()),
        "final_plc_mean": float(final_scores.mean()),
        "final_plc_std": float(final_scores.std()),
        "residual_gap": best_gap,
    }


def print_calibration(result):
    if result is None:
        print("No paired PLC-on/PLC-off samples with the new per-op log format found — can't calibrate.", file=sys.stderr)
        return

    print(f"Calibrated kCodecPlc against {result['n_plc']} PLC-on runs vs. {result['n_off']} PLC-off runs (full sweep).\n")
    print(f"{'':<22}{'off (fixed)':>14}{'plc, original':>16}{'plc, calibrated':>18}")
    print(f"{'kCodecPlc weight':<22}{V1_WEIGHTS_ORIGINAL['kCodecPlc']:>14.2f}{V1_WEIGHTS_ORIGINAL['kCodecPlc']:>16.2f}{result['weights']['kCodecPlc']:>18.6f}")
    print(f"{'avg windowed v1':<22}{result['off_mean']:>14.4f}{result['baseline_plc_mean']:>16.4f}{result['final_plc_mean']:>18.4f}")
    print(f"{'std windowed v1':<22}{result['off_std']:>14.4f}{result['baseline_plc_std']:>16.4f}{result['final_plc_std']:>18.4f}")
    print(f"\nresidual gap (plc - off) after calibration: {result['residual_gap']:+.5f}  (was {result['baseline_plc_mean']-result['off_mean']:+.5f} at the original weight)")
    std_diff = result['final_plc_std'] - result['off_std']
    print(
        f"\nSpread (std) after calibration: plc {result['final_plc_std']:.4f} vs. off "
        f"{result['off_std']:.4f} ({'+' if std_diff >= 0 else ''}{std_diff:.4f}) — only the "
        "average is being matched here; a single weight can't also force the "
        "per-condition spread to match, so this is reported, not corrected."
    )
    print(f"\nCopy into V1_WEIGHTS_CALIBRATED: kCodecPlc = {result['weights']['kCodecPlc']:.6f}")


# Results get split across two locations by runTests()'s every-50-tests
# move: whatever hasn't hit that threshold yet stays in public/audio, the
# rest gets moved to the hardcoded tmp path. Scan both by default so nothing
# gets missed.
DEFAULT_ROOTS = [
    "/home/dangnp/workspace/tmp/audio",
    os.path.join(os.path.dirname(__file__), "frontend/loss-simulator/public/audio"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "root_dir", nargs="?",
        help="Folder containing pulled test-result subfolders. Default: scan both "
             "/home/dangnp/workspace/tmp/audio and frontend/loss-simulator/public/audio.",
    )
    parser.add_argument("--csv", help="Also write the per-test breakdown to this CSV path")
    parser.add_argument(
        "--sweep-progress", action="store_true",
        help="Report how much of the current full loss x rtt sweep (see SWEEP_NETWORKS/"
             "SWEEP_LOSS/SWEEP_DELAY) is done vs. still missing, and the exact `full:N` "
             "skip value to resume an interrupted run, instead of eyeballing folder names.",
    )
    parser.add_argument(
        "--calibrate", action="store_true",
        help="Re-solve V1_WEIGHTS_CALIBRATED from the currently pulled paired PLC-on/"
             "PLC-off data and print the result with an explanation, instead of the "
             "normal report.",
    )
    args = parser.parse_args()

    roots = [args.root_dir] if args.root_dir else DEFAULT_ROOTS
    results = [r for root in roots for r in find_results(root)]
    if not results:
        print(f"No matching result folders found under {roots}", file=sys.stderr)
        return 1

    if args.calibrate:
        print_calibration(calibrate_plc_weights(results))
        return 0

    if args.sweep_progress:
        progress = sweep_progress(results)
        print(f"done: {progress['done']}/{progress['total']}")
        if not progress["missing"]:
            print("Nothing missing — the sweep is complete.")
        elif progress["resume_skip"] is not None:
            last_done = sweep_case_from_index(progress["resume_skip"] - 1)
            print(f"Clean contiguous resume point. Last completed: {last_done}")
            print(f"Type full:{progress['resume_skip']} to resume exactly where it left off.")
        else:
            print(f"{len(progress['missing'])} scattered cases missing (not a clean prefix/suffix):")
            for idx in progress["missing"][:50]:
                print(" ", sweep_case_from_index(idx))
            if len(progress["missing"]) > 50:
                print(f"  ... and {len(progress['missing']) - 50} more")
        return 0

    print_report(results)

    if args.csv:
        write_csv(results, args.csv)
        print(f"\nWrote {len(results)} rows to {args.csv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


'''
Verified against the real source (~/workspace/zrtc_core/zrtc/webrtc/), as
of the kCodecPlc=0.59 test:
  - modules/audio_coding/neteq/neteq_impl.cc: CalculateScore() (the switch
    below) and GetLastNeteqScore() (the actual history->score formula).
  - common_types.cc: NeteqScore::neteqPenV1 / neteqPenV2 (the deployed
    constants) and NeteqScore::parseSingleNeteq() (the isDeepPlc override
    that sets kCodecPlcPen = 0.59 for "NeteqV1Score" — this is how the PLC
    build's 0.59 gets applied at runtime, not a hardcoded literal).

Two things this script's V1_WEIGHTS_ORIGINAL/CALIBRATED intentionally do
NOT try to reproduce, since they're bugs/dead code in the app rather than
real behavior to model:
  - Mode::kAccelerateSuccess never calls appendNetEqMode(4) — v1/v2 update
    same as always, but that op is silently missing from the per-op log,
    not recorded as any other mode either. Any per-op sequence parsed from
    a pulled .txt file undercounts kAccelerateSuccess.
  - Mode::kAccelerateSuccess also doesn't read NeteqScore::neteqPenV1's
    kAccelerateSuccessPen field — it uses the literal 0.5f directly, so
    changing that struct field would have no effect. It happens to equal
    the struct's value (0.5), so this doesn't change any numbers here.

NeteqScore NetEqImpl::GetLastNeteqScore() {
    NetEqScore ret({ 5.0f, 5.0f });
    rtc::CritScope lock(&plc_ratio_history_mutex_);
    if (plc_ratio_history_.size() < 150)  return ret;
    float c1 = 0, c2 = 0;
    for (auto plc_ratio : plc_ratio_history_) {
        c1 += plc_ratio.v1;
        c2 += plc_ratio.v2;
    }
    auto retV1 = (100 * c1 / plc_ratio_history_.size());
    retV1 = std::min(std::max(retV1, 0.0f), 100.0f);
    retV1 = (100 - retV1) / 20;
    ret.v1 = retV1;
    auto retV2 = (100 * c2 / plc_ratio_history_.size());
    retV2 = std::min(std::max(retV2, 0.0f), 100.0f);
    retV2 = (100 - retV2) / 20;
    ret.v2 = retV2;
    return ret;
}

// common_types.cc
NeteqScore::NeteqPenaltyScore NeteqScore::neteqPenV1 = {
    0.0f,       // kNormalPen
    0.25f,      // kCodecPlcPen  (overridden to 0.59 for isDeepPlc builds
                //                by parseSingleNeteq() — see below)
    0.25f,      // kExpandPen
    0.10f,      // kMergePen
    0.5f,       // kAccelerateSuccessPen  (dead — switch uses 0.5f literal)
    0.1f,       // kAccelerateLowEnergyPen
    0.0f,       // kAccelerateFailPen
    0.10f,      // kPreemptiveExpandSuccessPen
    0.05f,      // kPreemptiveExpandLowEnergyPen
    0.0f,       // kPreemptiveExpandFailPen
};

void NeteqScore::parseSingleNeteq(const std::string version, bool isDeepPlc) {
  auto& target = GetTargetNeteqVersion(version == "NeteqV1Score");
  if (version == "NeteqV1Score" && isDeepPlc) {
    target.kCodecPlcPen = 0.59;  // <- change this to 0.346649, see calibrate_plc_weights()
  }
  // override the above value as well
}

void NetEqImpl::CalculateScore()
{
  static float score_penalty_by_voice_bandwidth[] = { 0.0f, /*4khz=*/0.2547f, /*6khz=*/0.1926f , /*8khz=*/0.1305f , /*12khz=*/0.0684f , /*20khz=*/0.0f };
    auto last_output_type = LastOutputType();
    //RTC_LOG(LS_INFO) << "last_mode_=" << (int)last_mode_ << ",last_voice_bandwidth_=" << last_voice_bandwidth_ << ", last_output_type=" << (int)last_output_type;
	switch (last_mode_) {
	case Mode::kNormal:
    plc_accumulate_ratio_.v1 = NeteqScore::neteqPenV1.kNormalPen;
    plc_accumulate_ratio_.v2 = NeteqScore::neteqPenV2.kNormalPen;
    webrtc::WebrtcStats::appendNetEqMode(0);
		break;
	case Mode::kCodecPlc:
	    // same as Mode::Expand but this mode get less penalty points
	    // if decode Plc fails -> add 0.3 to current history
	    // the more points you add to plc_accumulate_ratio_, the more penalty points you get in logged neteqScore
      webrtc::WebrtcStats::appendNetEqMode(1);
	    plc_accumulate_ratio_.v1 += NeteqScore::neteqPenV1.kCodecPlcPen;
	    plc_accumulate_ratio_.v2 += last_output_type == OutputType::kNormalSpeech ? 0.30f : NeteqScore::neteqPenV2.kCodecPlcPen;
      break;
	case Mode::kExpand:
    webrtc::WebrtcStats::appendNetEqMode(2);
    plc_accumulate_ratio_.v1 += NeteqScore::neteqPenV1.kExpandPen;
    plc_accumulate_ratio_.v2 += last_output_type == OutputType::kNormalSpeech ? 0.30f : NeteqScore::neteqPenV2.kExpandPen;
		break;
	case Mode::kMerge:
    webrtc::WebrtcStats::appendNetEqMode(3);
    plc_accumulate_ratio_.v1 = NeteqScore::neteqPenV1.kMergePen;
    plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.15f : NeteqScore::neteqPenV2.kMergePen;
		break;
	case Mode::kAccelerateSuccess:
	    // NOTE: no appendNetEqMode() call here — this op is silently
	    // missing from the per-op log (see comment above).
	    plc_accumulate_ratio_.v1 = 0.5f;  // NOTE: literal, ignores neteqPenV1.kAccelerateSuccessPen
	    plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.75f : 0.25f;
		break;
	case Mode::kAccelerateLowEnergy:
      webrtc::WebrtcStats::appendNetEqMode(5);
    	plc_accumulate_ratio_.v1 = NeteqScore::neteqPenV1.kAccelerateLowEnergyPen;
    	plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.75f : NeteqScore::neteqPenV2.kAccelerateLowEnergyPen;
    break;
	case Mode::kAccelerateFail:
    webrtc::WebrtcStats::appendNetEqMode(6);
    plc_accumulate_ratio_.v1 = NeteqScore::neteqPenV1.kAccelerateFailPen;
    plc_accumulate_ratio_.v2 = NeteqScore::neteqPenV2.kAccelerateFailPen;
		break;
	case Mode::kPreemptiveExpandSuccess:
    webrtc::WebrtcStats::appendNetEqMode(7);
    plc_accumulate_ratio_.v1 = NeteqScore::neteqPenV1.kPreemptiveExpandSuccessPen;
    plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.15f : NeteqScore::neteqPenV2.kPreemptiveExpandSuccessPen;
    break;
	case Mode::kPreemptiveExpandLowEnergy:
    webrtc::WebrtcStats::appendNetEqMode(8);
    plc_accumulate_ratio_.v1 = NeteqScore::neteqPenV1.kPreemptiveExpandLowEnergyPen;
    plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.10f : NeteqScore::neteqPenV2.kPreemptiveExpandLowEnergyPen;
		break;
	case Mode::kPreemptiveExpandFail:
    webrtc::WebrtcStats::appendNetEqMode(9);
    plc_accumulate_ratio_.v1 = NeteqScore::neteqPenV1.kPreemptiveExpandFailPen;
    plc_accumulate_ratio_.v2 = NeteqScore::neteqPenV2.kPreemptiveExpandFailPen;
		break;
	default:
    webrtc::WebrtcStats::appendNetEqMode(10);
    plc_accumulate_ratio_.v1 = 0.0f;
    plc_accumulate_ratio_.v2 = 0.0f;
		break;
	}

  if (last_voice_bandwidth_ >= 1 && last_voice_bandwidth_ <= 5) {
    plc_accumulate_ratio_.v2 = plc_accumulate_ratio_.v2 + score_penalty_by_voice_bandwidth[last_voice_bandwidth_];
  }

  plc_accumulate_ratio_.v1 = std::min(plc_accumulate_ratio_.v1, 5.0f);
  plc_accumulate_ratio_.v1 = std::max(plc_accumulate_ratio_.v1, 0.0f);
  plc_accumulate_ratio_.v2 = std::min(plc_accumulate_ratio_.v2, 5.0f);
  plc_accumulate_ratio_.v2 = std::max(plc_accumulate_ratio_.v2, 0.0f);
	{
		rtc::CritScope lock(&plc_ratio_history_mutex_);
		plc_ratio_history_.push_back(plc_accumulate_ratio_);
		if (plc_ratio_history_.size() > 150) plc_ratio_history_.pop_front();
	}
}
'''
