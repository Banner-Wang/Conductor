import os
import argparse


def update_env_file(env_file, **kwargs):
    # 读取现有的 env_file 文件
    with open(env_file, 'r') as f:
        lines = f.readlines()

    # 创建一个字典来存储键值对
    env_dict = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_dict[key.upper()] = value

    # 更新字典中的值
    for key, value in kwargs.items():
        env_dict[key.upper()] = value

    # 写回更新后的内容到 env_file 文件
    with open(env_file, 'w') as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update env_file file')
    parser.add_argument('--env_file', default='env_file', help='Path to env_file file')
    parser.add_argument('--dataset', help='Value for DATASET')
    parser.add_argument('--train_cmd', help='Value for TRAIN_CMD')
    parser.add_argument('--log_file', help='Value for LOG_FILE')
    parser.add_argument('--dingding_token', help='Value for DINGDING_TOKEN')
    parser.add_argument('--icefall_path', help='Value for ICEFALL_PATH')

    args = parser.parse_args()

    kwargs = {k.upper(): v for k, v in vars(args).items() if v is not None and k != 'env_file'}
    update_env_file(args.env_file, **kwargs)
