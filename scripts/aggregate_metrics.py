import json, pandas as pd, pathlib, re

def parse_experiment_id(exp_name):
    """Extracts parameters from the experiment ID string."""
    meta = {}
    # Updated regex to capture RR (Request Rate) instead of U (Users)
    m = re.search(r'G(\d+).*RR(\d+).*PL(\w+).*B(\d+).*MBT(\d+).*TP(\d+).*DP(\d+).*Q(\w+)', exp_name)
    if not m:
        print(f"Warning: Could not parse experiment ID: {exp_name}")
        return None
    
    meta.update({
        'gpu_count': int(m.group(1)),
        'request_rate': int(m.group(2)),
        'prompt_profile': m.group(3),
        'batch_size': int(m.group(4)),
        'max_batched_tokens': int(m.group(5)),
        'tp': int(m.group(6)),
        'dp': int(m.group(7)),
        'quant': m.group(8)
    })
    return meta

def main():
    root = pathlib.Path('results/raw')
    rows = []
    
    if not root.exists():
        print(f"Results directory not found: {root}")
        return

    for exp_dir in root.iterdir():
        if not exp_dir.is_dir():
            continue

        meta = parse_experiment_id(exp_dir.name)
        if not meta:
            continue

        benchmark_dir = exp_dir / 'benchmark'
        result_files = list(benchmark_dir.glob('*.json'))
        
        if not result_files:
            print(f"Warning: No benchmark result JSON found in {benchmark_dir}")
            continue
        
        # Assuming there's only one result file per benchmark run
        result_file = result_files[0]
        
        with open(result_file, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {result_file}")
                continue
        
        # Extract key metrics from the benchmark result
        meta.update({
            'successful_requests': data.get('successful_requests'),
            'benchmark_duration_s': data.get('benchmark_duration_s'),
            'total_input_tokens': data.get('total_input_tokens'),
            'total_generated_tokens': data.get('total_generated_tokens'),
            'request_throughput_req_s': data.get('request_throughput_req/s'),
            'output_token_throughput_tok_s': data.get('output_token_throughput_tok/s'),
            'total_token_throughput_tok_s': data.get('total_token_throughput_tok/s'),
            'mean_ttft_ms': data.get('mean_ttft_ms'),
            'median_ttft_ms': data.get('median_ttft_ms'),
            'p99_ttft_ms': data.get('p99_ttft_ms'),
            'mean_tpot_ms': data.get('mean_tpot_ms'),
            'median_tpot_ms': data.get('median_tpot_ms'),
            'p99_tpot_ms': data.get('p99_tpot_ms'),
        })
        rows.append(meta)

    if not rows:
        print("No valid experiment results found to aggregate.")
        return

    out_dir = pathlib.Path('results/agg')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(rows)
    output_path = out_dir / 'summary_metrics.parquet'
    df.to_parquet(output_path, index=False)
    
    print(f"Successfully aggregated {len(rows)} experiments into {output_path}")

if __name__ == "__main__":
    main()
