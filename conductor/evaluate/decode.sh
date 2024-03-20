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

root_dir=$(dirname "$0")
epoch=999
model_name=$(basename "$model_dir_path")

if [ -z "$recipe" ]; then
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

# 检查trainset变量值是否在可选列表中
if ! [[ " ${datasets[@]} " =~ " $trainset " ]]; then
    echo "Error: Invalid trainset value '$trainset'. Allowed values are: ${datasets[*]}"
    exit 1
fi

# 下载模型
bash "$root_dir/download_model.sh" "$model_dir_path" "$root_dir/models"

# 建立软链接和检查数据链接
for dataset in "${datasets[@]}"; do
  docker exec -it "$docker_name" sh -c "/tests/ln_model.sh $dataset $model_name $epoch $recipe"
  if ! docker exec -it "$docker_name" sh -c "/tests/check_data_link.sh $dataset"; then
    echo "Data link check failed for dataset $dataset. Aborting."
    exit 1
  fi
done

# 执行测试
for testset in "${datasets[@]}"; do
  echo "Decoding test dataset: $testset"
  docker exec -it "$docker_name" sh -c "/tests/start_decode.sh $trainset $testset $recipe $epoch $size"
done

# 获取WER
file="$root_dir/wer_summary.csv"
if [ -f "$file" ]; then
    rm -f "$file"
fi

for dataset in "${datasets[@]}"; do
  docker exec -it "$docker_name" sh -c "cd /tests && python3 /tests/wer_summary.py $dataset"
done

if [ -f "$file" ]; then
  echo "Save wer data to $file"
  cat "$file"
else
  echo "WER data file not found."
fi