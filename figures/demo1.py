'''
2025/11/3, 我想要让AI生成一张论文的图形的效果.
'''

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# ======= 全局字体设置 =======

plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题
plt.rcParams.update({
    'font.size': 12,
    'legend.fontsize': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'lines.linewidth': 2,
})

# ======= 模拟实验数据 =======
x = np.linspace(0, 24, 25)
def gen_curve(base, scale): 
    return base * (1 - np.exp(-x/scale))

datasets = {
    "Forked-daapd": [gen_curve(200, 8), gen_curve(150, 6), gen_curve(180, 7), gen_curve(190, 9)],
    "Dcmtk": [gen_curve(600, 3), gen_curve(580, 3.5), gen_curve(590, 3.2), gen_curve(595, 3.3)],
    "Dnsmasq": [gen_curve(700, 2.8), gen_curve(600, 3.2), gen_curve(750, 2.5), gen_curve(760, 2.6)],
    "Tinydtls": [gen_curve(400, 5), gen_curve(350, 4.5), gen_curve(370, 5.2), gen_curve(390, 5.5)],
    "Bftpd": [gen_curve(800, 3.2), gen_curve(780, 3.5), gen_curve(790, 3.1), gen_curve(795, 3.3)],
    "Lightftp": [gen_curve(500, 4.2), gen_curve(480, 4.5), gen_curve(490, 4.3), gen_curve(495, 4.4)],
}

methods = ["AFLNET", "AFLNWE", "SNPSFuzzer-tmp", "SNPSFuzzer"]
colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']
markers = ['o', '^', 'x', 's']

# ======= 画 2×3 子图 =======
fig, axes = plt.subplots(2, 3, figsize=(12, 6))
axes = axes.flatten()

for i, (title, curves) in enumerate(datasets.items()):
    ax = axes[i]
    for j, y in enumerate(curves):
        ax.plot(x, y, label=methods[j], color=colors[j], marker=markers[j], markevery=4, markersize=4)
    
    ax.set_xlabel("时间（小时）")
    ax.set_ylabel("路径覆盖数")
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(frameon=True)
    
    # 添加子图编号 (a), (b), ...
    ax.text(0.02, 0.9, f"({chr(97+i)})", transform=ax.transAxes, fontsize=12, fontweight='bold')

# 调整布局
plt.tight_layout()
plt.show()
