import json
import os
import re


def extract_prefix_from_url(image_url: str) -> str:
    """从 image_url 中提取文件名，并仅删除结尾为以下两种格式的序号：

    1. _三位数字 (如 _003)
    2. _三位数字_两位数字 (如 _002_01)

    保留四位数的年份（如 _2020, _1988）。
    """
    filename = os.path.basename(image_url)
    name_without_ext = os.path.splitext(filename)[0]

    # 正则解析：
    # (?:_\d{3}_\d{2}|_\d{3})$
    #  - _\d{3}_\d{2} : 匹配 _XXX_XX (3位数字+2位数字)
    #  - |             : 或
    #  - _\d{3}        : 匹配 _XXX (3位数字)
    #  - $             : 必须在字符串末尾
    pattern = r'(?:_\d{3}_\d{2}|_\d{3})$'

    prefix = re.sub(pattern, '', name_without_ext)
    return prefix


def transform_title(raw_prefix: str) -> str:
    """处理提取出的前缀字符串，生成格式化后的 title：

    1. 将驼峰命名在非首位大写字母前加空格（例如 ArmaniPrive -> Armani Prive）
    2. 将下划线 '_' 替换为空格
    """
    # 驼峰分词：小写字母/数字与大写字母之间插入空格
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', raw_prefix)
    # 处理连续大写加小写的情况（如 ChanelCouture -> Chanel Couture）
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', s)

    # 将下划线替换为空格
    s = s.replace('_', ' ')

    # 清理多余连续空格
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def process_jsonl(input_file: str, output_file: str):
    with (
        open(input_file, 'r', encoding='utf-8') as fin,
        open(output_file, 'w', encoding='utf-8') as fout,
    ):
        for line in fin:
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)
            image_url = data.get('image_url', '')

            if image_url:
                prefix = extract_prefix_from_url(image_url)
                title = transform_title(prefix)
                data['title'] = title

            fout.write(json.dumps(data, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    input_jsonl = 'scripts/clothing/clothing.jsonl'
    output_jsonl = 'scripts/clothing/clothing_with_title.jsonl'

    process_jsonl(input_jsonl, output_jsonl)
    print(f'处理完成！结果已写入 {output_jsonl}')