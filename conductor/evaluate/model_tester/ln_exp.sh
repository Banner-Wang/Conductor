#!/bin/bash

if [ $# -ne 3 ]; then
  echo "Usage: $0 <dataset> <model_path> <recipe>"
  exit 1
fi

dataset=$1
model_path=$2
recipe=$3

cd /workspace/icefall/egs/"$dataset"/ASR

if [ ! -d "./$recipe" ]; then
    echo "Error: recipe ./$recipe does not exist."
    exit 1
fi

if [ -d "./$recipe/exp" ]; then
    rm -f "$recipe/exp"
fi

ln -sfv "$model_path" ./$recipe/exp
