"""
NetEq penalty scoring.

The app's own "neteq" field (see the raw txt logs pulled into
frontend/loss-simulator/public/audio/*/) is a rolling average over only the
last ~150 decode operations of the call (see `plc_ratio_history_` in the
C++ snippet at the bottom of this file), computed from `plc_accumulate_ratio_.v1`.
That per-op penalty already weighs kCodecPlc and kExpand identically (0.25
each) — they represent the same underlying event ("this frame needed loss
concealment"), just handled by the codec's own PLC vs. NetEq's generic
expand depending on whether Opus PLC is enabled.

Because we only get final aggregate mode counts from the pulled .txt files
(not the ordered per-frame history), we can't reproduce the app's exact
windowed score. Instead this computes a whole-call, count-weighted average
using a per-mode weight table ("neteq.v1").

PLC-off runs are ALWAYS scored with V1_WEIGHTS_ORIGINAL, untouched — that's
the fixed reference. PLC-on runs are scored with a separate table,
V1_WEIGHTS_CALIBRATED, fit via `--calibrate` so that score_on(calibrated)
lands close to score_off(original) for the same network condition, instead
of just applying one shared table to both sides and reporting whatever gap
falls out. Re-run --calibrate and update the constant as more of the sweep
completes — see neteq_calibration.log for the last fit.

Usage:
    python3 neteq_eval.py [root_dir] [--csv out.csv] [--calibrate] [--log path]

    root_dir defaults to scanning both /home/dangnp/workspace/tmp/audio and
    frontend/loss-simulator/public/audio — walks every test-result folder,
    parses its .txt NetEq stats file, computes neteq.v1, and prints a report
    grouped by network condition so PLC-on and PLC-off runs of the same
    condition sit side by side. --calibrate re-derives the weight table
    instead of just reporting the gap; --log also writes it to a file.
"""

import argparse
import csv
import os
import re
import sys

MODE_KEYS = [
    "kNormal", "kCodecPlc", "kExpand", "kMerge",
    "kAccelerateSuccess", "kAccelerateLowEnergy", "kAccelerateFail",
    "kPreemptiveExpandSuccess", "kPreemptiveExpandLowEnergy", "kPreemptiveExpandFail",
    "kDefault",
]

# Per-mode v1 penalty weights, taken directly from the app's C++ NetEq
# stats update (see bottom of file). Independent of last_output_type,
# unlike the app's v2 variant, which we don't have enough data to reproduce.
# Kept only as the "original" reference column in --calibrate's report —
# scoring itself now defaults to V1_WEIGHTS_CALIBRATED below.
V1_WEIGHTS_ORIGINAL = {
    "kNormal": 0.0,
    "kCodecPlc": 0.25,
    "kExpand": 0.25,
    "kMerge": 0.10,
    "kAccelerateSuccess": 0.5,
    "kAccelerateLowEnergy": 0.5,
    "kAccelerateFail": 0.0,
    "kPreemptiveExpandSuccess": 0.10,
    "kPreemptiveExpandLowEnergy": 0.05,
    "kPreemptiveExpandFail": 0.0,
    "kDefault": 0.0,
}

# PLC-on-only weight table. Fit from `python3 neteq_eval.py --calibrate`
# against 1901 paired PLC-on/off samples from the full loss x rtt
# cross-product sweep, solving ONLY for how PLC-on runs get scored — the
# PLC-off side is always scored with V1_WEIGHTS_ORIGINAL, untouched, as the
# fixed reference (RMS delta of on-vs-off: 0.0127 with the original table
# applied to both sides, 0.0080 with this table applied to the on side).
# See neteq_calibration.log for the full report. Re-run --calibrate and
# update these as more of the sweep completes.
#
# Every mode except kNormal/kDefault (definitional/always-zero) is free —
# with the off side fixed, there's no risk of a free mode "explaining away"
# the gap by degrading the reference, so there's no need to anchor modes
# just to keep them from drifting (see ANCHORED_WEIGHTS). Used ONLY for
# PLC-on results — see compute_score_for_result().
V1_WEIGHTS_CALIBRATED = {
    "kNormal": 0.0,
    "kCodecPlc": 0.2598,
    "kExpand": 0.2419,
    "kMerge": 0.1218,
    "kAccelerateSuccess": 0.1110,
    "kAccelerateLowEnergy": 0.2872,
    "kAccelerateFail": 0.1371,
    "kPreemptiveExpandSuccess": 0.0802,
    "kPreemptiveExpandLowEnergy": 0.1421,
    "kPreemptiveExpandFail": 0.0637,
    "kDefault": 0.0,
}

MAX_SCORE = 5.0

FOLDER_PATTERN = re.compile(
    r"^en-(?P<complexity>\d+)_dec-(?P<decComplexity>\d+)_"
    r"(?P<plc>plc|normal)_dred-(?P<dredDuration>\d+)_"
    r"(?:(?P<network>.+)_loss-(?P<loss>\d+)_rtt-(?P<rtt>\d+)_)?"
    r"(?P<timestamp>\d{2}-\d{2}-\d{4}_\d{6})$"
)


def parse_neteq_file(path):
    """Read one pulled NetEq .txt stat file into {mode: count, 'neteq': float}."""
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
    """Whole-call, count-weighted v1 penalty score. Returns (score, per-mode contribution)."""
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
    """Walk root_dir for pulled test-result folders, parsing their name + .txt stats."""
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

        counts = parse_neteq_file(os.path.join(folder, txt_files[0]))
        is_plc = match.group("plc") == "plc"
        score, breakdown = compute_v1_score(counts, V1_WEIGHTS_CALIBRATED if is_plc else V1_WEIGHTS_ORIGINAL)

        info = match.groupdict()
        results.append({
            "folder": name,
            "plc": is_plc,
            "network": info["network"] or "",
            "loss": int(info["loss"]) if info["loss"] else None,
            "rtt": int(info["rtt"]) if info["rtt"] else None,
            "counts": counts,
            "app_neteq": counts.get("neteq"),
            "neteq_v1": score,
            "breakdown": breakdown,
        })
    return results


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



# Modes whose weight is anchored rather than fit. kNormal/kDefault=0 are
# definitional (no penalty for clean audio; kDefault never occurs in the
# data at all) — that's the only anchoring needed now. Since the off side
# is a fixed, untouched reference (see calibrate_weights()), a free mode
# can no longer "explain away" the gap by degrading that reference the
# way it could when both sides shared one weight table — so every other
# mode is safe to leave free. Add entries here only for modes you want
# pinned at their original value for some other reason.
ANCHORED_WEIGHTS = {
    "kNormal": 0.0,
    "kDefault": 0.0,
}


def _mode_frequencies(counts):
    total = sum(counts.get(k, 0) for k in MODE_KEYS)
    if total == 0:
        return {k: 0.0 for k in MODE_KEYS}
    return {k: counts.get(k, 0) / total for k in MODE_KEYS}


def calibrate_weights(results):
    """
    Solve for a PLC-on-only weight table (V1_WEIGHTS_CALIBRATED) such that
    score_on(calibrated) comes out approximately equal to score_off(original)
    for the same network condition. PLC-off is the fixed reference — always
    scored with V1_WEIGHTS_ORIGINAL, never touched — only the on side's
    weights are solved for.

    For every (network, loss, rtt) pair with both a PLC-on and a PLC-off
    result: target_penalty = the off side's penalty under the untouched
    original table (a fixed number per sample, no unknowns). On the on
    side, the anchored modes (see ANCHORED_WEIGHTS) also use their original
    value, so only the free modes' contribution is unknown:

        sum(w_free[m] * freq_on[m]) ~= target_penalty - sum(anchored[m] * freq_on[m])

    That's a standard (non-homogeneous) overdetermined linear system —
    least-squares-solve it for the free weights.
    """
    import numpy as np

    by_key = {}
    for r in results:
        key = (r["network"], r["loss"], r["rtt"])
        by_key.setdefault(key, {}).setdefault(r["plc"], []).append(r)

    free_modes = [m for m in MODE_KEYS if m not in ANCHORED_WEIGHTS]
    rows, rhs, pairs_used = [], [], []

    for key, by_plc in by_key.items():
        if True not in by_plc or False not in by_plc:
            continue
        freq_on = _mode_frequencies(by_plc[True][0]["counts"])
        freq_off = _mode_frequencies(by_plc[False][0]["counts"])

        target_penalty = sum(V1_WEIGHTS_ORIGINAL[m] * freq_off[m] for m in MODE_KEYS)
        anchored_contribution = sum(ANCHORED_WEIGHTS[m] * freq_on[m] for m in ANCHORED_WEIGHTS)

        rows.append([freq_on[m] for m in free_modes])
        rhs.append(target_penalty - anchored_contribution)
        pairs_used.append(key)

    if len(rows) < len(free_modes):
        print(
            f"Only {len(rows)} paired (PLC-on, PLC-off) samples available, "
            f"need at least {len(free_modes)} to fit {len(free_modes)} free weights. "
            "Run more of the PLC-off half of the sweep first.",
            file=sys.stderr,
        )
        return None, pairs_used

    A = np.array(rows)
    b = np.array(rhs)
    solved, *_ = np.linalg.lstsq(A, b, rcond=None)

    weights = dict(ANCHORED_WEIGHTS)
    weights.update({m: float(w) for m, w in zip(free_modes, solved)})
    return weights, pairs_used


def build_calibration_report(weights, results, pairs_used):
    """Build the calibration report as text (used for both console + log-file output)."""
    lines = [f"Fit against {len(pairs_used)} paired (PLC-on, PLC-off) samples.", ""]

    lines.append(f"{'mode':<28}{'original':>10}{'calibrated':>12}")
    for mode in MODE_KEYS:
        anchored = " (anchored)" if mode in ANCHORED_WEIGHTS else ""
        lines.append(f"{mode:<28}{V1_WEIGHTS_ORIGINAL[mode]:>10.4f}{weights[mode]:>12.4f}{anchored}")

    by_key = {}
    for r in results:
        key = (r["network"], r["loss"], r["rtt"])
        by_key.setdefault(key, {}).setdefault(r["plc"], []).append(r)

    lines.append("")
    lines.append(f"{'network':<20}{'loss':>6}{'rtt':>6}  {'old delta':>10}  {'new delta':>10}")
    total_old_sq, total_new_sq, n = 0.0, 0.0, 0
    for key in sorted(pairs_used, key=lambda k: (k[0], k[1] or 0)):
        network, loss, rtt = key
        on_counts = by_key[key][True][0]["counts"]
        off_counts = by_key[key][False][0]["counts"]
        old_on, _ = compute_v1_score(on_counts, V1_WEIGHTS_ORIGINAL)
        off_score, _ = compute_v1_score(off_counts, V1_WEIGHTS_ORIGINAL)  # off is always the fixed reference
        new_on, _ = compute_v1_score(on_counts, weights)
        old_delta, new_delta = old_on - off_score, new_on - off_score
        total_old_sq += old_delta ** 2
        total_new_sq += new_delta ** 2
        n += 1
        lines.append(f"{network:<20}{loss!s:>6}{rtt!s:>6}  {old_delta:>10.3f}  {new_delta:>10.3f}")

    lines.append("")
    lines.append(f"RMS delta: original={((total_old_sq / n) ** 0.5):.4f}  calibrated={((total_new_sq / n) ** 0.5):.4f}")
    return "\n".join(lines)


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
        "--calibrate", action="store_true",
        help="Solve for per-mode penalty weights that make PLC-on and PLC-off "
             "neteq.v1 scores approximately equal, instead of just listing them.",
    )
    parser.add_argument(
        "--log",
        help="With --calibrate, also write the weight table to this file "
             "(default: neteq_calibration.log next to this script).",
    )
    args = parser.parse_args()

    roots = [args.root_dir] if args.root_dir else DEFAULT_ROOTS
    results = [r for root in roots for r in find_results(root)]
    if not results:
        print(f"No matching result folders found under {roots}", file=sys.stderr)
        return 1

    if args.calibrate:
        weights, pairs_used = calibrate_weights(results)
        if weights is None:
            return 1
        report = build_calibration_report(weights, results, pairs_used)
        print(report)

        log_path = args.log if args.log else os.path.join(os.path.dirname(__file__), "neteq_calibration.log")
        with open(log_path, "w") as f:
            f.write(report + "\n")
        print(f"\nWrote calibration log to {log_path}")
    else:
        print_report(results)

    if args.csv:
        write_csv(results, args.csv)
        print(f"\nWrote {len(results)} rows to {args.csv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


'''
  static float score_penalty_by_voice_bandwidth[] = { 0.0f, /*4khz=*/0.2547f, /*6khz=*/0.1926f , /*8khz=*/0.1305f , /*12khz=*/0.0684f , /*20khz=*/0.0f };
    auto last_output_type = LastOutputType();
    //RTC_LOG(LS_INFO) << "last_mode_=" << (int)last_mode_ << ",last_voice_bandwidth_=" << last_voice_bandwidth_ << ", last_output_type=" << (int)last_output_type;
	switch (last_mode_) {
        case Mode::kNormal:
            plc_accumulate_ratio_.v1 = 0.0f;
            plc_accumulate_ratio_.v2 = 0.0f;
            webrtc::WebrtcStats::kNormal.increaseAndGet();
            break;
        case Mode::kCodecPlc:
            // same as Mode::Expand but this mode get less penalty points
            // if decode Plc fails -> add 0.3 to current history
            // the more points you add to plc_accumulate_ratio_, the more penalty points you get in logged neteqScore
            webrtc::WebrtcStats::kCodecPlc.increaseAndGet();
            plc_accumulate_ratio_.v1 += 0.25f;
            plc_accumulate_ratio_.v2 += last_output_type == OutputType::kNormalSpeech ? 0.30f : 0.15f;
            break;
        case Mode::kExpand:
            webrtc::WebrtcStats::kExpand.increaseAndGet();
            plc_accumulate_ratio_.v1 += 0.25f;
            plc_accumulate_ratio_.v2 += last_output_type == OutputType::kNormalSpeech ? 0.30f : 0.25f;
            break;
        case Mode::kMerge:
            webrtc::WebrtcStats::kMerge.increaseAndGet();
            plc_accumulate_ratio_.v1 = 0.10f;
            plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.15f : 0.10f;
            break;
        case Mode::kAccelerateSuccess:
            webrtc::WebrtcStats::kAccelerateSuccess.increaseAndGet();
            plc_accumulate_ratio_.v1 = 0.5f;
            plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.75f : 0.5f;
            break;
        case Mode::kAccelerateLowEnergy:
            webrtc::WebrtcStats::kAccelerateLowEnergy.increaseAndGet();
            plc_accumulate_ratio_.v1 = 0.5f;
            plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.75f : 0.5f;
            break;
        case Mode::kAccelerateFail:
            webrtc::WebrtcStats::kAccelerateFail.increaseAndGet();
            plc_accumulate_ratio_.v1 = 0.0f;
            plc_accumulate_ratio_.v2 = 0.0f;
            break;
        case Mode::kPreemptiveExpandSuccess:
            webrtc::WebrtcStats::kPreemptiveExpandSuccess.increaseAndGet();
            plc_accumulate_ratio_.v1 = 0.10f;
            plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.15f : 0.10f;
            break;
        case Mode::kPreemptiveExpandLowEnergy:
            webrtc::WebrtcStats::kPreemptiveExpandLowEnergy.increaseAndGet();
            plc_accumulate_ratio_.v1 = 0.05f;
            plc_accumulate_ratio_.v2 = last_output_type == OutputType::kNormalSpeech ? 0.10f : 0.05f;
            break;
        case Mode::kPreemptiveExpandFail:
            webrtc::WebrtcStats::kPreemptiveExpandFail.increaseAndGet();
            plc_accumulate_ratio_.v1 = 0.0f;
            plc_accumulate_ratio_.v2 = 0.0f;
            break;
        default:
            webrtc::WebrtcStats::kDefault.increaseAndGet();
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
    //RTC_LOG(LS_INFO) << "v1=" << plc_accumulate_ratio_.v1 << ", v2=" << plc_accumulate_ratio_.v2;
    {
        rtc::CritScope lock(&plc_ratio_history_mutex_);
        plc_ratio_history_.push_back(plc_accumulate_ratio_);
        if (plc_ratio_history_.size() > 150) plc_ratio_history_.pop_front();
    }
'''
