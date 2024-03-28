#!/bin/bash

# 获取环境变量
icefall_path="${ICEFALL_PATH}"
cmd="${TRAIN_CMD}"
dataset_name="${DATASET_NAME}"
dataset_src="${DATASET_SRC}"
dingding_token="${DINGDING_TOKEN}"
host_ip="${HOST_IP}"
training_dir="${TRAINING_DIR}"

# 发送容器启动/重启通知
message="容器启动/重启通知"
python3 health_check.py $dingding_token $host_ip $dataset_name "${cmd}" --message "$message"

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

# 进入 对应数据集的ASR 目录
cd icefall/egs/$dataset_name/ASR || exit
# 获取最新的epoch
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

# 更新 start-epoch 参数
cmd=$(echo "$cmd" | sed "s/--start-epoch [0-9]*/--start-epoch $((max_epoch + 1))/")

# 执行训练命令
eval "$cmd"

# 发送训练完成通知
cd /workspace/Conductor/docker || exit
python3 health_check.py $dingding_token $host_ip $dataset_name "${cmd}" $dataset_src --training_dir "$training_dir"