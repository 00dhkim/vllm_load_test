import yaml, itertools, subprocess, datetime, os, pathlib

CFG = yaml.safe_load(open('config/experiment_matrix.yaml'))
base_env = {**{k:str(v) for k,v in CFG['common_env'].items()}}

factors = CFG['factors']
profiles = CFG['profiles']
repetitions = CFG['meta']['repetitions']
run_time = CFG['meta']['default_run_time']

matrix = itertools.product(
    factors['gpu_counts'],
    factors['users'],
    factors['prompt_len_profile'],
    factors['batch_size'],
    factors['max_batched_tokens'],
    factors['data_parallel'],
    factors['tensor_parallel'],
    factors['quant_mode']
)

def build_id(ts, g,u,pl,bs,mbt,dp,tp,q,rep):
    return f"{ts}__G{g}__U{u}__PL{pl}__B{bs}__MBT{mbt}__TP{tp}__DP{dp}__Q{q}__R{rep}"

ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

for (g,u,pl,bs,mbt,dp,tp,q) in matrix:
    if g != (dp * tp):
        print(f"Skipping invalid combination: gpus={g}, dp={dp}, tp={tp}")
        continue

    prof = profiles[pl]
    for rep in range(repetitions):
        exp_id = build_id(ts,g,u,pl,bs,mbt,dp,tp,q,rep)
        env = os.environ.copy()
        env.update(base_env)
        env.update({
            'PROMPTS_FILE': prof['prompts_file'],
            'MAX_TOKENS': str(prof['max_tokens']),
            'USERS': str(u),
            'SPAWN': str(int(u/5)),  # 예시 spawn rate
            'RUN_TIME': run_time,
            'BATCH_SIZE': str(bs),
            'MBT': str(mbt),
            'TP': str(tp),
            'DP': str(dp),
            'QUANT_MODE': q
        })
        out_dir = pathlib.Path(f"results/raw/{exp_id}")
        if out_dir.exists():
            print("skip existing", exp_id)
            continue
        print("Running", exp_id)
        subprocess.run(['bash','scripts/run_single.sh', exp_id], env=env, check=True)
