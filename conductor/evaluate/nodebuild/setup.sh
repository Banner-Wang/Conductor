#!/bin/bash

# 定义变量
WORKSPACE_DIR="/data/AI_VOICE_WORKSPACE/asr/Conductor"
ICEFALL_REPO="https://github.com/gaojiaodeng/icefall.git"
ICEFALL_BRANCH="gigaspeech_modify"
DOCKER_IMAGE="k2fsa/icefall:torch2.0.0-cuda11.7"
DOCKER_CONTAINER_NAME="icefall_decode"

# 创建目录结构
echo "开始准备环境..."

if [ ! -d "$WORKSPACE_DIR" ]; then
    echo "创建目录：$WORKSPACE_DIR"
    mkdir -p $WORKSPACE_DIR/icefall $WORKSPACE_DIR/models $WORKSPACE_DIR/prepared_data_devtest
else
    echo "目录 $WORKSPACE_DIR 已存在，跳过创建步骤。"
fi

# 克隆或更新icefall仓库
if [ ! -d "$WORKSPACE_DIR/icefall/.git" ]; then
    echo "克隆 icefall 仓库到 $WORKSPACE_DIR/icefall"
    git clone -b $ICEFALL_BRANCH $ICEFALL_REPO $WORKSPACE_DIR/icefall
else
    echo "icefall 仓库已存在，尝试更新..."
    (cd $WORKSPACE_DIR/icefall && git pull)
fi

# 同步测试数据集
echo "同步测试数据集..."
# 这里假设你已有权限访问对应的数据集位置
rsync -avz /s3mnt/AI_VOICE_WORKSPACE/asr/prepared_data_devtest/ $WORKSPACE_DIR/prepared_data_devtest

# 检查Docker容器是否已经存在
if docker ps -a | grep -q $DOCKER_CONTAINER_NAME; then
    echo "Docker容器 $DOCKER_CONTAINER_NAME 已存在。"
else
    echo "创建Docker容器 $DOCKER_CONTAINER_NAME..."
    docker run --gpus all -d --name "$DOCKER_CONTAINER_NAME" -it -v $WORKSPACE_DIR:/tests $DOCKER_IMAGE
fi

echo "环境准备完成。请根据需要手动进入Docker容器内部进行后续配置。"