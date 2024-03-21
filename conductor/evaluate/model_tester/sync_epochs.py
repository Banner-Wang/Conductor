import os
import argparse

from conductor.utils import get_sorted_epochs, copy_file, get_logger

log = get_logger(os.path.basename(__file__))


def sync_epochs(src_path: str, dest_path: str, start_epoch: int = 0):
    """
    同步src_path和dest_path中的epoch文件。
    :param src_path: 源目录路径
    :param dest_path: 目标目录路径
    :param start_epoch: 起始epoch，默认为0
    :return: 返回src_epoch和dest_epoch的值
    """
    # 获取src_epoch和dest_epoch
    try:
        src_epoch = get_sorted_epochs(src_path, start_epoch)
    except Exception as e:
        raise Exception(f"Failed to get sorted epochs from src_path: {src_path}. Error: {e}")

    try:
        dest_epoch = get_sorted_epochs(dest_path, start_epoch)
    except Exception as e:
        raise Exception(f"Failed to get sorted epochs from dest_path: {dest_path}. Error: {e}")

    # 比较src_epoch和dest_epoch，执行相应操作
    if src_epoch > dest_epoch:
        # 需要从src_path复制文件到dest_path
        for epoch in range(dest_epoch + 1, src_epoch + 1):
            src_file = os.path.join(src_path, f"epoch-{epoch}.pt")
            try:
                copy_file(src_file, dest_path)
                log.info(f"Epoch {epoch} copied from {src_path} to {dest_path}.")
            except Exception as e:
                log.error(f"Failed to copy epoch {epoch} from {src_path} to {dest_path}. Error: {e}")
                raise
    elif src_epoch == dest_epoch:
        log.info("Both src_path and dest_path are synchronized.")
    else:
        # src_epoch < dest_epoch 的情况
        raise Exception("Error: Source has fewer epochs than destination.")

    return src_epoch, dest_epoch


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync epochs between two directories.")
    parser.add_argument("src_path", type=str, help="The source directory path.")
    parser.add_argument("dest_path", type=str, help="The destination directory path.")
    parser.add_argument("--start_epoch", type=int, default=0, help="The starting epoch. Defaults to 0.")

    args = parser.parse_args()

    try:
        src_epoch, dest_epoch = sync_epochs(args.src_path, args.dest_path, args.start_epoch)
        print(f"Sync completed. src_epoch: {src_epoch}, dest_epoch: {dest_epoch}")
    except Exception as e:
        print(f"An error occurred: {e}")
