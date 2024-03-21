#!/bin/bash

if [ $# -ne 4 ]; then
  echo "Usage: $0 <dataset> <model_name> <epoch> <recipe>"
  exit 1
fi

dataset=$1
model_name=$2
epoch=$3
recipe=$4

cd /workspace/icefall/egs/"$dataset"/ASR

if [ ! -d "./$recipe" ]; then
    echo "Error: recipe ./$recipe does not exist."
    exit 1
fi

mkdir -p ./$recipe/exp/

if [ -L "./$recipe/exp/epoch-$epoch.pt" ]; then
  rm "./$recipe/exp/epoch-$epoch.pt"
fi

# 检查pretrained.pt文件是否存在
if [ ! -e "/tests/models/$model_name/pretrained.pt" ]; then
    echo "Error: pretrained.pt file does not exist."
    exit 1
fi

ln -sfv /tests/models/"$model_name"/pretrained.pt ./$recipe/exp/epoch-"$epoch".pt

# Check if the symlink was created successfully
if [ $? -eq 0 ]; then
  echo "Soft link successfully"
else
  echo "Error: Failed to create soft link"
  exit 1
fi
