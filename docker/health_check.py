import os
import logging
import argparse
from conductor.utils.basics import notify_dingding

# 检查 train.sh 进程是否存在
def check_train_process():
    try:
        with open('/workspace/compose_icefall/train.log', 'r') as f:
            lines = f.readlines()
        if any('Training finished' in line for line in lines):
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking train process: {e}")
        return False


# 检查日志文件是否存在并不为空
def check_log_file():
    try:
        log_file = '/data/log/train.log'
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking log file: {e}")
        return False


# 检查健康状态
def health_check():
    if check_train_process() and check_log_file():
        print("Health check passed")
        return True
    else:
        print("Health check failed")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dingding_token", type=str, help="Dingding robot token.")

    args = parser.parse_args()
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    notify_dingding(args.dingding_token, "进程: test")
    # Log something
    logging.debug('Health check is being performed')
    health_check()
