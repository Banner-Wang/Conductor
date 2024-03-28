#!/bin/bash

if [ $# -ne 6 ]; then
  echo "Usage: $0 <trainset> <testset> <epoch_dir> <recipe> <epoch> <avg> <size> "
  exit 1
fi

trainset=$1
testset=$2
epoch_dir=$3
recipe=$4
epoch=$5
avg=$6
size=$7

case $trainset in
  commonvoice)
    bpe_model="$COMMONVOICE_DATA/en/lang_bpe_500/bpe.model"
    lang_dir="$COMMONVOICE_DATA/en/lang_bpe_500"
    ;;
  gigaspeech)
    bpe_model="$GIGASPEECH_DATA/lang_bpe_500/bpe.model"
    lang_dir="$GIGASPEECH_DATA/lang_bpe_500"
    ;;
  libriheavy)
    bpe_model="$LIBRIHEAVY_DATA/lang_bpe_500/bpe.model"
    lang_dir="$LIBRIHEAVY_DATA/lang_bpe_500"
    ;;
  librispeech)
    bpe_model="$LIBRISPEECH_DATA/lang_bpe_500/bpe.model"
    lang_dir="$LIBRISPEECH_DATA/lang_bpe_500"
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
echo "--exp-dir: $epoch_dir"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

#if [ -d "./$recipe/exp/greedy_search" ]; then
#    # 清空目录
#    rm -rf ./$recipe/exp/greedy_search/*
#fi

if [ "$size" == "medium" ]; then
  python3 ./$recipe/decode.py \
    --exp-dir $epoch_dir \
    --epoch $epoch \
    --avg $avg \
    --bpe-model $bpe_model \
    --lang-dir $lang_dir \
    --max-duration 150 \
    --use-averaged-model 0 \
    --decoding-method greedy_search
elif [ "$size" == "large" ]; then
  python3 ./$recipe/decode.py \
    --exp-dir $epoch_dir \
    --epoch $epoch \
    --avg $avg \
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