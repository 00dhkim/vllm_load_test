import yaml, itertools, subprocess, datetime, os, pathlib

# 1. Load the saturation test specific configuration
CFG = yaml.safe_load(open('config/saturation_matrix.yaml'))
base_env = {**{k:str(v) for k,v in CFG['common_env'].items()}}

factors = CFG['factors']
profiles = CFG['profiles']
repetitions = CFG['meta']['repetitions']
run_time = CFG['meta']['default_run_time']
output_root = CFG['meta']['output_root']

matrix = itertools.product(
    factors['gpu_counts'],
    factors['request_rates'],
    factors['prompt_len_profile'],
    factors['batch_size'],
    factors['max_batched_tokens'],
    factors['data_parallel'],
    factors['tensor_parallel'],
    factors['quant_mode']
)

def build_id(ts, g,rr,pl,bs,mbt,dp,tp,q,rep):
    # ID now includes RR for request rate, matching the parser in the notebook
    return f"{ts}__SAT_G{g}__RR{rr}__PL{pl}__B{bs}"

ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

for (g,rr,pl,bs,mbt,dp,tp,q) in matrix:
    # Constraint: gpu_count must equal tensor_parallel_size * data_parallel_size
    if g != (dp * tp):
        print(f"Skipping invalid combination: gpus={g}, dp={dp}, tp={tp}")
        continue

    prof = profiles[pl]
    for rep in range(repetitions):
        exp_id = build_id(ts,g,rr,pl,bs,mbt,dp,tp,q,rep)
        env = os.environ.copy()
        env.update(base_env)
        env.update({
            'PROMPTS_FILE': prof['prompts_file'],
            'MAX_TOKENS': str(prof['max_tokens']),
            'REQUEST_RATE': str(rr),
            'RUN_TIME': run_time,
            'BATCH_SIZE': str(bs),
            'MBT': str(mbt),
            'TP': str(tp),
            'DP': str(dp),
            'QUANT_MODE': q
        })
        
        # Use the dedicated output directory
        out_dir = pathlib.Path(f"{output_root}/{exp_id}")
        if out_dir.exists():
            print(f"Skipping existing experiment: {exp_id}")
            continue
        
        print(f"Running saturation experiment: {exp_id}")
        # 2. Call the saturation test specific shell script
        subprocess.run(['bash','scripts/run_single_saturation.sh', exp_id], env=env, check=True)
