import json, pandas as pd, pathlib, re
root = pathlib.Path('results/raw')
rows=[]
for exp in root.iterdir():
    if not exp.is_dir(): continue
    meta = {}
    m = re.search(r'G(\d+).*U(\d+).*PL(\w+).*B(\d+).*MBT(\d+).*TP(\d+).*DP(\d+).*Q(\w+)', exp.name)
    if not m: continue
    meta.update({'gpu_count': int(m.group(1)), 'users': int(m.group(2)), 'prompt_profile': m.group(3),
                 'batch_size': int(m.group(4)), 'max_batched_tokens': int(m.group(5)),
                 'tp': int(m.group(6)), 'dp': int(m.group(7)), 'quant': m.group(8)})

    locust_hist = exp/'locust'/'locust_stats_history.csv'
    if not locust_hist.exists(): continue
    ldf = pd.read_csv(locust_hist).tail(30)
    meta.update({
        'req_s': ldf['current_rps'].mean(),
        'lat_avg_ms': ldf['response_time'].mean(),
        'lat_p95_ms': ldf['response_time_percentile_0.95'].mean()
    })

    # vLLM metrics (prefill/decode jsonl)
    vfile = exp/'vllm'/'vllm_metrics.jsonl'
    if vfile.exists():
        prefill_toks = 0; prefill_time=0; decode_toks=0; decode_time=0
        for line in vfile.open():
            try: ev=json.loads(line)
            except: continue
            if ev.get('phase')=='prefill':
                prefill_toks += ev.get('tokens',0); prefill_time += ev.get('time',0)
            elif ev.get('phase')=='decode':
                decode_toks += ev.get('tokens',0); decode_time += ev.get('time',0)
        if prefill_time>0:
            meta['prefill_tokens_sec'] = prefill_toks/prefill_time
        if decode_time>0:
            meta['decode_tokens_sec'] = decode_toks/decode_time
        total_time = prefill_time + decode_time
        if total_time>0:
            meta['tokens_sec'] = (prefill_toks+decode_toks)/total_time
            meta['decode_fraction'] = decode_time/total_time
    rows.append(meta)

out = pathlib.Path('results/agg')
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_parquet(out/'summary_metrics.parquet', index=False)
