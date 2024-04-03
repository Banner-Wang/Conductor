## 先决条件

- Python 3.10及以上
- Docker
- Docker Compose (版本 2.25.0 或更高)
- pip install dingtalkchatbot

## 快速开始

1. 下载 GitHub 项目到您的工作目录 `YOUR_WORK_DIR`:

```bash
cd <YOUR_WORK_DIR>
git clone https://github.com/Banner-Wang/Conductor.git
```

2. 进入 `Conductor` 目录:

```bash
cd Conductor
```

3. 根据说明执行 `setup.py` 来配置环境变量:

```bash
python3 setup.py \
    --dataset_name librispeech \
    --train_cmd "python3 ./zipformer/train.py \
        --world-size 1 \
        --num-epochs 20 \
        --start-epoch 1 \
        --use-fp16 1 \
        --exp-dir zipformer/exp \
        --causal 0 \
        --full-libri 0 \
        --base-lr 0.025 \
        --max-duration 350" \
    --dingding_token xxxxxxxxxxxxxxxxxxxxxx \
    --icefall_path "/tmp/banner/Conductor/icefall"
```

4. 启动 Docker 容器开始训练:

```bash
cd docker
docker compose -p <YOUR_DOCKER_NAME> up train -d 

```

## 设置环境说明

```bash
python setup.py [选项]
```

### 选项

- `--dataset_name`: 数据集名称
- `--dingding_token`: DingDing 令牌的值
- `--icefall_path`: Icefall 作业路径
- `--commonvoice_data_dir`: Common Voice 数据目录 (
  默认: `AI_VOICE_WORKSPACE/asr/prepared_data/commonvoice/cv_en_161/data`)
- `--gigaspeech_data_dir`: GigaSpeech 数据目录 (默认: `AI_VOICE_WORKSPACE/asr/prepared_data/gigaspeech/data_XL`)
- `--libriheavy_data_dir`: LibriHeavy 数据目录 (默认: `AI_VOICE_WORKSPACE/asr/prepared_data/libriheavy/data`)
- `--librispeech_data_dir`: LibriSpeech 数据目录 (默认: `AI_VOICE_WORKSPACE/asr/prepared_data/librispeech/data`)
- `--env_file`: `.env` 文件的路径 (默认: `./docker/.env`)
- `--dataset_src`: 数据集源根路径 (默认: `nfsmnt`)
- `--decode_start_epoch`: 开始解码的轮次 (默认: 10)
- `--training_dir`: 训练目录
- `--train_cmd`: 训练命令
- `--decode_cmd`: 解码命令
- `--clean`: 清空 `.env` 文件的内容
- `--show`: 显示 `.env` 文件的内容

## 功能

1. 检查是否安装了 Docker 和 Docker Compose,并满足版本要求。
2. 读取现有的 `.env` 文件(如果存在),并根据提供的选项更新环境变量。
3. 检查是否挂载了所需的目录(`/s3mnt` 和 `/nfsmnt`)。
4. 获取主机 IP 地址。
5. 使用新的环境变量更新 `.env` 文件。
6. 在 Icefall 项目中为指定的数据集创建符号链接。
7. 提供选项来清空 `.env` 文件的内容(`--clean`)和显示 `.env` 文件的内容(`--show`)。

4. 启动 Docker 容器:

###### 4.1 启动训练

```bash
cd docker
docker compose -p <YOUR_DOCKER_NAME> up train -d 

```

###### 4.2 启动decode

```bash
cd docker
docker compose -p <YOUR_DOCKER_NAME> up decode -d 
```

5. 清空 `.env` 文件的内容:

```bash
python setup.py --clean
```

6. 显示 `.env` 文件的内容:

```bash
python setup.py --show
```

## 注意事项

- 该脚本需要挂载某些目录(`/s3mnt` 和 `/nfsmnt`)。如果它们没有被挂载,脚本将以错误退出。
- 该脚本使用 `conductor.utils.get_logger` 函数记录消息。确保已安装 `conductor` 包并正确配置。
- 该脚本假设 Icefall 项目中存在某些路径和目录。如果需要,请根据你的项目结构修改路径。