# vLLM Scaling Experiment Suite

This repository contains a suite of scripts to systematically test the scaling performance of a vLLM (vLLM) server, based on the hypotheses and experimental design proposed [here](https://docs.google.com/document/d/1zY...).

The primary goal is to understand why throughput doesn't scale linearly with the number of GPUs and to identify the key bottlenecks.

## Project Structure

```
vllm_scaling_exp/
  README.md
  requirements.txt
  env.example              # Environment variable template
  config/
    experiment_matrix.yaml # Defines all experiment combinations
    prompts_*.txt          # Prompts of varying lengths for tests
  locust/
    locustfile.py          # Locust test script, parameterized by env vars
  vllm_instrument/
    patch_vllm_metrics.py  # Monkey-patches vLLM to capture prefill/decode stats
  scripts/
    run_matrix.py          # Main script to run all experiments from the matrix
    run_single.sh          # Helper script to run one experiment configuration
    aggregate_metrics.py   # Script to collect and merge results from all runs
    amdahl_fit.py          # Script to estimate the sequential portion of the workload
  analysis/
    notebook.ipynb         # Jupyter notebook for visualizing results
  results/
    raw/<exp_id>/          # Raw data for each experiment run
    agg/                   # Aggregated results (e.g., summary.parquet)
    figs/                  # Saved plots from the analysis notebook
```

## Setup

1.  **Install Dependencies:**
    It's recommended to use `uv` for faster dependency management.
    ```bash
    uv pip install -r requirements.txt
    ```

2.  **Configure Environment:**
    Copy the example environment file and customize it for your setup. This is especially important for setting `VLLM_HOST` if your vLLM server runs on a different machine.
    ```bash
    cp env.example .env
    # Edit .env with your settings
    ```
    The scripts will automatically pick up these variables.

## How to Run Experiments

The entire experimental campaign is defined in `config/experiment_matrix.yaml`. The `run_matrix.py` script iterates through every valid combination of factors defined in this file.

### Running the Full Experiment Matrix

To launch the complete test suite, simply run:
```bash
python scripts/run_matrix.py
```
This will:
1.  Read the `experiment_matrix.yaml`.
2.  For each valid combination of parameters (GPUs, users, prompt length, etc.):
    a. Construct a unique `experiment_id`.
    b. Set the corresponding environment variables.
    c. Execute `scripts/run_single.sh` for that experiment.

### Running a Single Experiment

You can also run a single experiment manually. This is useful for debugging or re-running a specific test case. The `run_single.sh` script is designed for this. It handles:
1.  Starting the vLLM server with the correct parallelization, batching, and instrumentation parameters.
2.  Waiting for the server to become healthy.
3.  Starting `nvidia-smi dmon` to monitor GPU utilization.
4.  Running the Locust load test with the specified user count and runtime.
5.  Cleaning up all background processes once the test is complete.

**Example:**
```bash
# Manually export all required environment variables
export VLLM_MODEL="NousResearch/Meta-Llama-3-8B-Instruct"
export USERS=100
export SPAWN=20
export RUN_TIME=3m
export PROMPTS_FILE=config/prompts_medium.txt
export MAX_TOKENS=128
export TP=1
export DP=1
export BATCH_SIZE=32
export MBT=4096
export VLLM_HOST="http://localhost:8000" # Adjust port if needed

# Run the script with a descriptive experiment ID
bash scripts/run_single.sh 2025-07-19_manual_G1_U100_medium
```

## Analysis

After the experiments have produced raw data in the `results/raw/` directory, you can process and analyze it.

1.  **Aggregate Metrics:**
    Run the aggregation script to parse all raw results and combine them into a single file.
    ```bash
    python scripts/aggregate_metrics.py
    ```
    This creates `results/agg/summary_metrics.parquet`, which contains key performance indicators (latency, throughput, tokens/sec, etc.) for each run.

2.  **Fit Amdahl's Law:**
    To quantify the sequential bottleneck, run the Amdahl fitting script.
    ```bash
    python scripts/amdahl_fit.py
    ```
    This uses the aggregated data to estimate the sequential portion (`s`) of the workload and saves the output to `results/agg/amdahl_fit.csv`.

3.  **Visualize Results:**
    The `analysis/notebook.ipynb` contains boilerplate code to generate plots from the aggregated data, such as:
    -   Throughput vs. GPU count
    -   Latency CDFs
    -   Amdahl's Law curve fitting

    Launch Jupyter and run the cells in the notebook:
    ```bash
    jupyter notebook analysis/notebook.ipynb
    ```
