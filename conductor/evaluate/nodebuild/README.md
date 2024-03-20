# AI ASR 测试环境准备指南

本指南提供了如何快速准备AI ASR测试环境的步骤，包括环境的设置和必要软件的安装。

## 快速开始

1. **下载和运行`setup.sh`脚本**

    脚本会自动准备环境，包括创建目录结构、克隆或更新`icefall`仓库、同步测试数据集、以及创建或检查Docker容器。

    ```bash
    # setup.sh路径： Conductor/blob/main/conductor/evaluate/nodebuild/setup.sh
    chmod +x setup.sh
    ./setup.sh
    ```

    请将`<脚本URL>`替换为实际的脚本下载链接。

2. **进入Docker容器**

    如果容器已经通过脚本创建，你可以使用以下命令进入容器：

    ```bash
    docker exec -it icefall_decode bash
    ```

3. **在Docker容器内部进行配置**

    根据需要，你可能需要在Docker容器内部执行一些额外的配置步骤，例如安装Python依赖或配置软链接。

    ```bash
    pip install pypinyin speechcolab pandas
    apt-get update && apt-get install -y jq git-lfs && git-lfs install
    ```

    然后，使用本地的`icefall`版本替换容器中的版本（如果需要）：

    ```bash
    rm -rf /workspace/icefall && ln -s /tests/icefall /workspace/icefall
    ```

## 注意事项

- 确保在执行脚本之前，你已经安装了Docker并且具有执行Docker命令的权限。
- 脚本在检查资源（如目录、Docker容器）是否已存在时，避免了重复创建，提高了环境准备的效率。

## 支持和贡献

如果你在使用脚本时遇到问题，或者有改进的建议，欢迎联系BannerWang。