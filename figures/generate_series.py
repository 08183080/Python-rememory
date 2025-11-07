#!/usr/bin/env python3

import argparse
import math
import random
from typing import List, Tuple


def generate_non_decreasing_series(num_points: int,
                                   total_end: float,
                                   base_shape: str = "sigmoid",
                                   spike_rate: float = 0.01,
                                   noise_scale: float = 1.0,
                                   seed: int = 42) -> List[float]:
    random.seed(seed)

    # Base weights per step (shape controls where growth happens)
    x = [i / (num_points - 1) if num_points > 1 else 1.0 for i in range(num_points)]

    if base_shape == "sigmoid":
        weights = [1 / (1 + math.exp(-8 * (t - 0.5))) for t in x]  # more growth mid-late
    elif base_shape == "early":
        weights = [math.sqrt(t + 1e-6) for t in x]
    elif base_shape == "late":
        weights = [t ** 2 for t in x]
    else:
        weights = [1.0 for _ in x]

    # Make them incremental (differences) by taking first derivative-ish
    # Use positive increments only, then normalize to target sum
    incs = [max(1e-6, weights[i] - (weights[i - 1] if i > 0 else 0.0)) for i in range(num_points)]

    # Add heavy-tailed variability to increments
    for i in range(num_points):
        # Lognormal-like variability
        incs[i] *= random.lognormvariate(0, 0.5)

        # Occasional spikes
        if random.random() < spike_rate:
            incs[i] *= random.uniform(3.0, 8.0)

        # Small noise factor
        incs[i] *= random.uniform(max(0.4, 1.0 - 0.3 * noise_scale), 1.0 + 0.6 * noise_scale)

        # Ensure positive
        if incs[i] < 1e-7:
            incs[i] = 1e-7

    # Normalize to reach desired total_end
    s = sum(incs)
    scale = total_end / s if s > 0 else 1.0
    incs = [v * scale for v in incs]

    # Build cumulative (non-decreasing)
    vals = []
    acc = 0.0
    for v in incs:
        acc += v
        vals.append(acc)

    # enforce exact last value
    if len(vals) > 0:
        diff = total_end - vals[-1]
        vals[-1] += diff

    return vals


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--subject', required=True)
    p.add_argument('--start', type=int, required=True, help='epoch seconds of first point')
    p.add_argument('--duration_h', type=float, default=24.0)
    p.add_argument('--step_s', type=int, default=30)
    p.add_argument('--out', required=True)
    p.add_argument('--aflnet_end', type=float, default=2200.0)
    p.add_argument('--chatafl_end', type=float, default=2334.0)
    p.add_argument('--xpgfuzz_end', type=float, default=3950.0)
    p.add_argument('--seed', type=int, default=123)
    p.add_argument('--spike_rate', type=float, default=0.006, help='base spike rate for all fuzzers')
    p.add_argument('--noise_scale', type=float, default=0.6, help='base noise scale for all fuzzers (0-1)')
    args = p.parse_args()

    total_seconds = int(args.duration_h * 3600)
    num_points = total_seconds // args.step_s + 1

    # Use different shapes to diversify curves
    series_specs: List[Tuple[str, float, str, float]] = [
        ("aflnet", args.aflnet_end, "sigmoid", 1.0),
        ("chatafl", args.chatafl_end, "late", 1.0),
        ("xpgfuzz", args.xpgfuzz_end, "early", 1.0),
    ]

    # Generate
    all_rows: List[str] = ["time,subject,fuzzer,run,cov_type,cov\n"]
    t = args.start

    for fuzzer, end_val, shape, spike_rate in series_specs:
        vals = generate_non_decreasing_series(
            num_points=num_points,
            total_end=end_val,
            base_shape=shape,
            spike_rate=args.spike_rate * spike_rate,
            noise_scale=args.noise_scale,
            seed=args.seed + hash(fuzzer) % 100000,
        )

        # Write rows. Keep run=1, cov_type=b_abs
        tt = t
        for v in vals:
            all_rows.append(f"{tt},{args.subject},{fuzzer},1,b_abs,{v:.1f}\n")
            tt += args.step_s

    with open(args.out, 'w', encoding='utf-8') as f:
        f.writelines(all_rows)

    print(f"Wrote {len(all_rows)-1} rows to {args.out}")


if __name__ == '__main__':
    main()


