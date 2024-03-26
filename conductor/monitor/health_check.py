import os
import sys
import re

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(base_dir)
import logging
import argparse
from conductor.utils import notify_dingding, get_sorted_epochs


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dingding_token", type=str, help="Dingding robot token.")
    parser.add_argument("dataset", type=str, help="Dingding robot token.")
    parser.add_argument("train_cmd", type=str, help="Dingding robot token.")
    return parser.parse_args()


def health_check(dataset, train_cmd):
    exp_dir_pattern = r"--exp-dir\s+(\S+)"
    match = re.search(exp_dir_pattern, train_cmd)
    if match:
        exp_dir = match.group(1)
        epoch_dir = f"/workspace/icefall/egs/{dataset}/ASR/{exp_dir}"
        max_epoch = get_sorted_epochs(epoch_dir, 1)
        notify_dingding(args.dingding_token, f"进程: 当前epoch进度：{max_epoch}")
    else:
        print("--exp-dir not found in the command string.")
        notify_dingding(args.dingding_token, "进程: --exp-dir not found in the command string.")


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=logging.DEBUG)
    health_check(args.dataset, args.train_cmd)
