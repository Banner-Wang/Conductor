import os
import argparse
import subprocess
import re


def get_interface_ip():
    try:
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        output = result.stdout

        ipv4_pattern = r'inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/\d+\s+.*global(?! docker).*\s+(\w+)$'
        matches = re.findall(ipv4_pattern, output, re.MULTILINE)

        for match in matches:
            ip_address, interface = match
            return ip_address
    except Exception as e:
        print("Error:", e)
        return {}


def update_env_file(env_file, **kwargs):
    env_dict = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_dict[key.upper()] = value

    # 更新字典中的值
    for key, value in kwargs.items():
        env_dict[key.upper()] = value

    # 写回更新后的内容到 .env 文件
    with open(env_file, 'w') as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update .env file')
    parser.add_argument('--env_file', default='./.env', help='Path to .env file')
    parser.add_argument('--host_ip', default=get_interface_ip(), help='host IP address')
    parser.add_argument('--dataset_src', default="data", help='Value for DATASET SRC')
    parser.add_argument('--dataset_name', help='Value for DATASET')
    parser.add_argument('--train_cmd', help='Value for TRAIN_CMD')
    parser.add_argument('--log_file', help='Value for LOG_FILE')
    parser.add_argument('--dingding_token', help='Value for DINGDING_TOKEN')
    parser.add_argument('--icefall_path', help='Value for ICEFALL_PATH')

    args = parser.parse_args()

    kwargs = {k.upper(): v for k, v in vars(args).items() if v is not None and k != 'env_file'}
    update_env_file(args.env_file, **kwargs)
