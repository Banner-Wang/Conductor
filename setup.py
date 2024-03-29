import os
import argparse
import subprocess
import re
import sys
from datetime import datetime
from conductor.utils import get_logger

log = get_logger(os.path.basename(__file__))


def is_mounted(mount_point):
    with open('/proc/mounts', 'r') as f:
        mounts = [line.split()[1] for line in f.readlines()]
        return mount_point in mounts


def check_docker_compose():
    try:
        # 检查 Docker 是否安装
        result = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            log.error("Docker is not installed on this system. Please install Docker first.")
            return False

        # 检查 Docker Compose 是否安装
        result = subprocess.run(['docker', 'compose', 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            log.error("Docker Compose is not installed on this system. Please install Docker Compose first.")
            return False

        # 检查 Docker Compose 版本号是否满足要求
        output = result.stdout.decode('utf-8').strip()
        version_str = output.split(',')[0].split()[-1].lstrip('v')  # 提取版本号字符串
        version_parts = version_str.split('.')
        major, minor, patch = [int(part) for part in version_parts]
        if major < 2 or (major == 2 and minor < 25):
            log.error(f"Your Docker Compose version ({version_str}) is too old. "
                      f"Please upgrade to version 2.25.0 or later.")
            return False

    except Exception as e:
        log.error(f"Error checking Docker and Docker Compose: {e}")
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
        log.error("Error:", e)
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

    if env_dict["TRAINING_DIR"] is None:
        cdate = datetime.now().strftime("%Y%m%d%H%M")
        dataser_src = env_dict["DATASET_SRC"]
        dataser_name = env_dict["DATASET_NAME"]
        host_ip = env_dict["HOST_IP"]
        env_dict["TRAINING_DIR"] = (f"/{dataser_src}/AI_VOICE_WORKSPACE/asr/training_model/"
                                    f"{dataser_name}_{host_ip}_{cdate}")

    if not os.path.exists(env_dict["TRAINING_DIR"]):
        os.makedirs(env_dict["TRAINING_DIR"])

    # 写回更新后的内容到 .env 文件
    with open(env_file, 'w') as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")

    return env_dict


def create_symlink(dataset: str, icefall_path: str):
    if not icefall_path:
        log.error(f"Error: --icefall_path is : {icefall_path}")
        exit(1)
    # 定义期望的目标路径字典
    dataset_paths = {
        'commonvoice': args.commonvoice_data,
        'gigaspeech': args.gigaspeech_data,
        'libriheavy': args.libriheavy_data,
        'librispeech': args.librispeech_data
    }

    # 检查 dataset 是否在字典中
    if dataset in dataset_paths:
        expected_target = dataset_paths[dataset]

        if not os.path.exists(expected_target):
            log.warning(f"Warning: Expected path not exist: {expected_target}. skipping")
            return
        symlink_path = os.path.join(icefall_path, 'egs', dataset, 'ASR')
        data_dir = 'data'
        if not os.path.isdir(symlink_path):
            log.error(f"Error: Expected path not exist: {symlink_path}")
            exit(1)

        symlink_target = os.path.join(symlink_path, data_dir)
        if not os.path.islink(symlink_target):
            os.symlink(expected_target, symlink_target)
            log.info(f"Created symlink for {dataset} at {symlink_target}")
        else:
            log.info(f"Symlink already exists for {dataset} at {symlink_target}")
    else:
        log.error(f"Unknown dataset: {dataset}")
        exit(1)


if __name__ == "__main__":
    # 检查 Docker 和 Docker Compose 的安装情况以及版本号
    if not check_docker_compose():
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Update .env file')
    parser.add_argument('--env_file', default='./docker/.env', help='Path to .env file')
    parser.add_argument('--commonvoice_data', type=str,
                        default='/nfsmnt/AI_VOICE_WORKSPACE/asr/prepared_data/commonvoice/cv_en_161/data',
                        help='common voice data')
    parser.add_argument('--gigaspeech_data', type=str,
                        default='/nfsmnt/AI_VOICE_WORKSPACE/asr/prepared_data/gigaspeech/data_XL',
                        help='gigaspeech data')
    parser.add_argument('--libriheavy_data', type=str,
                        default='/nfsmnt/AI_VOICE_WORKSPACE/asr/prepared_data/libriheavy/data',
                        help='libriheavy data')
    parser.add_argument('--librispeech_data', type=str,
                        default='/nfsmnt/AI_VOICE_WORKSPACE/asr/prepared_data/librispeech/data',
                        help='librispeech data')
    parser.add_argument('--host_ip', default=get_interface_ip(), help='host IP address')
    parser.add_argument('--dataset_src', default='nfsmnt', help='Value for DATASET SRC')
    parser.add_argument('--cd /', default=None, help='training directory, S3 or NFS')
    parser.add_argument('--model_size', default='medium', help='train model size')
    parser.add_argument('--start_epoch', default=10, type=int, help='start epoch to decode')
    parser.add_argument('--dataset_name', help='Value for DATASET')
    parser.add_argument('--train_cmd', help='Value for TRAIN_CMD')
    parser.add_argument('--dingding_token', help='Value for DINGDING_TOKEN')
    parser.add_argument('--icefall_path', help='Value for ICEFALL_PATH')

    args = parser.parse_args()

    kwargs = {k.upper(): v for k, v in vars(args).items() if v is not None and k != 'env_file'}
    env_dict = update_env_file(args.env_file, **kwargs)
    if not is_mounted("/%s" % env_dict["dataset_src".upper()]):
        log.error(f"Error: {env_dict['dataset_src'.upper()]} is not mounted.")
        exit(1)
    datasets = ("commonvoice", "gigaspeech", "libriheavy", "librispeech")
    for dataset in datasets:
        create_symlink(dataset, env_dict["icefall_path".upper()])
