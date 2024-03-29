#!/bin/bash

icefall_path=$ICEFALL_PATH
dingding_token="${DINGDING_TOKEN}"
host_ip="${HOST_IP}"
train_cmd="${TRAIN_CMD}"
epoch_dir=$TRAINING_DIR
dataset=$DATASET_NAME
model_size=$MODEL_SIZE
decode_start_epoch=$DECODE_START_EPOCH


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
wer_dir="$epoch_dir/greedy_search"

recipe=${exp_dir%%/*}
if [[ ! -d "./$recipe" ]]; then
    printf "Error: /workspace/icefall/egs/%s/ASR/%s does not exist.\n" "$dataset" "$recipe"
    exit 1
fi

last_epoch=0
while true; do
  epoch_files=$(ls ${epoch_dir}/epoch-*.pt 2>/dev/null)
  for file in $epoch_files; do
      if [[ -f "$file" ]]; then
          epoch=$(basename "$file" | cut -d'-' -f2 | cut -d'.' -f1)
          if ((epoch > last_epoch)); then
              last_epoch=$epoch
          fi
      fi
  done
    # 搜索文件
  files=$(ls $wer_dir/wer-summary* 2>/dev/null)

  # 用于保存处理过的epoch和avg值
  declare -A processed_combinations

  for file in $files; do
    # 提取测试集名称、epoch值、avg值
#    test_sub_set=$(echo "$file" | sed 's/wer-summary-(.)-greedy_search./\1/')
    epoch=$(echo "$file" | grep -oP 'epoch-\K[0-9]+')
    avg=$(echo "$file" | grep -oP 'avg-\K[0-9]+')
    # 保存已处理的组合
    processed_combinations[$epoch,$avg]=1
  done

  #执行for循环，根据以上提取的值
  for ((epoch=last_epoch; epoch>0; epoch--)); do
    for ((avg=1; avg<=epoch-decode_start_epoch; avg++)); do
    # 检查组合是否已处理
      if [[ -n ${processed_combinations[$epoch,$avg]} ]]; then
        echo "File for epoch $epoch and avg $avg already exists, skipping..."
        continue
      fi
      echo "decode epoch: $epoch, decode avg: $avg"
      bash /workspace/Conductor/conductor/decode/within_dataset_decode/start_decode.sh \
      "$dataset" "$dataset" "$epoch_dir" "$recipe" "$epoch" "$avg" "$model_size"
    done
  done

  if [ "$last_epoch" -eq "$num_epochs" ]; then
        break
  fi
done

cd /workspace/Conductor || exit
python3 /workspace/Conductor/conductor/decode/within_dataset_decode/health_check.py $dingding_token $host_ip $dataset "$epoch_dir"