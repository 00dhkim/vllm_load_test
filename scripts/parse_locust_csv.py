import pandas as pd, json, argparse, pathlib

parser = argparse.ArgumentParser()
parser.add_argument('--exp-dir', required=True)
args = parser.parse_args()

exp = pathlib.Path(args.exp_dir)
locust_stats = exp / 'locust' / 'locust_stats_history.csv'
if not locust_stats.exists():
    raise SystemExit('stats history not found')

df = pd.read_csv(locust_stats)
# throughput req/s, latency ms -> summarize last 30s window
last_window = df.tail(30)
summary = {
    'requests_per_sec_mean': last_window['current_rps'].mean(),
    'fail_ratio': (last_window['fail_ratio'].mean()),
    'avg_response_time_ms': last_window['response_time'].mean(),
    'p95_ms': last_window['response_time_percentile_0.95'].mean(),
}
print(json.dumps(summary, indent=2))
