"""由真实的 results.csv 生成报告素材。

直接运行：

    uv run --locked python render_results.py

读取当前工作目录的 results.csv（不在这一步重新投针），生成：

- results-table.tex  可直接 \\input 的 LaTeX 表格：n、触线数、估计值
- results-params.tex 可直接 \\input 的短文字：实际 seed、各组 n、针长、线间距
- results.png        展示不同 n 对应估计值的静态图，附真实 pi 参考线

图表与参数文件使用同一份 CSV，不编造或手工美化结果。
输出中文 LaTeX 时沿用模板的字体设置（由 report.tex 的 ctexart/fandol 提供）；
图片坐标轴使用英文，避免图像中文字体成为额外安装任务。
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 无显示环境也能生成图片。

import matplotlib.pyplot as plt
import matplotlib.ticker

CSV_NAME = "results.csv"
TABLE_NAME = "results-table.tex"
PARAMS_NAME = "results-params.tex"
PNG_NAME = "results.png"


def read_results(path=CSV_NAME):
    """读取 results.csv，返回按 n 升序排列的记录列表。"""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"找不到 {csv_path}，请先运行 experiment.py 生成真实结果。")
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = [
            {
                "seed": int(row["seed"]),
                "n": int(row["n"]),
                "crossings": int(row["crossings"]),
                "pi_estimate": float(row["pi_estimate"]),
                "needle_length": float(row["needle_length"]),
                "line_spacing": float(row["line_spacing"]),
            }
            for row in csv.DictReader(handle)
        ]
    if not rows:
        raise ValueError(f"{csv_path} 中没有数据行。")
    rows.sort(key=lambda r: r["n"])
    return rows


def _fmt(value, digits=6):
    """去掉多余的尾随零，便于在报告中阅读。"""
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return text if text else "0"


def write_params(rows, path=PARAMS_NAME):
    """生成显示实际 seed、各组 n、针长和线间距的短文字。"""
    seeds = sorted({row["seed"] for row in rows})
    lengths = sorted({row["needle_length"] for row in rows})
    spacings = sorted({row["line_spacing"] for row in rows})
    sizes = [row["n"] for row in rows]

    seed_text = ", ".join(str(s) for s in seeds)
    n_text = ", ".join(f"$n={n}$" for n in sizes)
    length_text = ", ".join(_fmt(v) for v in lengths)
    spacing_text = ", ".join(_fmt(v) for v in spacings)

    lines = [
        f"本次实验使用 seed ${seed_text}$；各组投针数为 {n_text}；"
        f"针长 $L={length_text}$，平行线间距 $d={spacing_text}$。",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_table(rows, path=TABLE_NAME):
    """生成 booktabs 风格的 LaTeX 表格：n、触线数 K、估计值。"""
    header = [
        r"\begin{tabular}{rrr}",
        r"\toprule",
        r"投针数 $n$ & 触线数 $K$ & 估计值 $\widehat{\pi}=2LN/(dK)$ \\",
        r"\midrule",
    ]
    body = [
        f"{row['n']} & {row['crossings']} & {_fmt(row['pi_estimate'])} \\\\"
        for row in rows
    ]
    footer = [
        r"\bottomrule",
        r"\end{tabular}",
    ]
    Path(path).write_text("\n".join(header + body + footer) + "\n", encoding="utf-8")


def write_figure(rows, path=PNG_NAME):
    """生成不同 n 对应估计值的静态图，附真实 pi 参考线。"""
    sizes = [row["n"] for row in rows]
    estimates = [row["pi_estimate"] for row in rows]

    fig, ax = plt.subplots(figsize=(7.0, 3.6), dpi=150)
    ax.axhline(math.pi, color="tab:red", linestyle="--", linewidth=1.2,
               label=r"true $\pi$")
    ax.plot(sizes, estimates, marker="o", color="tab:blue", linewidth=1.5,
            label="estimate")
    for n, value in zip(sizes, estimates):
        ax.annotate(f"{value:.4f}", (n, value), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8)

    ax.set_xscale("log")
    ax.set_xlabel("number of needles n")
    ax.set_ylabel(r"estimated $\pi$")
    ax.set_title("Buffon's needle: estimate of pi vs. n")
    ax.grid(True, which="both", linestyle=":", alpha=0.4)
    ax.set_xticks(sizes)
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_ylim(min(estimates + [math.pi]) - 0.2, max(estimates + [math.pi]) + 0.2)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main(argv=None):
    rows = read_results()
    write_params(rows)
    write_table(rows)
    write_figure(rows)
    print(f"已由 {CSV_NAME} 生成 {PARAMS_NAME}、{TABLE_NAME} 和 {PNG_NAME}（{len(rows)} 行）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
