import os
import sys
import re
import pandas as pd

# 接收外部传入的变量
if len(sys.argv) > 1:
    dataset = sys.argv[1]
else:
    print("请提供数据集名称。")
    sys.exit()

# 定义路径
path = f"/workspace/icefall/egs/{dataset}/ASR/zipformer/exp/greedy_search"

# 查找wer文件
if os.path.exists(path):
    wer_files = [f for f in os.listdir(path) if re.search(r"wer-summary-\S+-greedy_search-\S+.txt", f)]
else:
    print(f"路径 {path} 不存在。")
    sys.exit()

# 初始化数据框
data = {"数据集": [], "测试子集": [], "WER": []}

# 遍历wer文件
for file in wer_files:
    with open(os.path.join(path, file), "r") as f:
        lines = f.readlines()
    # 提取信息
    testset = re.search(r"wer-summary-(\S+)-greedy_search", file).group(1)
    wer = re.search(r"greedy_search\s+(\S+)", lines[1]).group(1)
    # 添加到数据框
    data["数据集"].append(dataset)
    data["测试子集"].append(testset)
    data["WER"].append(float(wer))

# 创建数据框
df = pd.DataFrame(data)

# 保存到CSV文件
csv_file = f"wer_summary.csv"
if os.path.exists(csv_file):
    # 如果文件存在,则追加新数据
    existing_df = pd.read_csv(csv_file)
    new_df = pd.concat([existing_df, df], ignore_index=True)
    new_df.to_csv(csv_file, index=False, encoding='utf-8')
else:
    # 如果文件不存在,则创建新文件
    df.to_csv(csv_file, index=False, encoding='utf-8')


