import yaml
import os
import subprocess
from unittest.mock import patch, mock_open

MOCK_CONFIG = '''
meta:
  default_run_time: "1m"
  repetitions: 1
common_env:
  VLLM_HOST: "http://localhost:18802"
factors:
  gpu_counts: [1, 2]
  users: [10]
  prompt_len_profile: ["short"]
  batch_size: [16]
  max_batched_tokens: [2048]
  data_parallel: [1, 2]
  tensor_parallel: [1, 2]
  quant_mode: ["fp16"]
profiles:
  short:
    prompts_file: config/prompts_short.txt
    max_tokens: 64
'''

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@patch("builtins.open", new_callable=mock_open, read_data=MOCK_CONFIG)
@patch("subprocess.run")
def test_run_matrix_logic(mock_subprocess_run, mock_file_open):
    from scripts.run_matrix import build_id
    # We need to import the script after patching the open function
    import scripts.run_matrix

    # The script will call subprocess.run for each valid experiment
    # We can check how many times it was called
    # Valid combinations:
    # g=1, dp=1, tp=1
    # g=2, dp=1, tp=2
    # g=2, dp=2, tp=1
    assert mock_subprocess_run.call_count == 3
