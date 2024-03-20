#!/bin/bash

if [ $# -ne 5 ]; then
  echo "Usage: $0 <trainset> <testset> <recipe> <epoch> <size>"
  exit 1
fi

trainset=$1
testset=$2
recipe=$3
epoch=$4
size=$5


case $trainset in
  commonvoice)
    bpe_model="/tests/prepared_data_devtest/commonvoice-16-en-dev/data/en/lang_bpe_500/bpe.model"
    lang_dir="/tests/prepared_data_devtest/commonvoice-16-en-dev/data/en/lang_bpe_500"
    ;;
  gigaspeech)
    bpe_model="/tests/prepared_data_devtest/giga-dev-dataset-fbank/data/lang_bpe_500/bpe.model"
    lang_dir="/tests/prepared_data_devtest/giga-dev-dataset-fbank/data/lang_bpe_500"
    ;;
  libriheavy)
    bpe_model="/tests/prepared_data_devtest/libriheavy-dev/data/lang_bpe_500/bpe.model"
    lang_dir="/tests/prepared_data_devtest/libriheavy-dev/data/lang_bpe_500"
    ;;
  librispeech)
    bpe_model="/tests/prepared_data_devtest/librispeech-dev-dataset-fbank/data/lang_bpe_500/bpe.model"
    lang_dir="/tests/prepared_data_devtest/librispeech-dev-dataset-fbank/data/lang_bpe_500"
    ;;
  *)
    echo "Unknown dataset: $trainset"
    exit 1
    ;;
esac

cd /workspace/icefall/egs/$testset/ASR

echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "Training Set: $trainset"
echo "model size: $size"
ls -l data
ls -l ./$recipe/exp/epoch-$epoch.pt
echo "--bpe-model: $bpe_model"
echo "--lang-dir: $lang_dir"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

if [ -d "./$recipe/exp/greedy_search" ]; then
    # 清空目录
    rm -rf ./$recipe/exp/greedy_search/*
fi

if [ "$size" == "medium" ]; then
  python3 ./$recipe/decode.py \
    --exp-dir ./$recipe/exp \
    --epoch $epoch \
    --avg 1 \
    --bpe-model $bpe_model \
    --lang-dir $lang_dir \
    --max-duration 150 \
    --use-averaged-model 0 \
    --decoding-method greedy_search
elif [ "$size" == "large" ]; then
  python3 ./$recipe/decode.py \
    --exp-dir ./$recipe/exp \
    --epoch $epoch \
    --avg 1 \
    --bpe-model $bpe_model \
    --lang-dir $lang_dir \
    --max-duration 150 \
    --use-averaged-model 0 \
    --num-encoder-layers 2,2,4,5,4,2 \
    --feedforward-dim 512,768,1536,2048,1536,768 \
    --encoder-dim 192,256,512,768,512,256 \
    --encoder-unmasked-dim 192,192,256,320,256,192 \
    --decoding-method greedy_search
else
  echo "Invalid size: $size, exiting..."
  exit 1
fi