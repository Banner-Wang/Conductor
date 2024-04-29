import os
import re
import argparse
import shutil
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

from conductor.utils import get_logger

log = get_logger(os.path.basename(__file__))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("testset_training_dir", type=str, help="testset epoch path to decode.")
    parser.add_argument("decode_method", type=str, help="decode method.")
    parser.add_argument("training_dir_name", type=str, help="training directory name.")
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


def plot_data(wer_path, data):
    """
    绘制关于不同测试集和平均值的WER（Word Error Rate）数据图表，并将图表保存为PNG文件。

    参数:
    wer_path: 字符串，指定保存图表文件的目录路径。
    data: 列表，包含WER数据，每个元素是四元组，分别表示测试集名称、所处的周期、平均值和WER值。

    返回值:
    png_arr: 列表，包含生成的图表文件名称（不带路径）。
    """
    # 提取唯一的测试集名称
    test_sets = list(set(item[0] for item in data))
    png_arr = []
    for test_set in test_sets:
        # 提取每个测试集中唯一的周期数和平均值，并进行排序
        epochs = sorted(set(item[1] for item in data if item[0] == test_set))
        avg_values = sorted(set(item[2] for item in data if item[0] == test_set), reverse=True)

        # 初始化WER矩阵，并将所有值设为NaN
        wer_matrix = np.zeros((len(avg_values), len(epochs)))
        wer_matrix[:] = np.nan

        # 填充WER矩阵
        for item in data:
            if item[0] == test_set:
                epoch_idx = epochs.index(item[1])
                avg_idx = avg_values.index(item[2])
                wer_matrix[avg_idx, epoch_idx] = item[3]

        # 绘制热力图
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(wer_matrix, cmap='YlGn_r')

        # 在图中显示每个WER值
        for i in range(len(avg_values)):
            for j in range(len(epochs)):
                if not np.isnan(wer_matrix[i, j]):
                    text = ax.text(j, i, f'{wer_matrix[i, j]:.2f}', ha='center', va='center', color='black')

        # 标记最小的WER值为红色
        min_wer = np.nanmin(wer_matrix)
        min_indices = np.where(wer_matrix == min_wer)
        for i, j in zip(min_indices[0], min_indices[1]):
            text = ax.text(j, i, f'{wer_matrix[i, j]:.2f}', ha='center', va='center', color='red')

        # 设置图表的刻度和标签
        ax.set_xticks(np.arange(len(epochs)))
        ax.set_yticks(np.arange(len(avg_values)))
        ax.set_xticklabels(epochs)
        ax.set_yticklabels(avg_values)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Avg')
        ax.set_title(f'WER Summary - {test_set}')
        fig.tight_layout()
        plt.colorbar(im)

        # 保存图表并收集文件名
        png_name = f"wer_summary_{test_set}.png"
        png_file_path = os.path.join(wer_path, png_name)
        plt.savefig(png_file_path)
        png_arr.append(png_name)
        plt.close()
    return png_arr


def main(wer_path, s3_testset_training_dir):
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
        log.info(f"File list length changed from {previous_len} to {current_len}")
        data = process_wer_files(file_list)
        png_arr = plot_data(wer_path, data)
        for png_file in png_arr:
            png_file_path = os.path.join(wer_path, png_file)
            shutil.copy(png_file_path, os.path.join(s3_testset_training_dir, png_file))
        # 更新wer_flag.txt文件的值为当前长度
        with open(wer_flag_file, 'w') as f:
            f.write(str(current_len))
    else:
        log.info("File list length unchanged. Skipping file processing.")


if __name__ == "__main__":
    args = get_args()
    wer_path = os.path.join(args.testset_training_dir, args.decode_method)
    s3_wer_dir = "/s3mnt/AI_VOICE_WORKSPACE/resouce"
    s3_testset_training_dir = os.path.join(s3_wer_dir, args.training_dir_name, args.testset_name)
    if not os.path.exists(s3_testset_training_dir):
        os.makedirs(s3_testset_training_dir)

    main(wer_path, s3_testset_training_dir)
