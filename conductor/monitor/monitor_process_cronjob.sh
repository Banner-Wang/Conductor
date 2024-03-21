#!/bin/bash

# 检查参数是否足够
if [ $# -lt 3 ]; then
    echo "使用方法："
    echo "    bash monitor_processes_cronjob.sh <人名+编号> <关键字1> [<关键字2> ...]"
    echo ""
    echo "说明："
    echo "    - 人名+任务信息：负责人_机器_prepare(或train)_数据集"
    echo "    - 日志路径：监控进程对应的日志文件"
    echo "    - 关键字：用于监控的关键字，可以指定一个或多个"
    echo "示例：bash aitoolkit/asr/monitor_process_cronjob.sh Banner001 /data/icefall/egs/gigaspeech/ASR/train_XL.log zipformer train"
    exit 1
fi

source /etc/profile
command -v poetry >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Poetry is not installed. Installing Poetry..."
    echo "To install Poetry, please run the following command:"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# 提取人名
name="$1"
log_path="$2"
shift 2

# 提取关键字数组
keywords=("$@")

# 获取脚本和日志文件的绝对路径
root_path=$(pwd)
py_path="aitoolkit/asr/process_monitor_alert.py"
log_file="$root_path/aitoolkit/asr/$name.log"
> "$log_file"

poetry install
# 构建 Python 脚本命令
command="cd $root_path && /root/.local/bin/poetry run python3 $py_path '$name' '$log_path'"
for keyword in "${keywords[@]}"; do
    command+=" '$keyword'"
done

# 添加定时任务，每5分钟执行一次
(crontab -l ; echo "*/5 * * * * $command >> $log_file 2>&1") | crontab -
echo "定时任务添加完成："
echo "=========================="
crontab -l
echo "=========================="

echo "查看日志命令："
echo "=========================="
echo "tail -f $log_file"
echo "=========================="

