#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <dataset>"
  exit 1
fi

dataset=$1

cd /workspace/icefall/egs/"$dataset"/ASR

if [ ! -L data ]; then
  echo "Data link does not exist for dataset $dataset"
  exit 1
fi

target=$(readlink -f data)

case $dataset in
  commonvoice)
    expected_target="/tests/prepared_data_devtest/commonvoice-16-en-dev/data"
    ;;
  gigaspeech)
    expected_target="/tests/prepared_data_devtest/giga-dev-dataset-fbank/data"
    ;;
  libriheavy)
    expected_target="/tests/prepared_data_devtest/libriheavy-dev/data"
    ;;
  librispeech)
    expected_target="/tests/prepared_data_devtest/librispeech-dev-dataset-fbank/data"
    ;;
  *)
    echo "Unknown dataset: $dataset"
    exit 1
    ;;
esac

if [ "$target" != "$expected_target" ]; then
  echo "Incorrect data link for dataset $dataset. Expected $expected_target, but found $target"
  exit 1
fi