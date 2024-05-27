import os
import sys
import re
import argparse
from datetime import datetime, timedelta

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(base_dir)
from conductor.utils import notify_dingding, get_logger, sync_epochs

log = get_logger(os.path.basename(__file__))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dingding_token", type=str, help="Dingding robot token.")
    parser.add_argument("hostip", type=str, help="host IP address.")
    parser.add_argument("dataset_name", type=str, help="dataset name.")
    parser.add_argument("train_cmd", type=str, help="train command")
    parser.add_argument("--training_dir", type=str, default=None, help="epoch path to decode")
    parser.add_argument("--message", type=str, default=None, help="Dingding message.")
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


# 告警函数
def alert_dingding(token, hostip, dataset_name, alert_level, message):
    alert_title = "训练进度通知"
    alert_time = bj_time()
    alert_application = f"{dataset_name} train"
    formatted_alert = """{alert_title}
    - 告警时间: {alert_time}
    - 告警级别: {alert_level}
    - 告警应用: {alert_application}
    - 主机: {hostip}
    - Message:
      - {message}
    """.format(alert_title=alert_title, alert_time=alert_time, alert_level=alert_level,
               alert_application=alert_application, hostip=hostip, message=message)

    log.debug(formatted_alert)
    notify_dingding(token, formatted_alert)


def health_check(token, hostip, dataset_name, train_cmd, **kwargs):
    training_dir = kwargs.get("training_dir")
    message = kwargs.get("message")

    if message is not None:
        alert_level = "通知"
        alert_dingding(token, hostip, dataset_name, alert_level, message)
        exit(0)

    exp_dir_pattern = r"--exp-dir\s+(\S+)"
    match = re.search(exp_dir_pattern, train_cmd)
    if not match:
        message = f"ERROR: --exp-dir not found in the command string."
        alert_level = "严重告警"
        alert_dingding(token, hostip, dataset_name, alert_level, message)
        exit(1)

    epoch_dir = f"/workspace/icefall/egs/{dataset_name}/ASR/{match.group(1)}"
    try:
        src_epoch, dest_epoch = sync_epochs(epoch_dir, training_dir, 1)
        log.info(f"Sync completed. src_epoch: {src_epoch}, dest_epoch: {dest_epoch}")
    except Exception as e:
        message = f"An error occurred: {e}"
        alert_level = "普通告警"
        alert_dingding(token, hostip, dataset_name, alert_level, message)
        exit(0)
    else:
        if src_epoch > dest_epoch:
            message = f"最新的epoch：{src_epoch}"
            alert_level = "通知"
            alert_dingding(token, hostip, dataset_name, alert_level, message)
        elif src_epoch == dest_epoch:
            log.info(f"src epoch:{src_epoch}, dest epoch:{dest_epoch}")
            exit(0)
        else:
            message = f"ERROR: src epoch:{src_epoch}, dest epoch:{dest_epoch}"
            alert_level = "严重告警"
            alert_dingding(token, hostip, dataset_name, alert_level, message)
            exit(1)


if __name__ == "__main__":
    args = get_args()
    health_check(args.dingding_token, args.hostip, args.dataset_name, args.train_cmd,
                 training_dir=args.training_dir, message=args.message)
