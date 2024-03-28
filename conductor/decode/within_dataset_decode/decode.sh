#!/bin/bash

epoch_dir=$TRAINING_DIR
train_cmd=$TRAIN_CMD
dataset=$DATASET_NAME
model_size=$MODEL_SIZE
start_epoch=1

cd /workspace/icefall/egs/"$dataset"/ASR || exit
exp_dir=$(echo "$cmd" | grep -o -- '--exp-dir [^ ]*' | cut -d ' ' -f2)
recipe=${exp_dir%%/*}
if [[ ! -d "./$recipe" ]]; then
    printf "Error: /workspace/icefall/egs/%s/ASR/%s does not exist.\n" "$dataset" "$recipe"
    exit 1
fi

if [[ -d "./$exp_dir" ]]; then
    rm -f "./$exp_dir"
fi

ln -sfv "$epoch_dir" ./$exp_dir

last_epoch=0
for file in $exp_dir/epoch-*.pt; do
    if [[ -f "$file" ]]; then
        epoch=$(basename "$file" | cut -d'-' -f2 | cut -d'.' -f1)
        if ((epoch > last_epoch)); then
            last_epoch=$epoch
        fi
    fi
done

function find_max_epoch() {
    files=$(ls $1/wer-summary* 2>/dev/null)
    if [[ -z "$files" ]]; then
        max_epoch=0
    else
        max_epoch=0
        for file in $files; do
            epoch=$(echo $file | grep -o 'epoch-[0-9]*' | sed 's/epoch-//')
            if [[ -n "$epoch" ]] && ((epoch <= 900)); then
                if ((epoch > max_epoch)); then
                    max_epoch=$epoch
                fi
            fi
        done
    fi
    echo $max_epoch
}

wer_dir="./$exp_dir/greedy_search"
used_epoch=$(find_max_epoch $wer_dir)
printf "Used epoch: %d, Last epoch: %d\n" "$used_epoch" "$last_epoch"

for ((epoch=last_epoch; epoch>used_epoch; epoch--)); do
    for ((decode_epoch=1; decode_epoch<=epoch-start_epoch; decode_epoch++)); do
        bash /workspace/Conductor/conductor/decode/within_dataset_decode/start_decode.sh \
            "$dataset" "$dataset" "$recipe" "$epoch" "$decode_epoch" "$model_size"
    done
done