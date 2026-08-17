# python3 scripts/clothing/7.generate_jsonl.py
import json
import uuid
from pathlib import Path
from urllib.parse import quote


# =========================
# 配置
# =========================

# 图片所在目录
IMAGE_DIR = Path("./clothing")

# 输出的 JSONL 文件
OUTPUT_FILE = Path("./clothing.jsonl")

# GitHub CDN 基础地址
CDN_BASE = (
    "https://cdn.statically.io/gh/"
    "rebeccaYan/resource-pictures/main/clothing/"
)

# 支持的图片格式
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
}


# =========================
# 从文件名提取 tag
# =========================

def extract_tag(filename: str) -> str:
    """
    取文件名中第一个 "_" 前面的内容。

    例如：
        Chanel_1991_SS.jpg
        -> Chanel

        ArmaniPrive_2024_SS_Couture.jpg
        -> ArmaniPrive

        OldMoney.jpg
        -> OldMoney
    """

    # 去掉扩展名
    stem = Path(filename).stem

    # 取第一个 "_" 前面的内容
    tag = stem.split("_", 1)[0]

    return tag


# =========================
# 生成 JSONL
# =========================

def generate_jsonl():
    image_files = sorted(
        file
        for file in IMAGE_DIR.rglob("*")
        if file.is_file()
        and file.suffix.lower() in IMAGE_EXTENSIONS
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for image_file in image_files:

            # 获取相对于 IMAGE_DIR 的路径
            relative_path = image_file.relative_to(IMAGE_DIR)

            # URL encode 文件名中的空格等特殊字符
            encoded_path = quote(
                relative_path.as_posix(),
                safe="/"
            )

            # 生成 CDN URL
            image_url = CDN_BASE + encoded_path

            # 提取 tag
            tag = extract_tag(image_file.name)

            # 构造 JSON 数据
            item = {
                "id": str(uuid.uuid4()),
                "image_url": image_url,
                "tags": [tag],
                "title": "",
            }

            # 写入一行 JSONL
            f.write(
                json.dumps(
                    item,
                    ensure_ascii=False
                ) + "\n"
            )

    print(f"完成，共生成 {len(image_files)} 条记录")
    print(f"输出文件：{OUTPUT_FILE}")


if __name__ == "__main__":
    generate_jsonl()