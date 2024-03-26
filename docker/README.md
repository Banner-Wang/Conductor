# icefall 训练环境

## 介绍

这个项目是一个 Docker Compose 配置文件,用于定义和配置名为 "icefall"
的服务,该服务用于训练语音识别模型。它包括以下主要组件:

1. **Dockerfile**:基于 `k2fsa/icefall:torch2.0.0-cuda11.7` 镜像构建,安装了必要的依赖包。

2. **Docker Compose 配置文件**:定义了 "icefall" 服务的配置,包括共享内存大小、工作目录、环境变量、数据卷映射、GPU
   资源预留、重启策略和健康检查等。

3. **train.sh 脚本**:用于在 Docker 容器中设置 icefall 工作环境,并根据训练进度和日志调整参数后运行训练命令。

4. **health_check.py 脚本**:用于定期检查训练进度,并通过钉钉机器人进行通知。

5. **setup.py 脚本**:用于更新 ` env_file` 文件中的环境变量。

## 快速开始

1. 下载 GitHub 项目到您的工作目录 `YOUR_WORK_DIR`:

```bash
git clone https://github.com/Banner-Wang/Conductor.git <YOUR_WORK_DIR>
```

2. 进入 `Conductor/docker` 目录:

```bash
cd <YOUR_WORK_DIR>/Conductor/docker
```

3. 根据说明执行 `setup.py` 来配置环境变量:

```bash
python3 setup.py --dataset <YOUR_DATASET> --train_cmd "<YOUR_TRAIN_CMD>" --log_file <YOUR_LOG_FILE> --dingding_token <YOUR_DINGDING_TOKEN> --icefall_path <YOUR_ICEFALL_PATH>
```

替换上面命令中的占位符为您实际的值:

- `YOUR_DATASET`: 您要使用的数据集名称
- `YOUR_TRAIN_CMD`: 训练命令,如 `python3 train.py ...`
- `YOUR_LOG_FILE`: 训练日志文件路径
- `YOUR_DINGDING_TOKEN`: 钉钉机器人的 Token
- `YOUR_ICEFALL_PATH`: icefall 代码的本地路径

4. 启动 Docker 容器:

```bash
docker compose -p <YOUR_DOCKER_NAME> up -d
```

这将使用 `YOUR_DOCKER_NAME` 作为容器前缀名称启动服务。您可以通过 `tail -f <YOUR_LOG_FILE>` 命令查看日志,确认训练过程正常进行。

现在,您已经成功配置并启动了 icefall 训练环境。训练完成后,模型文件将保存在 `icefall/egs/${YOUR_DATASET}/ASR/` 目录下。

## 使用方法

1. 确保安装了 Docker 和 Docker Compose。

2. 将代码克隆到本地目录。

3. 准备好训练数据集,并将其放置在 `/data/AI_VOICE_WORKSPACE/asr/prepared_data/` 目录下。

4. 修改 `env_file` 文件,设置必要的环境变量,如 `DATASET`、`TRAIN_CMD`、`LOG_FILE`、`DINGDING_TOKEN` 和 `ICEFALL_PATH` 等。

5. 运行 `docker-compose up -d` 命令启动服务。

6. 通过 `docker logs` 命令查看日志,确认训练过程正常进行。

7. 训练完成后,模型文件将保存在 `icefall/egs/${DATASET}/ASR/` 目录下。

## 配置文件解释

### Docker Compose 配置

- `services.icefall` 定义了 "icefall" 服务。
- `shm_size` 设置共享内存大小。
- `build` 指定使用当前目录下的 Dockerfile 构建镜像。
- `working_dir` 设置容器中的工作目录。
- `env_file` 从 ` env_file` 文件加载环境变量。
- `volumes` 映射主机目录到容器内。
- `command` 定义容器启动后执行的命令。
- `deploy` 定义服务部署相关配置,如 GPU 资源预留和重启策略。
- `healthcheck` 定义健康检查设置。

### train.sh 脚本

该脚本的主要作用是:

- 自动链接数据和代码
- 根据之前的训练进度设置开始 epoch
- 根据错误日志调整训练参数
- 运行修改后的训练命令

### health_check.py 脚本

该脚本用于定期检查训练进度,并通过钉钉机器人进行通知。

### setup.py 脚本

该脚本用于更新 ` env_file` 文件中的环境变量。