import os
import pandas as pd
import subprocess
import json

def test_aggregation():
    # Create dummy raw results directory
    exp_name = "20250719-120000__G1__U10__PLshort__B16__MBT2048__TP1__DP1__Qfp16__R0"
    raw_dir = os.path.join("results", "raw", exp_name)
    locust_dir = os.path.join(raw_dir, "locust")
    vllm_dir = os.path.join(raw_dir, "vllm")
    os.makedirs(locust_dir, exist_ok=True)
    os.makedirs(vllm_dir, exist_ok=True)

    # Create dummy locust stats file
    locust_data = {
        'Timestamp': [1, 2, 3],
        'User Count': [10, 10, 10],
        'Type': ['GET', 'GET', 'GET'],
        'Name': ['/', '/', '/'],
        'Requests/s': [1.0, 1.0, 1.0],
        'Failures/s': [0.0, 0.0, 0.0],
        '50%': [100, 100, 100],
        '95%': [200, 200, 200],
        'Average Response Time': [150, 150, 150],
        'Min Response Time': [100, 100, 100],
        'Max Response Time': [200, 200, 200],
        'Average Content Size': [100, 100, 100],
        'current_rps': [1.0, 1.0, 1.0],
        'fail_ratio': [0.0, 0.0, 0.0],
        'response_time': [150, 150, 150],
        'response_time_percentile_0.95': [200, 200, 200]
    }
    pd.DataFrame(locust_data).to_csv(os.path.join(locust_dir, "locust_stats_history.csv"), index=False)

    # Create dummy vllm metrics file
    with open(os.path.join(vllm_dir, "vllm_metrics.jsonl"), "w") as f:
        f.write(json.dumps({"phase": "prefill", "tokens": 10, "time": 0.1}) + "\n")
        f.write(json.dumps({"phase": "decode", "tokens": 20, "time": 0.2}) + "\n")

    # Run aggregation script
    subprocess.run(["python", "scripts/aggregate_metrics.py"], check=True)

    # Check aggregated results
    df = pd.read_parquet("results/agg/summary_metrics.parquet")
    assert len(df) == 1
    assert df.iloc[0]["gpu_count"] == 1
    assert df.iloc[0]["users"] == 10
    assert df.iloc[0]["req_s"] == 1.0
    assert df.iloc[0]["tokens_sec"] > 0
