# import json
# import os
# import re
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from openai import OpenAI

# # 1. 实例化 API Client (以阿里云 DashScope/Qwen-VL 为例，兼容标准的 OpenAI 格式)
# client = OpenAI(
#     api_key="sk-ws-H.EPHHMXP.dDnm.MEUCICf_9kp4lfDgKqCgfxXnFxx4s7Z5lL0GB2ba99weCjhiAiEArEI6WUKFwAi1DnB0JZpNeMh9brJ2LBKfisgIWdZQEwA",  # 替换为你的 API Key
#     base_url="https://ws-1k52q3ryskipjsrw.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
# )

# # 2. 定制系统 Prompt：只提取【材质、风格、单品】三类标签
# SYSTEM_PROMPT = """你是一个专业的服装打标助手。
# 请观察输入的服装图片，严格仅从以下给定的标签分类库中选择最符合的标签：

# 【可选标签库】：
# - 材质：纯棉, 真丝, 亚麻, 羊毛, 羊绒, 牛仔, 雪纺, 蕾丝, 皮革, 毛呢
# - 风格：极简, 甜美, 复古, 学院, 运动, 机能, 通勤, 老钱, 工装, 街头
# - 单品：外套, 衬衫, T恤, 针织, 毛衣, 连衣裙, 半身裙, 裤装, 套装

# 【输出要求】：
# 严禁输出任何分析过程或多余文字，仅以 JSON 数组格式返回选中的标签字符串列表。
# 例如：["牛仔", "街头", "外套"]
# """


# def process_item(item):
#     """处理单条记录，仅补充【材质、风格、单品】标签"""
#     image_url = item.get("image_url")
#     if not image_url:
#         return item

#     # 获取原有的 tags (例如 ['AI'] 或 ['AI绘图', '女装'])
#     existing_tags = item.get("tags", [])

#     try:
#         response = client.chat.completions.create(
#             model="qwen-vl-max",  # 或 qwen-vl-plus / gpt-4o-mini
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "image_url", "image_url": {"url": image_url}},
#                         {
#                             "type": "text",
#                             "text": "请根据图片分析，补充材质、风格和单品标签。",
#                         },
#                     ],
#                 },
#             ],
#             temperature=0.1,
#         )

#         res_text = response.choices[0].message.content.strip()

#         # 清理 JSON 代码块标记
#         if "```" in res_text:
#             res_text = re.sub(r"```json|```", "", res_text).strip()

#         new_tags = json.loads(res_text)

#         # 合并旧标签与新补充的标签（去重并保持顺序）
#         combined_tags = list(existing_tags)
#         for tag in new_tags:
#             if tag not in combined_tags:
#                 combined_tags.append(tag)

#         item["tags"] = combined_tags

#     except Exception as e:
#         print(f"❌ 处理失败 ID {item.get('id')}: {e}")

#     return item


# def batch_process(input_file, output_file, max_workers=5):
#     """并发批量处理，支持断点续传"""
#     # 1. 检查已处理的 ID，防止重复处理
#     processed_ids = set()
#     if os.path.exists(output_file):
#         with open(output_file, "r", encoding="utf-8") as f:
#             for line in f:
#                 if line.strip():
#                     data = json.loads(line)
#                     processed_ids.add(data.get("id"))
#         print(f"🔍 检查到已完成 {len(processed_ids)} 条记录，将自动跳过。")

#     # 2. 读取未处理的数据
#     to_process = []
#     with open(input_file, "r", encoding="utf-8") as f:
#         for line in f:
#             if line.strip():
#                 data = json.loads(line)
#                 if data.get("id") not in processed_ids:
#                     to_process.append(data)

#     total_tasks = len(to_process)
#     if total_tasks == 0:
#         print("🎉 所有数据已处理完毕！")
#         return

#     print(f"🚀 开始批量补充打标，待处理: {total_tasks} 条记录...")

#     # 3. 多线程并发请求并实时写入文件
#     completed_count = 0
#     with open(output_file, "a", encoding="utf-8") as out_f:
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             futures = {
#                 executor.submit(process_item, item): item for item in to_process
#             }

#             for future in as_completed(futures):
#                 res = future.result()
#                 # 实时追加写入，避免意外中断丢失数据
#                 out_f.write(json.dumps(res, ensure_ascii=False) + "\n")
#                 out_f.flush()

#                 completed_count += 1
#                 print(
#                     f"✅ 已完成: {completed_count}/{total_tasks} (ID: {res.get('id')}) | 当前标签: {res.get('tags')}"
#                 )

#     print(f"\n✨ 全部处理完成！结果已更新至 {output_file}")


# if __name__ == "__main__":
#     # 请确保 input.jsonl 路径正确
#     batch_process("prisma/seed/outfits/clothing.jsonl", "output.jsonl", max_workers=10)

import base64
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import unquote, urlparse
from openai import OpenAI

# 1. 配置你的 API Key
client = OpenAI(
    api_key="sk-ws-H.EPHHMXP.dDnm.MEUCICf_9kp4lfDgKqCgfxXnFxx4s7Z5lL0GB2ba99weCjhiAiEArEI6WUKFwAi1DnB0JZpNeMh9brJ2LBKfisgIWdZQEwA",  # 替换为你的 API Key
    base_url="https://ws-1k52q3ryskipjsrw.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
)

# 2. 本地图片根目录（替换为你电脑上对应的 GitHub 仓库图片文件夹绝对路径）
LOCAL_IMAGE_DIR = (
    "/Users/yanyinhong/Development/GitHub/rebeccaYan/resource-pictures/clothing"
)

SYSTEM_PROMPT = """你是一个专业的服装打标助手。
请观察输入的服装图片，严格仅从以下给定的标签分类库中选择最符合的标签：

【可选标签库】：
- 材质：纯棉, 真丝, 亚麻, 羊毛, 羊绒, 牛仔, 雪纺, 蕾丝, 皮革, 毛呢
- 风格：极简, 甜美, 复古, 学院, 运动, 机能, 通勤, 老钱, 工装, 街头
- 单品：外套, 衬衫, T恤, 针织, 毛衣, 连衣裙, 半身裙, 裤装, 套装

【输出要求】：
严禁输出任何分析过程或多余文字，仅以 JSON 数组格式返回选中的标签字符串列表。
例如：["牛仔", "街头", "外套"]
"""


def get_local_b64_image(image_url):
    """根据 URL 中的文件名，拼接本地绝对路径并转为 Base64"""
    # 提取 URL 中的文件名（例如 AI_001.png）
    filename = os.path.basename(urlparse(image_url).path)
    filename = unquote(filename)  # 处理 URL 编码字符

    local_path = os.path.join(LOCAL_IMAGE_DIR, filename)

    if not os.path.exists(local_path):
        raise FileNotFoundError(f"本地未找到图片: {local_path}")

    ext = os.path.splitext(filename)[1].lower()
    mime_type = "image/png"
    if ext in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    elif ext == ".webp":
        mime_type = "image/webp"

    with open(local_path, "rb") as f:
        b64_str = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{b64_str}"


def process_item(item):
    """处理单条记录"""
    image_url = item.get("image_url")
    if not image_url:
        return item, False

    existing_tags = item.get("tags", [])

    try:
        # 读取本地图片转 Base64
        b64_url = get_local_b64_image(image_url)

        response = client.chat.completions.create(
            model="qwen-vl-max",  # 或 qwen-vl-plus
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": b64_url},
                        },
                        {
                            "type": "text",
                            "text": "请根据图片分析，补充材质、风格和单品标签。",
                        },
                    ],
                },
            ],
            temperature=0.1,
        )

        res_text = response.choices[0].message.content.strip()
        if "```" in res_text:
            res_text = re.sub(r"```json|```", "", res_text).strip()

        new_tags = json.loads(res_text)

        # 合并去重
        combined_tags = list(existing_tags)
        for tag in new_tags:
            if tag not in combined_tags:
                combined_tags.append(tag)

        item["tags"] = combined_tags
        return item, True

    except Exception as e:
        print(f"❌ 处理失败 ID {item.get('id')}: {e}")
        return item, False


def batch_process(input_file, output_file, max_workers=10):
    """并发批量处理，支持断点续传"""
    processed_ids = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    processed_ids.add(data.get("id"))

    to_process = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                if data.get("id") not in processed_ids:
                    to_process.append(data)

    total_tasks = len(to_process)
    if total_tasks == 0:
        print("🎉 所有数据已处理完毕！")
        return

    print(
        f"🚀 开始批量打标（读取本地图片模式），待处理: {total_tasks} 条..."
    )

    completed_count = 0
    with open(output_file, "a", encoding="utf-8") as out_f:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_item, item): item for item in to_process
            }

            for future in as_completed(futures):
                res, success = future.result()
                if success:
                    out_f.write(json.dumps(res, ensure_ascii=False) + "\n")
                    out_f.flush()

                completed_count += 1
                status_icon = "✅" if success else "⚠️"
                print(
                    f"{status_icon} 进度: {completed_count}/{total_tasks} (ID: {res.get('id')}) | 最新标签: {res.get('tags')}"
                )


if __name__ == "__main__":
    batch_process("prisma/seed/outfits/clothing.jsonl", "prisma/seed/outfits/output.jsonl", max_workers=10)