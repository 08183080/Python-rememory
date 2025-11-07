import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(42)

tools = ["AFLNET", "AFLNWE", "SNPSFuzzer-tmp", "SNPSFuzzer"]
protocols = ["Forked-daapd","Dcmtk","Dnsmasq","Tinydtls","Bftpd","Lightftp"]
hours = np.arange(0, 25)
n_runs = 8

# 针对每个协议设置不同规模（L 越大协议越复杂）
base_params = {
    "Forked-daapd": {"L": [200, 100, 180, 190]},
    "Dcmtk": {"L": [550, 450, 560, 580]},
    "Dnsmasq": {"L": [600, 500, 700, 750]},
    "Tinydtls": {"L": [400, 250, 380, 420]},
    "Bftpd": {"L": [800, 650, 820, 850]},
    "Lightftp": {"L": [450, 250, 460, 480]},
}

def generate_curve(L, noise_scale):
    k = 0.25 + np.random.uniform(-0.05, 0.05)
    a, b = 30, 0.6
    values = []
    for t in hours:
        val = L * (1 - np.exp(-k * t)) + a * np.log1p(b * t)
        val += np.random.normal(0, noise_scale)
        values.append(max(0, val))
    return np.clip(np.cumsum(np.diff([0]+values)), 0, L)

# 生成数据
data = []
for proto in protocols:
    Ls = base_params[proto]["L"]
    for i, tool in enumerate(tools):
        for run in range(n_runs):
            curve = generate_curve(Ls[i], noise_scale=5)
            for t, v in zip(hours, curve):
                data.append((proto, tool, run, t, v))
df = pd.DataFrame(data, columns=["protocol","tool","run","time","coverage"])

# 绘图
fig, axes = plt.subplots(2, 3, figsize=(15, 7.5))
axes = axes.flatten()
colors = {"AFLNET":"tab:blue","AFLNWE":"tab:orange","SNPSFuzzer-tmp":"tab:green","SNPSFuzzer":"tab:red"}

for ax, proto in zip(axes, protocols):
    for tool in tools:
        sub = df[(df.protocol==proto) & (df.tool==tool)]
        mean = sub.groupby("time")["coverage"].mean()
        std = sub.groupby("time")["coverage"].std() / 2  # 缩小阴影范围
        ax.plot(hours, mean, label=tool, color=colors[tool])
        ax.fill_between(hours, mean-std, mean+std, alpha=0.15, color=colors[tool])
    ax.set_title(proto, fontsize=12, fontweight='bold')
    ax.set_xlabel("时间（小时）")
    ax.set_ylabel("路径覆盖数")
    ax.grid(True, linestyle='--', linewidth=0.5)
    ax.legend(fontsize=8, loc="lower right")

plt.tight_layout()
plt.savefig("fixed_synthetic_plot.png", dpi=300)
plt.show()
