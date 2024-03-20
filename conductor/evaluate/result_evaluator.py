import os
import sys
import re
import shutil
import hashlib
import time
from conductor.utils.parse import get_logger

log = get_logger(os.path.basename(__file__))


def epoch_key(s):
    match = re.match(r'^epoch-(\d+)\.pt$', s)
    if match:
        return int(match.group(1))
    else:
        return 0


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_sorted_epochs(path):
    if not os.path.isdir(path):
        log.error(f"Error: Directory {path} does not exist.")
        sys.exit(1)

    # 获取所有epoch文件并排序
    epoch_files = sorted([f for f in os.listdir(path) if re.match(r'^epoch-\d+\.pt$', f)], key=epoch_key)

    if not epoch_files:
        log.error("No epoch files found.")
        sys.exit(1)

    if "epoch-1.pt" not in epoch_files:
        log.error("Error: epoch-1.pt not found or sequence is not continuous.")
        sys.exit(1)

    max_epoch = int(re.findall(r'\d+', epoch_files[-1])[0])

    # 如果存在缺失的epoch文件,打印错误信息并退出
    missing_epochs = [i for i in range(1, max_epoch + 1) if f"epoch-{i}.pt" not in epoch_files]
    if missing_epochs:
        log.error(f"Error: Missing epochs: {', '.join(map(str, missing_epochs))}")
        sys.exit(1)

    return max_epoch


def copy_file(src_file: str, dest_dir: str):
    # 检查源文件是否存在
    if not os.path.isfile(src_file):
        log.error(f"Error: Source file '{src_file}' does not exist.")
        sys.exit(1)

    # 检查目标目录是否存在,不存在则创建
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 获取源文件信息
    src_size = os.path.getsize(src_file)
    src_md5 = calculate_md5(src_file)

    # 复制文件
    dest_file = os.path.join(dest_dir, os.path.basename(src_file))
    start_time = time.time()
    shutil.copy2(src_file, dest_file)
    elapsed_time = time.time() - start_time

    # 验证复制后的文件
    dest_size = os.path.getsize(dest_file)
    dest_md5 = calculate_md5(dest_file)
    if src_size != dest_size or src_md5 != dest_md5:
        log.error(f"Error: File copy failed for '{src_file}'.")
        sys.exit(1)
    else:
        output = (f"File '{src_file}' copied to '{dest_file}' successfully.\n"
                  f"File size: {src_size} bytes\n"
                  f"MD5: {src_md5}\n"
                  f"Time elapsed: {elapsed_time:.2f} seconds\n")
        log.debug(output)


def main():
    # 显示脚本的使用方式
    if len(sys.argv) < 2:
        log.error(f"Usage: {sys.argv[0]} <path>")
        sys.exit(1)

    path = sys.argv[1]
    max_epoch = get_sorted_epochs(path)
    log.debug(max_epoch)


if __name__ == "__main__":
    main()
