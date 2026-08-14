

from pathlib import Path
import re

# ============================================================
# 配置
# ============================================================

IMAGE_DIR = Path("./clothing")

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".avif",
}


# ============================================================
# 从文件名中提取「名称主体」
# ============================================================

def extract_base_name(filename):
    """
    从文件名中提取主体名称。

    示例：

    80年代穿搭_1.png
        -> 80年代穿搭

    80年代穿搭_12.png
        -> 80年代穿搭

    80年代穿搭 (1).png
        -> 80年代穿搭

    Luisa Beccaria 2005_2.jpg
        -> Luisa Beccaria 2005

    注意：
    只处理「末尾的编号」，
    不修改名称主体中的任何内容。
    """

    stem = Path(filename).stem

    # 去掉末尾的 "(1)"、"(2)" 等
    stem = re.sub(r"\s*\(\d+\)\s*$", "", stem)

    # 去掉末尾的 "_1"、"_2"、"_123"
    stem = re.sub(r"_\d+\s*$", "", stem)

    # 去掉末尾的 "-1"、"-2"、"-123"
    stem = re.sub(r"-\d+\s*$", "", stem)

    return stem.strip()


# ============================================================
# 扫描图片
# ============================================================

images = [
    p for p in IMAGE_DIR.iterdir()
    if p.is_file()
    and p.suffix.lower() in IMAGE_EXTENSIONS
]

# 按文件名排序
images.sort(key=lambda p: p.name.lower())


# ============================================================
# 提取唯一名称
# ============================================================

names = []
seen = set()

for image in images:

    base_name = extract_base_name(image.name)

    if base_name not in seen:
        seen.add(base_name)
        names.append(base_name)


# ============================================================
# 输出
# ============================================================

print()
print("=" * 70)
print("发现的名称主体")
print("=" * 70)
print()

for i, name in enumerate(names, start=1):
    print(f"{i:03d}. {name}")

print()
print("=" * 70)
print(f"图片数量：{len(images)}")
print(f"名称数量：{len(names)}")
print("=" * 70)