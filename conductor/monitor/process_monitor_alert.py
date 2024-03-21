import psutil
import datetime
import sys
import os
import subprocess
import time

from conductor.utils.basics import notify_dingding


def generate_alert_message(keywords, handler, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 定义告警信息
    alert_title = "[未找到以下关键字对应的进程] [紧急处理]"
    alert_message = f"{alert_title}\n- 关键字：{'、'.join(keywords)}\n- 处理人：@{handler}\n- 告警时间：{timestamp}\n -日志详情：{message}"
    return alert_message


def find_processes(keywords):
    matched_processes = []
    current_pid = psutil.Process().pid  # 当前进程的PID
    # 获取所有进程信息
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        cmdline = proc.info['cmdline']
        if cmdline and all(keyword in ' '.join(cmdline) for keyword in
                           keywords) and proc.pid != current_pid and 'poetry' not in ' '.join(cmdline).lower():
            process_info = (f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}, "
                            f"[pname: {proc.info['name']}] [pid: {proc.info['pid']}]\n"
                            f"cmdline: {' '.join(cmdline)}\n")

            print(process_info)
            matched_processes.append(process_info)
    return matched_processes


if __name__ == "__main__":
    # 从命令行参数中获取关键字列表
    handler = sys.argv[1]
    log_path = sys.argv[2]
    keywords = sys.argv[3:]

    # 如果没有指定关键字，记录错误并退出程序
    if not keywords:
        print("请指定至少一个关键字作为命令行参数")
        sys.exit(1)

    # 查找进程并记录信息，找到匹配的进程后立即结束程序
    matched_processes = find_processes(keywords)
    if not matched_processes:
        cat_log_cmd = f"tail -10 {log_path}"
        result = subprocess.run(cat_log_cmd, shell=True, capture_output=True, text=True)

        # 检查命令执行结果
        if result.returncode == 0:
            loginfo = result.stdout
        else:
            loginfo = f"没有拿到日志信息，{result.stderr}"

        alert_message = generate_alert_message(keywords, handler, loginfo)
        print(alert_message)
        # 调用 notify_dingding 函数发送告警信息到钉钉群

        notify_dingding(alert_message)
        cmd = f"bash ./aitoolkit/asr/cancel_schedule_by_string.sh {handler}"
        os.system(cmd)
