import argparse
import re
import os
from bs4 import BeautifulSoup

from conductor.utils import link_dingding


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dingding_token", type=str, help="Dingding robot token.")
    parser.add_argument("hostip", type=str, help="host IP address.")
    parser.add_argument("env_info", type=str, help="测试报告的环境信息 <docker/.env>.")
    parser.add_argument("loss_link", type=str, help="loss曲线图URL.")
    parser.add_argument("training_dir_name", type=str, help="存放模型文件的目录名.")
    return parser.parse_args()


def find_png(path):
    result = []
    s3_src_path = path.replace("/s3mnt/", "")
    for root, dirs, files in os.walk(path):
        png_files = [file for file in files if file.lower().endswith('.png')]

        if png_files:
            test_set = os.path.basename(root)
            s3_path = os.path.join(s3_src_path, test_set)
            wer_png_urls = []
            for png_file in png_files:
                wer_png_url = f"https://pro-ai-voice.s3.us-west-1.amazonaws.com/{s3_path}/{png_file}"
                wer_png_urls.append(wer_png_url)
            result.append({
                "test_set": test_set,
                "img_src_list": wer_png_urls
            })

    return result


def parse_env(env_info):
    env_lines = env_info.strip().splitlines()

    # 给定的顺序
    order = [
        "HOST_IP", "DECODE_START_EPOCH", "DECODE_END_EPOCH",
        "DATASET_NAME", "ICEFALL_PATH", "TRAINING_DIR",
        "TRAIN_CMD", "DECODE_CMD"
    ]

    # 将每行映射到其键（即每行的开头部分）
    line_mapping = {line.split('=')[0]: line for line in env_lines}

    # 构造一个新列表，其中只包含给定顺序中存在的键
    sorted_info = [line_mapping[key] for key in order if key in line_mapping]
    # 将已排序的信息转换回字符串
    sorted_info_str = '\n'.join(sorted_info)
    env_info = re.sub(r'(?<!\S)--', r'\n--', sorted_info_str)
    env_info = re.sub(r'(\s)(\d+)', r' \2', env_info)
    return env_info


# 从文件读取HTML内容
def read_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# 将修改后的HTML内容写入新文件
def write_html_file(output_path, html_content):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)


# 外部替换的函数
def replace_info(soup, environment_info=None, link=None):
    # 替换环境信息文字
    if environment_info:
        env_info_pre = soup.find('pre', class_='environment-info')
        env_info_pre.string = environment_info

    # 替换超链接
    if link:
        a_tag = soup.find('a', target="_blank")
        a_tag['href'] = link


def add_image_group(soup, image_group_map):
    image_module = soup.find('div', id='image-module')
    new_image_group = soup.new_tag('div', **{'class': 'image-group'})

    # Combine all image sources into a single list
    all_img_src = []
    for image_group in image_group_map:
        all_img_src.extend(image_group["img_src_list"])

    images_row = soup.new_tag('div', **{'class': 'images-row'})
    for img_src in all_img_src:
        image_container = soup.new_tag('div', **{'class': 'image-container'})
        img_tag = soup.new_tag('img', src=img_src)
        image_container.append(img_tag)
        images_row.append(image_container)

    new_image_group.append(images_row)
    image_module.append(new_image_group)


def main(dingding_token, host_ip, env_info, loss_link, images_src):
    image_group_map = find_png(images_src)
    print(image_group_map)
    # 读取模板文件
    template_path = 'conductor/visualize/template.html'  # 您的模板HTML文件路径
    html_content = read_html_file(template_path)
    soup = BeautifulSoup(html_content, 'html.parser')

    env_info = parse_env(env_info)
    replace_info(soup, environment_info=env_info, link=loss_link)

    add_image_group(soup, image_group_map)

    # 指定新文件的路径
    output_path = os.path.join(images_src, 'output.html')  # 您的输出HTML文件路径
    write_html_file(output_path, soup.prettify())
    s3_output_path = output_path.replace("/s3mnt/", "")

    title = "ASR测试报告"
    text = f"训练机器：{host_ip}"
    url = f"https://pro-ai-voice.s3.us-west-1.amazonaws.com/{s3_output_path}"
    link_dingding(dingding_token, title, text, url)


if __name__ == '__main__':
    args = get_args()
    s3_wer_dir = "/s3mnt/AI_VOICE_WORKSPACE/resouce"
    s3_images_src = os.path.join(s3_wer_dir, args.training_dir_name)
    main(args.dingding_token, args.hostip, args.env_info, args.loss_link, s3_images_src)
