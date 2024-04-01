import os
import argparse
import subprocess
import re
import sys
from datetime import datetime
from conductor.utils import get_logger

log = get_logger(os.path.basename(__file__))
NFS_SERVER_IP = ['10.68.89.114', '172.16.1.223']
DATASETS = ("commonvoice", "gigaspeech", "libriheavy", "librispeech")


def get_args():
    parser = argparse.ArgumentParser(description='Update .env file')
    parser.add_argument('--commonvoice_data_dir',
                        type=str,
                        default='AI_VOICE_WORKSPACE/asr/prepared_data/commonvoice/cv_en_161/data',
                        help='common voice data')
    parser.add_argument('--gigaspeech_data_dir',
                        type=str,
                        default='AI_VOICE_WORKSPACE/asr/prepared_data/gigaspeech/data_XL',
                        help='gigaspeech data')
    parser.add_argument('--libriheavy_data_dir',
                        type=str,
                        default='AI_VOICE_WORKSPACE/asr/prepared_data/libriheavy/data',
                        help='libriheavy data')
    parser.add_argument('--librispeech_data_dir',
                        type=str,
                        default='AI_VOICE_WORKSPACE/asr/prepared_data/librispeech/data',
                        help='librispeech data')

    parser.add_argument('--env_file', default='./docker/.env', help='Path to .env file')
    parser.add_argument('--dataset_src', default='nfsmnt', help='dataset src root path')
    parser.add_argument('--decode_start_epoch', default=10, type=int, help='start epoch to decode')
    parser.add_argument('--decode_end_epoch', help='end epoch to decode')
    parser.add_argument('--dataset_name', help='dataset name')
    parser.add_argument('--dingding_token', help='Value for dingding token')
    parser.add_argument('--icefall_path', help='icefall job path')
    parser.add_argument('--training_dir', help='training directory')
    parser.add_argument('--train_cmd', help='train cmd')
    parser.add_argument('--decode_cmd', help='decode cmd')

    parser.add_argument('--clean', action='store_true', help='Clear the contents of the .env file')
    parser.add_argument('--show', action='store_true', help='Show the contents of the .env file')

    return parser.parse_args()


def clean_env_file(env_file_path):
    if os.path.exists(env_file_path):
        os.remove(env_file_path)
        log.info(f"Cleared the contents of {env_file_path}")


def show_env_file_content(env_file_path):
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as file:
            log.info(f"Contents of {args.env_file}:\n{file.read()}")
    else:
        log.error(f"Error: {env_file_path} does not exist.")


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


def __mnt_check(*mnt_dirs):
    for _mnt_dir in mnt_dirs:
        if not is_mounted(_mnt_dir):
            log.error(f"Error: {_mnt_dir} is not mounted.")
            exit(1)


def __get_interface_ip():
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


def update_env_file(env_file_path, **kwargs):
    env_dict = {}

    # 读取现有的环境变量文件
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_dict[key.upper()] = value
    # 更新环境变量
    for key, value in kwargs.items():
        key_upper = key.upper()
        env_dict[key_upper] = value

    host_ip = __get_interface_ip()
    env_dict["HOST_IP"] = host_ip
    if host_ip in NFS_SERVER_IP:
        env_dict["DATASET_SRC"] = "data"
        __mnt_check('/s3mnt')
    else:
        __mnt_check('/s3mnt', '/nfsmnt')

    env_dict["COMMONVOICE_DATA_DIR"] = os.path.join('/', env_dict["DATASET_SRC"], env_dict["COMMONVOICE_DATA_DIR"])
    env_dict["GIGASPEECH_DATA_DIR"] = os.path.join('/', env_dict["DATASET_SRC"], env_dict["GIGASPEECH_DATA_DIR"])
    env_dict["LIBRIHEAVY_DATA_DIR"] = os.path.join('/', env_dict["DATASET_SRC"], env_dict["LIBRIHEAVY_DATA_DIR"])
    env_dict["LIBRISPEECH_DATA_DIR"] = os.path.join('/', env_dict["DATASET_SRC"], env_dict["LIBRISPEECH_DATA_DIR"])

    if "TRAINING_DIR" not in env_dict:
        cdate = datetime.now().strftime("%Y%m%d%H%M")
        dataset_src = env_dict.get("DATASET_SRC")
        dataset_name = env_dict.get("DATASET_NAME")
        training_dir = f"/{dataset_src}/AI_VOICE_WORKSPACE/asr/training_model/{dataset_name}_{host_ip}_{cdate}"
        env_dict["TRAINING_DIR"] = training_dir
        os.makedirs(training_dir, exist_ok=True)

    # 写入更新后的环境变量到文件
    try:
        with open(env_file_path, 'w') as file:
            for key, value in env_dict.items():
                file.write(f"{key}={value}\n")
    except IOError as error:
        print(f"Error writing to {env_file_path}: {error}")

    return env_dict


def create_symlink(dataset: str, env_dict: dict):
    icefall_path = env_dict["ICEFALL_PATH"]
    if not icefall_path:
        log.error(f"Error: --icefall_path is : {icefall_path}")
        exit(1)
    dataset_path = env_dict[f"{dataset.upper()}_DATA_DIR"]
    if not os.path.exists(dataset_path):
        log.warning(f"Warning: Expected path not exist: {dataset_path}. skipping")
        return

    symlink_path = os.path.join(icefall_path, 'egs', dataset, 'ASR')
    if not os.path.isdir(symlink_path):
        log.error(f"Error: Expected path not exist: {symlink_path}")
        exit(1)

    data_dir = 'data'
    symlink_target = os.path.join(symlink_path, data_dir)
    if not os.path.islink(symlink_target):
        os.symlink(dataset_path, symlink_target)
        log.info(f"Created symlink for {dataset_path} at {symlink_target}")
    else:
        log.info(f"Symlink already exists for {dataset} at {symlink_target}")


if __name__ == "__main__":
    # Check Docker and Docker Compose installation and version
    if not check_docker_compose():
        sys.exit(1)

    args = get_args()
    kwargs = {k.upper(): v for k, v in vars(args).items() if
              v is not None and k != 'env_file' and k != 'clean' and k != 'show'}
    if args.clean:
        clean_env_file(args.env_file)
        sys.exit(0)
    if args.show:
        show_env_file_content(args.env_file)
        sys.exit(0)
    else:
        env_dict = update_env_file(args.env_file, **kwargs)
