# 说明

#### 安装poetry
    curl -sSL https://install.python-poetry.org | python3 -

#### 快速开始
```shell
git clone https://github.com/Banner-Wang/Conductor.git
cd Conductor/conductor/monitor
export DINGDING_ROBOT_TOKEN=<YOUR_ROBOT_TOKEN>
```

##### 设置进程监控定时任务
示例：
*注意： 监控多个进程时，人名编号递增即可*
```shell
bash aitoolkit/asr/monitor_process_cronjob.sh Banner001 <YOU_LOG_PTAH> zipformer train
```

##### 删除定时任务
示例：
```shell
bash aitoolkit/asr/cancel_schedule_by_string.sh Banner001
```

##### 查看日志

```shell
cat aitoolkit/asr/Banner001.log # 日志文件名与人名保持一致
```