#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage: $0 <model_dir_path> <target_dir>"
  exit 1
fi

model_dir_path=$1
target_dir=$2
model_dir_path=${model_dir_path%/}

if [ ! -d "$target_dir/$(basename $model_dir_path)" ]; then
  rsync -av "$model_dir_path" "$target_dir"

  if [ $? -ne 0 ]; then
    echo "Error: rsync failed to download the model from $model_dir_path"
    exit 1
  fi
else
  echo "Model $(basename $model_dir_path) already exists in $target_dir"
fi