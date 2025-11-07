#!/usr/bin/env python3

import argparse
import pandas as pd
import matplotlib.pyplot as plt

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文
plt.rcParams['axes.unicode_minus'] = False    # 解决负号乱码

def process_csv(csv_file, put, runs, cut_off, step, fuzzers):
    df = pd.read_csv(csv_file)
    mean_list = []

    for fuzzer in fuzzers:
        fuzzer = fuzzer.lower()
        cov_type = 'b_abs'

        df1 = df[(df['subject'] == put) & 
                 (df['fuzzer'] == fuzzer) & 
                 (df['cov_type'] == cov_type)]
        if df1.empty:
            print(f"[警告] 无数据: {put}, {fuzzer}, {cov_type}")
            continue

        mean_list.append((put, fuzzer, cov_type, 0, 0.0))

        for time in range(1, cut_off + 1, step):
            cov_total = 0
            run_count = 0
            for run in range(1, runs + 1):
                df2 = df1[df1['run'] == run]
                try:
                    start = df2.iloc[0, 0]
                    df3 = df2[df2['time'] <= start + time * 60]
                    cov_total += df3.tail(1).iloc[0, 5]
                    run_count += 1
                except Exception:
                    print(f"Issue with run {run}. Skipping")
            mean_list.append((put, fuzzer, cov_type, time, cov_total / max(run_count, 1)))

    mean_df = pd.DataFrame(mean_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    return mean_df

def main(csv_files, puts, runs, cut_off, step, out_file, fuzzers):
    n = len(csv_files)
    cols = 2
    rows = (n + 1) // 2  # 每行2个子图

    fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 4*rows))
    axes = axes.flatten()

    for i, (csv_file, put) in enumerate(zip(csv_files, puts)):
        mean_df = process_csv(csv_file, put, runs, cut_off, step, fuzzers)

        ax = axes[i]
        # 标题加粗
        # ax.set_title(f"{put}", fontsize=14, fontweight='bold')
        ax.set_title(f"{put.capitalize()}", fontsize=16, fontweight='bold')
        ax.set_xlabel("时间（分钟）", fontsize=10)
        ax.set_ylabel("分支覆盖数", fontsize=10)
        ax.grid(True)

        # for key, grp in mean_df.groupby(['fuzzer', 'cov_type']):
        #     if key[1] == 'b_abs':
        #         # 保留时间为分钟
        #         ax.plot(grp['time'], grp['cov'], label=key[0])


        # Fuzzer 名称映射
        fuzzer_label_map = {
            'aflnet': 'AFLNet',
            'xpgfuzz': 'XPGFUZZ',
            'chatafl': 'ChatAFL'
        }

        for key, grp in mean_df.groupby(['fuzzer', 'cov_type']):
            if key[1] == 'b_abs':
                label = fuzzer_label_map.get(key[0].lower(), key[0])  # 默认保持原名
                ax.plot(grp['time'], grp['cov'], label=label)

                ax.legend(fontsize=10)

        # 添加下方 (a), (b), ... 标签
        letter = chr(ord('a') + i)
        ax.text(0.5, -0.2, f"({letter})", transform=ax.transAxes,
                fontsize=14, ha='center', va='center')

    # 去掉多余子图
    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.savefig(out_file, dpi=400, bbox_inches='tight')
    print(f"✅ 图已保存到：{out_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--csv_files', nargs='+', type=str, required=True, help="List of CSV files")
    parser.add_argument('-p', '--puts', nargs='+', type=str, required=True, help="List of subject programs")
    parser.add_argument('-r', '--runs', type=int, required=True, help="Number of runs")
    parser.add_argument('-c', '--cut_off', type=int, required=True, help="Cut-off time in minutes")
    parser.add_argument('-s', '--step', type=int, required=True, help="Time step in minutes")
    parser.add_argument('-o', '--out_file', type=str, required=True, help="Output image file")
    parser.add_argument('-f', '--fuzzers', nargs='+', required=True, help="List of fuzzers")
    args = parser.parse_args()

    main(args.csv_files, args.puts, args.runs, args.cut_off, args.step, args.out_file, args.fuzzers)
