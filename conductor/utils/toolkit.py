import os
import re
import shutil
import hashlib
import time
from basics import get_logger

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


def get_sorted_epochs(path: str, start_epoch: int):
    if not os.path.isdir(path):
        raise Exception(f"Error: Directory {path} does not exist.")

    # 获取所有epoch文件并排序
    epoch_files = sorted([f for f in os.listdir(path) if re.match(r'^epoch-\d+\.pt$', f)], key=epoch_key)

    if not epoch_files:
        log.info("no epoch files found.")
        return 0

    if f"epoch-{start_epoch}.pt" not in epoch_files:
        log.info(f"epoch-{start_epoch}.pt not found.")
        return 0

    max_epoch = int(re.findall(r'\d+', epoch_files[-1])[0])

    # 如果存在缺失的epoch文件,打印错误信息并退出
    missing_epochs = [i for i in range(start_epoch, max_epoch + 1) if f"epoch-{i}.pt" not in epoch_files]
    if missing_epochs:
        raise Exception(f"Error: Missing epochs: {', '.join(map(str, missing_epochs))}")

    return max_epoch


def copy_file(src_file: str, dest_dir: str):
    # 检查源文件是否存在
    if not os.path.isfile(src_file):
        raise Exception(f"Error: Source file '{src_file}' does not exist.")

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
        raise Exception(f"Error: File copy failed for '{src_file}'.")
    else:
        output = (f"File '{src_file}' copied to '{dest_file}' successfully.\n"
                  f"File size: {src_size} bytes\n"
                  f"MD5: {src_md5}\n"
                  f"Time elapsed: {elapsed_time:.2f} seconds\n")
        log.debug(output)
