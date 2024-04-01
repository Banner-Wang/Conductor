#!/bin/bash

required_vars=(
    "ICEFALL_PATH"
    "DINGDING_TOKEN"
    "HOST_IP"
    "TRAINING_DIR"
    "DATASET_NAME"
    "DECODE_CMD"
    "DECODE_START_EPOCH"
    "DECODE_END_EPOCH"
    "COMMONVOICE_DATA_DIR"
    "GIGASPEECH_DATA_DIR"
    "LIBRIHEAVY_DATA_DIR"
    "LIBRISPEECH_DATA_DIR"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var not set"
        exit 1
    fi
done

icefall_path=${ICEFALL_PATH}
dingding_token="${DINGDING_TOKEN}"
host_ip="${HOST_IP}"
epoch_dir=${TRAINING_DIR}
dataset=${DATASET_NAME}
decode_cmd="${DECODE_CMD}"
decode_start_epoch=${DECODE_START_EPOCH}
decode_end_epoch="${DECODE_END_EPOCH}"


case $dataset in
  commonvoice)
    bpe_model="$COMMONVOICE_DATA_DIR/en/lang_bpe_500/bpe.model"
    lang_dir="$COMMONVOICE_DATA_DIR/en/lang_bpe_500"
    ;;
  gigaspeech)
    bpe_model="$GIGASPEECH_DATA_DIR/lang_bpe_500/bpe.model"
    lang_dir="$GIGASPEECH_DATA_DIR/lang_bpe_500"
    ;;
  libriheavy)
    bpe_model="$LIBRIHEAVY_DATA_DIR/lang_bpe_500/bpe.model"
    lang_dir="$LIBRIHEAVY_DATA_DIR/lang_bpe_500"
    ;;
  librispeech)
    bpe_model="$LIBRISPEECH_DATA_DIR/lang_bpe_500/bpe.model"
    lang_dir="$LIBRISPEECH_DATA_DIR/lang_bpe_500"
    ;;
  *)
    echo "Unknown dataset: $dataset"
    exit 1
    ;;
esac


# 进入工作目录
cd /workspace || exit

# 链接 icefall 目录
if [ ! -L "icefall" ]; then
    current_time=$(date +%Y%m%d%H%M%S)
    mv -f icefall icefall_$current_time
    ln -svf "$icefall_path" icefall
else
    echo "icefall has been linked."
fi

cd /workspace/icefall/egs/"$dataset"/ASR || exit

decode_method=$(echo "$decode_cmd" | grep -o -- '--decoding-method [^ ]*' | cut -d ' ' -f2)
wer_dir="$epoch_dir/$decode_method"

#recipe=${exp_dir%%/*}
#if [[ ! -d "./$recipe" ]]; then
#    printf "Error: /workspace/icefall/egs/%s/ASR/%s does not exist.\n" "$dataset" "$recipe"
#    exit 1
#fi

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
      # 使用sed命令替换或新增参数
      decode_cmd=$(echo "$decode_cmd" | sed -E \
          -e "s|--epoch [0-9]+|--epoch $epoch|" \
          -e "s|--avg [0-9]+|--avg $avg|" \
          -e "s|--exp-dir [^ ]+|--exp-dir $epoch_dir|" \
          -e "s|--bpe-model [^ ]+|--bpe-model $bpe_model|" \
          -e "s|--lang-dir [^ ]+|--lang-dir $lang_dir|" \
          -e "/--epoch [0-9]+/! s|$| --epoch $epoch|" \
          -e "/--avg [0-9]+/! s|$| --avg $avg|" \
          -e "/--exp-dir [^ ]+/! s|$| --exp-dir $epoch_dir|" \
          -e "/--bpe-model [^ ]+/! s|$| --bpe-model $bpe_model|" \
          -e "/--lang-dir [^ ]+/! s|$| --lang-dir $lang_dir|")
      echo "decode cmd: $decode_cmd"
      eval "$decode_cmd"
    done
  done

  if [ "$last_epoch" -eq "$decode_end_epoch" ]; then
        break
  fi
done

cd /workspace/Conductor || exit
python3 /workspace/Conductor/conductor/decode/within_dataset_decode/health_check.py $dingding_token $host_ip $dataset "$epoch_dir"