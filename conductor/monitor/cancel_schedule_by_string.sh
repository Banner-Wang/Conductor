#!/bin/bash

# 检查是否提供了关键字参数
if [ $# -eq 0 ]; then
    echo "请提供要删除的关键字"
    echo "示例：bash cancel_schedule_by_string.sh Banner python zipformer train"
    exit 1
fi

# 将关键字连接成一个模式，用于匹配定时任务
pattern=".*$(IFS="|"; echo "$*").*"
echo "$pattern"

# 列出当前用户的所有定时任务，并将结果存储到临时文件中
crontab -l > /tmp/crontab.tmp

# 使用 grep 命令查找要删除的定时任务，并将结果写回到临时文件中
grep -vE "$pattern" /tmp/crontab.tmp > /tmp/crontab.tmp2

# 将更新后的定时任务写回到 crontab 中
crontab /tmp/crontab.tmp2

# 删除临时文件
rm /tmp/crontab.tmp /tmp/crontab.tmp2

crontab -l

echo "定时任务已删除"
