import pandas as pd

# 原文件路径
csv_path = "kamailio.csv"

# 读取 CSV
df = pd.read_csv(csv_path)

# 过滤 cov_type 为 'b_abs' 的行
df_filtered = df[df['cov_type'] == 'b_abs']

# 覆盖写回原文件（不保留原索引）
df_filtered.to_csv(csv_path, index=False)
