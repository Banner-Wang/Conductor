#!/bin/bash

required_vars=(
    "ICEFALL_PATH"
    "DINGDING_TOKEN"
    "HOST_IP"
    "TRAINING_DIR"
    "DECODE_CMD"
    "DECODE_START_EPOCH"
    "DECODE_END_EPOCH"
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
decode_cmd="${DECODE_CMD}"
decode_start_epoch=${DECODE_START_EPOCH}
decode_end_epoch="${DECODE_END_EPOCH}"

training_dirname=$(basename "$epoch_dir")
env_path="/workspace/Conductor/docker/.env"
envinfo=$(<"$env_path")

get_max_epoch() {
    local directory="$1"
    if ls "$directory"/epoch-*.pt 1> /dev/null 2>&1; then
        max_epoch=$(ls "$directory"/epoch-*.pt | sed -n 's/.*epoch-\([0-9]\+\)\.pt/\1/p' | sort -n | tail -n 1)
        echo $max_epoch
    else
        echo 0
    fi
}

check_matching_file() {
    local directory="$1"
    local epoch="$2"
    local avg="$3"
    local pattern="wer-summary-*-epoch-$epoch-avg-$avg*"
    if ls "$directory"/$pattern 1> /dev/null 2>&1; then
        return 0 # 文件存在，返回0表示成功
    else
        return 1 # 文件不存在，返回1表示失败
    fi
}

link_files() {
    local source_dir="$1"
    local destination_dir="$2"

    # 检查目的路径是否存在，如果不存在则创建
    if [ ! -d "$destination_dir" ]; then
        mkdir -p "$destination_dir"
    fi

    # 遍历源路径下的所有.pt文件
    for file in "$source_dir"/*.pt; do
        file_name=$(basename "$file")
        link_name="$destination_dir/$file_name"

        # 检查软链接是否已经存在，如果存在则跳过
        if [ -e "$link_name" ]; then
            echo "Skipping $file_name. Link already exists."
            continue
        fi

        # 创建软链接
        ln -s "$file" "$link_name"
        echo "Linked $file_name to $link_name"
    done
}

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


decode_method=$(echo "$decode_cmd" | grep -o -- '--decoding-method [^ ]*' | cut -d ' ' -f2)
decode_cuts=$(echo "$decode_cmd" | grep -o -- '--decode-cuts [^ ]*' | cut -d ' ' -f2 | sed "s/['\"]//g")
IFS=',' read -ra testsets <<< "$decode_cuts"

while true; do
  flag=0
  for testset in "${testsets[@]}"; do
    testset_epoch_dir="${epoch_dir}/${testset}"
    testset_wer_dir="${testset_epoch_dir}/${decode_method}"
    # 建立epoch.pt文件的软链接
    link_files ${epoch_dir} ${testset_epoch_dir}

    # 找到最新的epcoh
    last_epoch=$(get_max_epoch ${testset_epoch_dir})

    # 根据epoch和avg来循环decode
    for ((epoch=last_epoch; epoch>decode_start_epoch; epoch--)); do
      echo "testset: $testset epoch: $epoch >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
      for ((avg=1; avg<=epoch-decode_start_epoch; avg++)); do
      # 检查组合是否已处理
        if check_matching_file ${testset_wer_dir} "$epoch" "$avg"; then
          echo "File for epoch $epoch and avg $avg already exists, skipping..."
          continue
        fi
        echo "decode testset: $testset, decode epoch: $epoch, decode avg: $avg"
        # 使用sed命令替换或新增参数
        decode_cmd=$(echo "$decode_cmd" | sed -E \
            -e "s|--epoch [0-9]+|--epoch $epoch|" \
            -e "s|--avg [0-9]+|--avg $avg|" \
            -e "s|--exp-dir [^ ]+|--exp-dir ${testset_epoch_dir}|" \
            -e "s|--decode-cuts [^ ]+|--decode-cuts ${testset}|" \
            -e "/--epoch [0-9]+/! s|$| --epoch $epoch|" \
            -e "/--avg [0-9]+/! s|$| --avg $avg|" \
            -e "/--exp-dir [^ ]+/! s|$| --exp-dir ${testset_epoch_dir}|" \
            -e "/--decode-cuts [^ ]+/! s|$| --decode-cuts ${testset}|")
        echo "decode cmd: $decode_cmd"
        cd /workspace/icefall/egs/tz/ASR || exit
        eval "$decode_cmd"
        flag=1
      done
    done
    if [ $flag -eq 1 ]; then
      cd /workspace/Conductor || exit
      python3 conductor/visualize/wer_chart_generator.py "${testset_epoch_dir}" $decode_method $training_dirname $testset
    fi
  done
  if [ $flag -eq 1 ]; then
    cd /workspace/Conductor || exit
    python3 conductor/visualize/report_html.py $dingding_token $host_ip "${envinfo}" "https://github.com/Banner-Wang/Conductor" "${training_dirname}"
  fi

  if [ "$last_epoch" -eq "$decode_end_epoch" ]; then
      echo "All epcohs have been decoded"
      break
  fi
  sleep 600
done
