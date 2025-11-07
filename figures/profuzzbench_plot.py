#!/usr/bin/env python3

import argparse
import pandas as pd
import matplotlib.pyplot as plt

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文
plt.rcParams['axes.unicode_minus'] = False    # 解决负号乱码

def main(csv_file, put, runs, cut_off, step, out_file, fuzzers):
    # 读取数据
    df = pd.read_csv(csv_file)

    mean_list = []

    for subject in [put]:
        for fuzzer in fuzzers:
            fuzzer = fuzzer.lower()
            cov_type = 'b_abs'

            df1 = df[(df['subject'] == subject) &
                     (df['fuzzer'] == fuzzer) &
                     (df['cov_type'] == cov_type)]

            if df1.empty:
                print(f"[警告] 无数据: {subject}, {fuzzer}, {cov_type}")
                continue

            mean_list.append((subject, fuzzer, cov_type, 0, 0.0))

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
                
                mean_list.append((subject, fuzzer, cov_type, time, cov_total / max(run_count, 1)))

    # 转换为 DataFrame
    mean_df = pd.DataFrame(mean_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])

    # 绘制单张图
    plt.figure(figsize=(10, 6))
    plt.title(f"{put} 分支覆盖率", fontsize=18)

    fontsize_xy = 14
    legend_fontsize = 14
    tick_fontsize = 12

    for key, grp in mean_df.groupby(['fuzzer', 'cov_type']):
        if key[1] == 'b_abs':
            plt.plot(grp['time'], grp['cov'], label=key[0])

    plt.xlabel('时间（分）', fontsize=fontsize_xy)
    plt.ylabel('分支数量', fontsize=fontsize_xy)
    plt.tick_params(axis='both', labelsize=tick_fontsize)
    plt.legend(loc='lower right', fontsize=legend_fontsize)
    plt.grid(True)

    # 保存图片
    plt.savefig(out_file, dpi=400, bbox_inches='tight')
    print(f"✅ 图已保存到：{out_file}")

# 参数解析
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--csv_file', type=str, required=True, help="Full path to results.csv")
    parser.add_argument('-p', '--put', type=str, required=True, help="Name of the subject program")
    parser.add_argument('-r', '--runs', type=int, required=True, help="Number of runs in the experiment")
    parser.add_argument('-c', '--cut_off', type=int, required=True, help="Cut-off time in minutes")
    parser.add_argument('-s', '--step', type=int, required=True, help="Time step in minutes")
    parser.add_argument('-o', '--out_file', type=str, required=True, help="Output file")
    parser.add_argument('-f', '--fuzzers', nargs='+', required=True, help="List of fuzzers")
    args = parser.parse_args()

    main(args.csv_file, args.put, args.runs, args.cut_off, args.step, args.out_file, args.fuzzers)
