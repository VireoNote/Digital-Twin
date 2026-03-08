import json
import argparse
import sys

def analyze_shadow_logs(filepath: str):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)

    records = [json.loads(line) for line in lines if line.strip()]
    total_runs = len(records)
    if total_runs == 0:
        print("No shadow runs found.")
        sys.exit(0)

    # Metrics counters
    split_court_count = 0
    zero_band_count = 0
    tactical_band_count = 0
    hypothesis_thrash_count = 0
    supersede_count = 0
    divergence_count = 0

    # Delta Class breakdown
    delta_classes = {}

    for r in records:
        if r.get("split_court_detected"):
            split_court_count += 1
            
        c_mode = r.get("compiler_mode")
        if c_mode == "frozen" or r.get("band_width", 1.0) == 0.0:
            zero_band_count += 1
        elif c_mode == "tactical_only":
            tactical_band_count += 1
            
        # Mock logic for thrash: if it goes from emerging direct to challenged
        if r.get("lifecycle_transition", "").endswith("challenged"):
            hypothesis_thrash_count += 1
            
        if r.get("superseded"):
            supersede_count += 1
            
        if r.get("shadow_vs_legacy_diverged"):
            divergence_count += 1
            
        d_class = r.get("decision_delta_class", "unknown")
        delta_classes[d_class] = delta_classes.get(d_class, 0) + 1

    print("==================================================")
    print(f" SHADOW COMPILER METRICS (Total Runs: {total_runs})")
    print("==================================================")
    print(f"1. Split Court Frequency : {split_court_count}/{total_runs} ({(split_court_count/total_runs)*100:.1f}%)")
    print(f"2. Zero-Band Rate        : {zero_band_count}/{total_runs} ({(zero_band_count/total_runs)*100:.1f}%)")
    print(f"3. Tactical-Band Rate    : {tactical_band_count}/{total_runs} ({(tactical_band_count/total_runs)*100:.1f}%)")
    print(f"4. Hypothesis Challenge  : {hypothesis_thrash_count}/{total_runs} ({(hypothesis_thrash_count/total_runs)*100:.1f}%)")
    print(f"5. Envelope Supersede    : {supersede_count}/{total_runs} ({(supersede_count/total_runs)*100:.1f}%)")
    print(f"6. New-vs-Old Divergence : {divergence_count}/{total_runs} ({(divergence_count/total_runs)*100:.1f}%)\n")

    print("--- Divergence Breakdown ---")
    for k, v in delta_classes.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", type=str, default="/home/liwu/digital_twin/06_Governance/shadow/shadow_runs.jsonl")
    args = parser.parse_args()
    analyze_shadow_logs(args.log_file)
