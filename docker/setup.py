import os
import argparse
import subprocess
import re
import sys
from datetime import datetime


def check_docker_compose():
    try:
        # 检查 Docker 是否安装
        result = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("Docker is not installed on this system. Please install Docker first.")
            return False

        # 检查 Docker Compose 是否安装
        result = subprocess.run(['docker', 'compose', 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("Docker Compose is not installed on this system. Please install Docker Compose first.")
            return False

        # 检查 Docker Compose 版本号是否满足要求
        output = result.stdout.decode('utf-8').strip()
        version_str = output.split(',')[0].split()[-1].lstrip('v')  # 提取版本号字符串
        version_parts = version_str.split('.')
        major, minor, patch = [int(part) for part in version_parts]
        if major < 2 or (major == 2 and minor < 25):
            print(f"Your Docker Compose version ({version_str}) is too old. Please upgrade to version 2.25.0 or later.")
            return False

    except Exception as e:
        print(f"Error checking Docker and Docker Compose: {e}")
        return False

    return True


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
    # 检查 Docker 和 Docker Compose 的安装情况以及版本号
    if not check_docker_compose():
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Update .env file')
    parser.add_argument('--env_file', default='./.env', help='Path to .env file')
    parser.add_argument('--host_ip', default=get_interface_ip(), help='host IP address')
    parser.add_argument('--dataset_src', default='nfsmnt', help='Value for DATASET SRC')
    parser.add_argument('--log_file', default='/workspace/Conductor/docker/train.log', help='Value for LOG_FILE')
    parser.add_argument('--training_dir', default=None, help='training directory, S3 or NFS')
    parser.add_argument('--dataset_name', help='Value for DATASET')
    parser.add_argument('--train_cmd', help='Value for TRAIN_CMD')
    parser.add_argument('--dingding_token', help='Value for DINGDING_TOKEN')
    parser.add_argument('--icefall_path', help='Value for ICEFALL_PATH')

    args = parser.parse_args()
    if args.training_dir is None:
        cdate = datetime.now().strftime("%Y%m%d%H")
        args.training_dir = f"/{args.dataset_src}/AI_VOICE_WORKSPACE/asr/training_model/{args.dataset_name}_{args.hostip}_{cdate}"
    kwargs = {k.upper(): v for k, v in vars(args).items() if v is not None and k != 'env_file'}
    update_env_file(args.env_file, **kwargs)
