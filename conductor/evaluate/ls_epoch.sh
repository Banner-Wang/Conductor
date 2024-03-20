#!/bin/bash

# 显示脚本的使用方式
if [ -z "$1" ]; then
    echo "Usage: $0 <path>"
    exit 1
fi

path="$1"

# 检查路径是否存在
if [ ! -d "$path" ]; then
    echo "Error: Directory $path does not exist."
    exit 1
fi

# 获取所有epoch文件并排序
epoch_files=($(find "$path" -name "epoch-*.pt" 2>/dev/null | sort -V))

# 如果没有epoch文件,退出
if [ ${#epoch_files[@]} -eq 0 ]; then
    echo "No epoch files found."
    exit 1
fi

# 检查epoch-1.pt是否存在
if [[ ! " ${epoch_files[@]} " =~ "epoch-1.pt" ]]; then
    echo "Error: epoch-1.pt not found or sequence is not continuous."
    exit 1
fi

# 获取最大epoch编号
max_epoch=$(basename "${epoch_files[-1]}" | sed 's/epoch-\([0-9]*\)\.pt/\1/')

# 检查缺失的epoch文件
missing_epochs=()
for ((i=1; i<=max_epoch; i++)); do
    if [ ! -f "$path/epoch-$i.pt" ]; then
        missing_epochs+=($i)
    fi
done

# 如果存在缺失的epoch文件,打印错误信息并退出
if [ ! -z "${missing_epochs[*]}" ]; then
    echo "Error: Missing epochs: ${missing_epochs[*]}"
    exit 1
fi

# 打印所有epoch编号
for file in "${epoch_files[@]}"; do
    basename "$file" | sed 's/epoch-\([0-9]*\)\.pt/\1/'
done
