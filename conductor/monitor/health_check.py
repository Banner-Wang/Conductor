import os
import sys
import re
import argparse
from datetime import datetime, timedelta

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(base_dir)
from conductor.utils import notify_dingding, get_sorted_epochs, get_logger

log = get_logger(os.path.basename(__file__))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dingding_token", type=str, help="Dingding robot token.")
    parser.add_argument("hostip", type=str, help="host IP address.")
    parser.add_argument("dataset", type=str, help="Dingding robot token.")
    parser.add_argument("train_cmd", type=str, help="Dingding robot token.")
    return parser.parse_args()


def bj_time():
    utc_now = datetime.utcnow()
    cst_offset = timedelta(hours=8)
    beijing_time = utc_now + cst_offset
    beijing_time_str = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    return beijing_time_str


def save_max_epoch(max_epoch, file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                existing_value = f.read().strip()
        else:
            existing_value = 0
        existing_value = int(existing_value)
        if existing_value < max_epoch:
            with open(file_path, 'w') as f:
                f.write(str(max_epoch))
            return 1
        elif existing_value == max_epoch:
            with open(file_path, 'w') as f:
                f.write(str(max_epoch))
            return 0
        else:
            return -1
    except Exception as e:
        log.error(f"Error occurred while saving max_epoch: {e}")


def health_check(token, hostip, dataset, train_cmd):
    exp_dir_pattern = r"--exp-dir\s+(\S+)"
    match = re.search(exp_dir_pattern, train_cmd)
    file_path = "./max_epoch.txt"
    if match:
        exp_dir = match.group(1)
        epoch_dir = f"/workspace/icefall/egs/{dataset}/ASR/{exp_dir}"
        max_epoch = get_sorted_epochs(epoch_dir, 1)
        flag = save_max_epoch(max_epoch, file_path)
        if flag == 0:
            log.debug(f"exist epoch:{max_epoch}, max epoch:{max_epoch}, file:{file_path}")
            return
        elif flag == -1:
            message = f"ERROR: exist epoch:{max_epoch}, max epoch:{max_epoch}"
            alert_title = "训练进度通知"
            alert_level = "警告"
        elif flag == 1:
            message = f"最新的epoch：{max_epoch}"
            alert_title = "训练进度通知"
            alert_level = "通知"
        else:
            return
    else:
        message = f"ERROR: --exp-dir not found in the command string."
        alert_title = "训练进度通知"
        alert_level = "警告"

    alert_time = bj_time()
    alert_application = f"{dataset} train"
    formatted_alert = f"""
    告警标题：{alert_title}
    告警时间：{alert_time}
    告警级别：{alert_level}
    告警应用：{alert_application}
    告警内容：{message}
    主机：{hostip}
    """
    log.debug(formatted_alert)
    notify_dingding(token, formatted_alert)


if __name__ == "__main__":
    args = get_args()
    health_check(args.dingding_token, args.hostip, args.dataset, args.train_cmd)
