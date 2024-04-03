import os
import sys
import re
import argparse
import shutil
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(base_dir)
from conductor.utils import link_dingding, get_logger

log = get_logger(os.path.basename(__file__))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dingding_token", type=str, help="Dingding robot token.")
    parser.add_argument("hostip", type=str, help="host IP address.")
    parser.add_argument("dataset_name", type=str, help="dataset name.")
    parser.add_argument("training_dir", type=str, help="epoch path to decode.")
    parser.add_argument("decode_method", type=str, help="decode method.")
    parser.add_argument("testset_name", type=str, help="testset name.")
    return parser.parse_args()


def bj_time():
    utc_now = datetime.utcnow()
    cst_offset = timedelta(hours=8)
    beijing_time = utc_now + cst_offset
    beijing_time_str = beijing_time.strftime("%Y%m%d%H%M")
    return beijing_time_str


def process_wer_files(file_list):
    data = []
    for file_name in file_list:
        # 解析文件名获取测试集、epoch和avg的值
        match = re.search(r'wer-summary-(.+)-greedy_search-epoch-(\d+)-avg-(\d+)', file_name)
        if match:
            test_set, epoch, avg = match.groups()
            # 读取文件内容获取WER值
            with open(file_name, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('greedy_search'):
                        wer = float(line.split()[1])
                        data.append((test_set, int(epoch), int(avg), wer))
                        break
    return data


def save_data_to_file(data, file_name):
    with open(file_name, 'w') as f:
        for item in data:
            f.write(f"{item[0]},{item[1]},{item[2]},{item[3]}\n")


def plot_data(data):
    test_sets = list(set(item[0] for item in data))
    png_arr = []
    for test_set in test_sets:
        epochs = sorted(set(item[1] for item in data if item[0] == test_set))
        avg_values = sorted(set(item[2] for item in data if item[0] == test_set), reverse=True)  # 反向排序avg值

        # 创建一个二维数组来存储WER值
        wer_matrix = np.zeros((len(avg_values), len(epochs)))
        wer_matrix[:] = np.nan  # 将所有元素设置为NaN

        for item in data:
            if item[0] == test_set:
                epoch_idx = epochs.index(item[1])
                avg_idx = avg_values.index(item[2])
                wer_matrix[avg_idx, epoch_idx] = item[3]

        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(wer_matrix, cmap='YlGn_r')

        # 在每个非空单元格中显示WER值
        for i in range(len(avg_values)):
            for j in range(len(epochs)):
                if not np.isnan(wer_matrix[i, j]):
                    text = ax.text(j, i, f'{wer_matrix[i, j]:.2f}', ha='center', va='center', color='black')

        # 标红最小的WER值
        min_wer = np.nanmin(wer_matrix)
        min_indices = np.where(wer_matrix == min_wer)
        for i, j in zip(min_indices[0], min_indices[1]):
            text = ax.text(j, i, f'{wer_matrix[i, j]:.2f}', ha='center', va='center', color='red')

        ax.set_xticks(np.arange(len(epochs)))
        ax.set_yticks(np.arange(len(avg_values)))
        ax.set_xticklabels(epochs)
        ax.set_yticklabels(avg_values)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Avg')
        ax.set_title(f'WER Summary - {test_set}')
        fig.tight_layout()
        plt.colorbar(im)
        png_name = f"wer_summary_{test_set}_{bj_time()}.png"
        plt.savefig(png_name)
        png_arr.append(png_name)
        plt.close()
    return png_arr


def health_check(wer_path, dingding_token, host_ip, dataset_name, testset_name):
    # 获取当前目录下所有wer-summary开头的文件
    file_list = [os.path.join(wer_path, file) for file in os.listdir(wer_path) if file.startswith('wer-summary')]
    current_len = len(file_list)
    wer_flag_file = os.path.join(wer_path, 'wer_flag.txt')

    # 尝试读取wer_flag.txt文件
    try:
        with open(wer_flag_file, 'r') as f:
            previous_len = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # 如果文件不存在或无法解析为整数，则视为长度改变
        previous_len = -1

    # 如果长度改变，则进行文件处理
    if current_len != previous_len:
        print(f"File list length changed from {previous_len} to {current_len}")
        data = process_wer_files(file_list)
        # save_data_to_file(data, 'wer_summary.txt')
        png_arr = plot_data(data)
        for png_file in png_arr:
            png_name = f"{dataset_name}_{png_file}"
            shutil.move(png_file, f"/s3mnt/AI_VOICE_WORKSPACE/resouce/{png_name}")
            title = f"IP: {host_ip}\ntrain set: {dataset_name}\n decode set: {testset_name}"
            text = f"{png_name}"
            url = (f"https://pro-ai-voice.s3.us-west-1.amazonaws.com/"
                   f"AI_VOICE_WORKSPACE/resouce/{png_name}")
            link_dingding(dingding_token, title, text, url)
        # 更新wer_flag.txt文件的值为当前长度
        with open(wer_flag_file, 'w') as f:
            f.write(str(current_len))
    else:
        print("File list length unchanged. Skipping file processing.")


if __name__ == "__main__":
    args = get_args()
    wer_path = os.path.join(args.training_dir, args.decode_method)
    health_check(wer_path, args.dingding_token, args.hostip, args.dataset_name, args.testset_name)
