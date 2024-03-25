# 自定义 Docker 镜像

这是一个基于 `k2fsa/icefall:torch2.0.0-cuda11.7` 镜像构建的自定义 Docker 镜像,添加了一些额外的软件包和运行脚本。

## 镜像内容

- 基础镜像: `k2fsa/icefall:torch2.0.0-cuda11.7`
- 额外安装的 Python 包:
  - pypinyin
  - speechcolab
  - pandas
- 额外安装的软件包:
  - jq
  - git-lfs
- 运行脚本: `AAA`

## 使用方法

1. 构建镜像:

   ```bash
   docker build -t your-image-name:tag .