# vLLM Scaling Experiment Suite

This repository contains a suite of scripts to systematically test the scaling performance of a vLLM server.

## Prerequisites

- Python 3.8+
- CUDA
- `uv` (or `pip`)
- vLLM installed

## Setup

1. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Configure environment:**
   Copy `env.example` to `.env` and modify the variables as needed.

## Running Experiments

To run the full experiment matrix, execute:

```bash
python scripts/run_matrix.py
```

To run a single experiment:

```bash
# Set environment variables for the specific run
export USERS=100
export ...

bash scripts/run_single.sh <experiment_id>
```

## Analysis

After running the experiments, you can analyze the results using the provided notebook:

```bash
jupyter notebook analysis/notebook.ipynb
```