import os
import sys
import argparse

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(base_dir)
from conductor.utils import get_logger, sync_epochs

log = get_logger(os.path.basename(__file__))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync epochs between two directories.")
    parser.add_argument("src_path", type=str, help="The source directory path.")
    parser.add_argument("dest_path", type=str, help="The destination directory path.")
    parser.add_argument("--start_epoch", type=int, default=0, help="The starting epoch. Defaults to 0.")

    args = parser.parse_args()

    try:
        src_epoch, dest_epoch = sync_epochs(args.src_path, args.dest_path, args.start_epoch)
        log.info(f"Sync completed. src_epoch: {src_epoch}, dest_epoch: {dest_epoch}")
        print(f"{src_epoch},{dest_epoch}")  # 打印src_epoch和dest_epoch，用逗号分隔
    except Exception as e:
        log.info(f"An error occurred: {e}")
