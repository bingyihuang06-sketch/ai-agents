"""蒲丰投针实验：估计圆周率并把真实结果写入 results.csv。

可被 import；import 时不启动实验、不写文件。
直接运行：

    uv run --locked python experiment.py

默认对 n = 1000, 10000, 100000（seed=42）各做一组独立实验，
每个实验组在投针循环外只初始化随机数生成器一次。
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from pathlib import Path

# CSV 表头，顺序与需求一致。
FIELDS = (
    "seed", "n", "crossings", "pi_estimate", "needle_length", "line_spacing"
)
DEFAULT_SIZES = (1000, 10000, 100000)
DEFAULT_SEED = 42
DEFAULT_LENGTH = 0.5
DEFAULT_SPACING = 1.0
CSV_NAME = "results.csv"


def _validate_geometry(length: float, spacing: float) -> None:
    """检查针长与线间距，非法时抛 ValueError，不静默改参数。"""
    if spacing <= 0:
        raise ValueError(f"spacing 必须为正，收到 {spacing!r}")
    if length <= 0:
        raise ValueError(f"length 必须为正，收到 {length!r}")
    if length > spacing:
        raise ValueError(f"要求 0 < length <= spacing，收到 length={length!r}, spacing={spacing!r}")


def crosses_line(distance, angle, length=DEFAULT_LENGTH, spacing=DEFAULT_SPACING):
    """判断一根针是否与平行线相交。

    相交判据：distance <= (length / 2) * sin(angle)；针尖恰好触线也算相交。
    输入范围：0 <= distance <= spacing/2，0 <= angle <= pi/2。
    非法几何参数抛 ValueError。
    """
    _validate_geometry(length, spacing)
    if not 0 <= distance <= spacing / 2:
        raise ValueError(f"distance 必须在 [0, {spacing / 2}] 内，收到 {distance!r}")
    if not 0 <= angle <= math.pi / 2:
        raise ValueError(f"angle 必须在 [0, pi/2] 内，收到 {angle!r}")
    # 比较运算直接产出原生 bool（测试用 `is True/False` 断言）。
    return distance <= (length / 2) * math.sin(angle)


def estimate_pi(n, crossings, length=DEFAULT_LENGTH, spacing=DEFAULT_SPACING):
    """由投针数与相交数估计圆周率：2 * length * n / (spacing * crossings)。"""
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError(f"n 必须是正整数，收到 {n!r}")
    if not isinstance(crossings, int) or isinstance(crossings, bool):
        raise ValueError(f"crossings 必须是整数，收到 {crossings!r}")
    if not 0 <= crossings <= n:
        raise ValueError(f"crossings 必须在 [0, n] 内，收到 crossings={crossings!r}, n={n!r}")
    if crossings == 0:
        raise ValueError("crossings=0 时无法用该公式估计圆周率")
    _validate_geometry(length, spacing)
    return 2 * length * n / (spacing * crossings)


def simulate(n, seed=DEFAULT_SEED, length=DEFAULT_LENGTH, spacing=DEFAULT_SPACING):
    """做 n 次独立投针，返回本次实验的真实结果。

    循环外只初始化一次随机数生成器；循环内持续取样，不在每次投针时重设 seed。
    distance ~ U[0, spacing/2]，angle ~ U[0, pi/2]，二者独立。
    """
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError(f"n 必须是正整数，收到 {n!r}")
    _validate_geometry(length, spacing)

    rng = random.Random(seed)  # 每组独立实验只初始化一次。
    crossings = 0
    for _ in range(n):
        distance = rng.uniform(0, spacing / 2)
        angle = rng.uniform(0, math.pi / 2)
        if distance <= (length / 2) * math.sin(angle):
            crossings += 1

    if crossings == 0:
        raise ValueError("本次实验 crossings=0，无法给出圆周率估计值")

    return {
        "seed": seed,
        "n": n,
        "crossings": crossings,
        "pi_estimate": estimate_pi(n, crossings, length=length, spacing=spacing),
        "needle_length": length,
        "line_spacing": spacing,
    }


def run_experiments(sizes, seed=DEFAULT_SEED, length=DEFAULT_LENGTH, spacing=DEFAULT_SPACING):
    """对每个 n 做一组独立实验，返回结果列表。"""
    results = []
    for n in sizes:
        result = simulate(n, seed=seed, length=length, spacing=spacing)
        results.append(result)
        print(
            f"n={n:>7} seed={seed} crossings={result['crossings']:>7} "
            f"pi_estimate={result['pi_estimate']:.6f}"
        )
    return results


def write_csv(results, path=CSV_NAME):
    """把结果写入当前工作目录下的 CSV，表头顺序与需求一致。"""
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="蒲丰投针估计圆周率")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="随机种子")
    parser.add_argument(
        "--n", type=int, action="append", dest="sizes",
        help="投针数，可重复指定；缺省保留 1000/10000/100000 三组",
    )
    parser.add_argument("--length", type=float, default=DEFAULT_LENGTH, help="针长")
    parser.add_argument("--spacing", type=float, default=DEFAULT_SPACING, help="平行线间距")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    sizes = args.sizes if args.sizes else list(DEFAULT_SIZES)
    results = run_experiments(
        sizes, seed=args.seed, length=args.length, spacing=args.spacing
    )
    write_csv(results)
    print(f"已写入 {CSV_NAME}（{len(results)} 行）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
