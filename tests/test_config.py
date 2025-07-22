import yaml
import os

def test_config_structure():
    with open('config/experiment_matrix.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    assert 'meta' in config
    assert 'common_env' in config
    assert 'factors' in config
    assert 'profiles' in config

def test_prompt_files_exist():
    with open('config/experiment_matrix.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    for profile in config['profiles'].values():
        assert os.path.exists(profile['prompts_file']), f"Prompt file not found: {profile['prompts_file']}"
