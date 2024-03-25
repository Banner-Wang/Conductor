# 使用 k2fsa/icefall:torch2.0.0-cuda11.7 作为基础镜像
FROM k2fsa/icefall:torch2.0.0-cuda11.7

# 更新软件包索引并安装必要的软件包
RUN apt-get update && apt-get install -y \
    jq \
    git-lfs \
    && git-lfs install

# 安装 Python 依赖包
RUN pip install \
    pypinyin \
    speechcolab \
    pandas

# # 复制并运行脚本 AAA
# COPY train.sh /workspace/icefall
# COPY health_check.py /workspace/icefall
# RUN chmod +x AAA
# CMD ["./AAA"]