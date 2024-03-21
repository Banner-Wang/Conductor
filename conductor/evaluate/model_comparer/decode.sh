#!/bin/bash

usage() {
  echo "Usage: $0 -d <model_dir_path> -n <docker_name> -r <recipe> -t <trainset> -s <size>"
  exit 1
}

# 初始化变量
model_dir_path=''
docker_name=''
recipe=''
trainset=''
size=''  # 默认值

# 解析命令行选项
while getopts ":d:n:r:t:s:" opt; do
  case $opt in
    d) model_dir_path=$OPTARG ;;
    n) docker_name=$OPTARG ;;
    r) recipe=$OPTARG ;;
    t) trainset=$OPTARG ;;
    s) size=$OPTARG ;;
    \?) echo "Invalid option: -$OPTARG" >&2; usage ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage ;;
  esac
done

# 检查必须的参数是否已经设置
if [ -z "$model_dir_path" ] || [ -z "$docker_name" ]; then
  usage
fi

file_dir=$(dirname "$0")
epoch=999
avg=1
model_name=$(basename "$model_dir_path")

if [ -z "$size" ]; then
  size=$(echo "$model_name" | cut -d'_' -f3)
fi

if [ -z "$recipe" ]; then
  recipe=$(echo "$model_name" | cut -d'_' -f4)
fi

if [ -z "$trainset" ]; then
  trainset=$(echo "$model_name" | cut -d'_' -f5)
fi

# 定义可选的数据集列表
datasets=("commonvoice" "gigaspeech" "libriheavy" "librispeech")

# 检查测试数据集是否完成链接
for dataset in "${datasets[@]}"; do
  if ! docker exec -it "$docker_name" sh -c "/tests/check_data_link.sh $dataset"; then
    echo "Data link check failed for dataset $dataset. Aborting."
    exit 1
  fi
done

# 检查trainset变量值是否在可选列表中
if ! [[ " ${datasets[@]} " =~ " $trainset " ]]; then
    echo "Error: Invalid trainset value '$trainset'. Allowed values are: ${datasets[*]}"
    exit 1
fi

# 清除wer_summary.csv
file="$file_dir/wer_summary.csv"
if [ -f "$file" ]; then
    rm -f "$file"
fi

if [ ! -d "$file_dir/models" ]; then
    mkdir -p "$file_dir/models"
fi
# 下载模型
bash "$file_dir/download_model.sh" "$model_dir_path" "$file_dir/models"

# 将model软链接到所有测试数据集目录下, 软链接成功后执行测试
for dataset in "${datasets[@]}"; do
  if docker exec -it "$docker_name" sh -c "/tests/ln_model.sh $dataset $model_name $epoch $recipe"; then
    echo "Decoding test dataset: $dataset"
    if ! docker exec -it "$docker_name" sh -c "/tests/start_decode.sh $trainset $dataset $recipe $epoch $avg $size"; then
      echo "Decoding test dataset: $dataset failed. Aborting."
      exit 1
    fi
    # 获取WER
    docker exec -it "$docker_name" sh -c "cd /tests && python3 /tests/wer_summary.py $dataset"
  fi
done

if [ -f "$file" ]; then
  echo "Save wer data to $file"
  cat "$file"
else
  echo "WER data file not found."
fi