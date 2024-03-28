#!/bin/bash

icefall_path=$ICEFALL_PATH
train_cmd="${TRAIN_CMD}"
epoch_dir=$TRAINING_DIR
dataset=$DATASET_NAME
model_size=$MODEL_SIZE
start_epoch=1

# 进入工作目录
cd /workspace || exit

# 检查 ICEFALL_PATH 是否设置
if [ -z "$icefall_path" ]; then
    echo "ICEFALL_PATH not set"
    exit 1
fi

# 链接 icefall 目录
if [ ! -L "icefall" ]; then
    current_time=$(date +%Y%m%d%H%M%S)
    mv -f icefall icefall_$current_time
    ln -svf "$icefall_path" icefall
else
    echo "icefall has been linked."
fi

cd /workspace/icefall/egs/"$dataset"/ASR || exit

num_epochs=$(echo "$train_cmd" | grep -o -- '--num-epochs [^ ]*' | cut -d ' ' -f2)
exp_dir=$(echo "$train_cmd" | grep -o -- '--exp-dir [^ ]*' | cut -d ' ' -f2)
wer_dir="./$epoch_dir/greedy_search"

recipe=${exp_dir%%/*}
if [[ ! -d "./$recipe" ]]; then
    printf "Error: /workspace/icefall/egs/%s/ASR/%s does not exist.\n" "$dataset" "$recipe"
    exit 1
fi


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

last_epoch=0
while true; do
  for file in $epoch_dir/epoch-*.pt; do
      if [[ -f "$file" ]]; then
          epoch=$(basename "$file" | cut -d'-' -f2 | cut -d'.' -f1)
          if ((epoch > last_epoch)); then
              last_epoch=$epoch
          fi
      fi
  done

  used_epoch=$(find_max_epoch $wer_dir)
  printf "Used epoch: %d, Last epoch: %d\n" "$used_epoch" "$last_epoch"

  if ((last_epoch <= used_epoch)); then
      echo "Last epoch is not greater than used epoch, waiting for 300 seconds..."
      sleep 300
      continue
  fi

  for ((epoch=last_epoch; epoch>used_epoch; epoch--)); do
      for ((decode_epoch=1; decode_epoch<=epoch-start_epoch; decode_epoch++)); do
          bash /workspace/Conductor/conductor/decode/within_dataset_decode/start_decode.sh \
              "$dataset" "$dataset" "$recipe" "$epoch" "$decode_epoch" "$model_size"
      done
  done

  if [ "$last_epoch" -eq "$num_epochs" ]; then
        break
  fi
done

