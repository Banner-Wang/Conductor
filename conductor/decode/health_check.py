import argparse
import os
import torch
from datetime import datetime, timedelta

from conductor.utils import notify_dingding, get_logger

log = get_logger(os.path.basename(__file__))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dingding_token", type=str, help="Dingding robot token.")
    parser.add_argument("hostip", type=str, help="host IP address.")
    parser.add_argument("dataset_name", type=str, help="dataset name.")
    return parser.parse_args()


def bj_time():
    utc_now = datetime.utcnow()
    cst_offset = timedelta(hours=8)
    beijing_time = utc_now + cst_offset
    beijing_time_str = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    return beijing_time_str


def alert_dingding(token, hostip, dataset_name, alert_level, message):
    alert_title = "decode进度通知"
    alert_time = bj_time()
    alert_application = f"{dataset_name} decode"
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


def main():
    args = get_args()

    if torch.cuda.is_available():
        log.info('CUDA is available')
        exit(0)
    else:
        alert_level = 'WARNING'
        dingding_token = args.dingding_token
        hostip = args.hostip
        dataset_name = args.dataset_name
        message = 'CUDA is not available. restart decode container'

        alert_dingding(dingding_token, hostip, dataset_name, alert_level, message)
        exit(1)


if __name__ == '__main__':
    main()
