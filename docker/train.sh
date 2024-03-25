#!/bin/bash
icefall_path="${ICEFALL_PATH}"
cmd="${TRAIN_CMD}"
dataset="${DATASET}"
log_file="${LOG_FILE}"

cd /workspace

if [ ! -d "${icefall_path}" ]; then
  echo "ICEFALL_PATH not set"
  exit 1
fi

if [ ! -L "/workspace/icefall" ]; then
    rm -f /workspace/icefall
    ln -svf $icefall_path /workspace/icefall
else
    echo "The specified path is not a symbolic link."
fi


cd /workspace/icefall/egs/$dataset/ASR


if [ ! -d "./data" ]; then
    ln -sfv "/data/AI_VOICE_WORKSPACE/asr/prepared_data/$dataset/data" ./data
fi

exp_dir=$(echo "$cmd" | grep -o -- '--exp-dir [^ ]*' | cut -d ' ' -f2)
max_epoch=0
for file in $exp_dir/epoch-*.pt; do
    if [ -f "$file" ]; then
        epoch=$(basename "$file" | cut -d'-' -f2 | cut -d'.' -f1)
        if [ "$epoch" -gt "$max_epoch" ]; then
            max_epoch=$epoch
        fi
    fi
done

cmd=$(echo "$cmd" | sed "s/--start-epoch [0-9]*/--start-epoch $((max_epoch + 1))/")

if [ ! -f $log_file ]; then
    if echo "$log_file" | grep -q "torch.cuda.OutOfMemoryError: CUDA out of memory"; then
       max_duration=$(echo "$cmd" | grep -o -- '--max-duration [^ ]*' | cut -d ' ' -f2)
       if [ "$max_duration" -gt 100 ]; then
           cmd=$(echo "$cmd" | sed "s/--max-duration [0-9]*\/--max-duration $(($max_duration - 100))/")
       else
           cmd=$(echo "$cmd" | sed "s/--max-duration [0-9]*\/--max-duration 50/")
       fi
    elif echo "$log_file" | grep -q "grad_scale is too small, exiting"; then
       base_lr=$(echo "$cmd" | grep -o -- '--base-lr [^ ]*' | cut -d ' ' -f2)
       if [ $(echo "$base_lr > 0.005" | bc -l) -eq 1 ]; then
           cmd=$(echo "$cmd" | sed "s/--base-lr [0-9\.]*\/--base-lr $(echo "$base_lr - 0.005" | bc)/")
       else
           echo "Learning rate is too small, exiting"
           exit 1
       fi
    else
       echo "No matching policy found, exiting"
       exit 1
    fi
fi

echo "$cmd"
eval "$cmd"