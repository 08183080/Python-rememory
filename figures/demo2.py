import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# ======== 全局绘图风格 ========
plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'legend.fontsize': 10,
    'lines.linewidth': 2.2
})

# ======== 读取所有 CSV 文件 ========
data_dir = 'data_csv_files'  # 你自己的数据目录
csv_files = sorted(glob.glob(os.path.join(data_dir, '*.csv')))

# ======== 设置颜色、线型等 ========
tools = ['AFLNET', 'ChatAFL', 'XPGFUZZ']
colors = ['#4C72B0', '#55A868', '#C44E52']  # 蓝、绿、红
markers = ['o', 's', '^']

# ======== 创建 2x3 子图 ========
fig, axes = plt.subplots(2, 3, figsize=(12, 6))
axes = axes.flatten()

for i, csv_file in enumerate(csv_files):
    df = pd.read_csv(csv_file)
    protocol_name = os.path.basename(csv_file).split('.')[0].capitalize()

    ax = axes[i]
    for j, tool in enumerate(tools):
        if tool not in df.columns:
            print(f"⚠️ 文件 {csv_file} 中缺少列 {tool}，已跳过。")
            continue
        ax.plot(df['time'], df[tool],
                label=tool,
                color=colors[j],
                marker=markers[j],
                markevery=4,
                markersize=4)
    
    ax.set_xlabel("时间（小时）")
    ax.set_ylabel("路径覆盖数")
    ax.set_title(protocol_name, fontsize=13, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(frameon=True)
    ax.text(0.02, 0.9, f"({chr(97 + i)})", transform=ax.transAxes, fontsize=12, fontweight='bold')

# ======== 调整整体布局 ========
plt.tight_layout()
plt.show()
