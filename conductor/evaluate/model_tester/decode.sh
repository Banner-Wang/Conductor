#!/bin/bash

#!/bin/bash

usage() {
  echo "Usage: $0 -d <model_dir_path> -n <docker_name> -r <recipe> -t <trainset> -s <size> -e <start_epoch>"
  exit 1
}

# 初始化变量
model_dir_path=''
docker_name=''
recipe=''
trainset=''
size=''
start_epoch=1  # 默认值

# 解析命令行选项
while getopts ":d:n:r:t:s:" opt; do
  case $opt in
    d) model_dir_path=$OPTARG ;;
    n) docker_name=$OPTARG ;;
    r) recipe=$OPTARG ;;
    t) trainset=$OPTARG ;;
    s) size=$OPTARG ;;
    s) start_epoch=$OPTARG ;;
    \?) echo "Invalid option: -$OPTARG" >&2; usage ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage ;;
  esac
done

# 检查必须的参数是否已经设置
if [ -z "$model_dir_path" ] || [ -z "$docker_name" ]; then
  usage
fi

file_dir=$(dirname "$0")

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

# 检查测试数据集是否完成链接
if ! docker exec -it "$docker_name" sh -c "$file_dir/../check_data_link.sh $trainset"; then
  echo "Data link check failed for dataset $trainset. Aborting."
  exit 1
fi

if [ ! -d "$file_dir/models" ]; then
    mkdir -p "$file_dir/models"
fi

# 下载模型
output=$(python3 $file_dir/sync_epochs.py "$model_dir_path" "$file_dir/models" --start_epoch $start_epoch)
remote_epoch=$(echo $output | cut -d ',' -f1)
local_epoch=$(echo $output | cut -d ',' -f2)

if [ "$remote_epoch" -le "$local_epoch" ]; then
    echo "remote epoch is less than or equal to the local epoch. Exiting."
    exit 0
fi


for ((i=$remote_epoch; i>$local_epoch; i--));
do
    for ((j=1; j<=$i-$start_epoch; j++));
    do
        docker exec -it "$docker_name" sh -c "$file_dir/../start_decode.sh $trainset $dataset $recipe $i $j $size"
    done
done