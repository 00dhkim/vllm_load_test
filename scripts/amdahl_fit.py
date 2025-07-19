import pandas as pd, numpy as np
# 입력 parquet: columns [gpu_count, tokens_sec]
df = pd.read_parquet('results/agg/summary_metrics.parquet')
base = df[df.gpu_count==1]['tokens_sec'].mean()
rows = []
for g in sorted(df.gpu_count.unique()):
    if g==1: continue
    S = (df[df.gpu_count==g]['tokens_sec'].mean()/base)
    # s 추정
    s = ((1/S) - (1/g)) / (1 - (1/g))
    rows.append({'gpu_count': g, 'speedup': S, 'estimated_s': s})
pd.DataFrame(rows).to_csv('results/agg/amdahl_fit.csv', index=False)
