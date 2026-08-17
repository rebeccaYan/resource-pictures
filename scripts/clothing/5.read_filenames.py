# python3 scripts/clothing/5.read_filenames.py
from pathlib import Path

# 要读取的图片目录
image_dir = Path("./clothing")

# 输出文件
output_file = Path("./filenames.txt")

# 支持的图片格式
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff"}

# 获取图片文件名
filenames = [
    file.name
    for file in image_dir.iterdir()
    if file.is_file() and file.suffix.lower() in image_extensions
]

# 排序，保证输出顺序稳定
filenames.sort()

# 写入 txt，一行一个文件名
output_file.write_text(
    "\n".join(filenames),
    encoding="utf-8"
)

print(f"共找到 {len(filenames)} 张图片")
print(f"文件名已保存到：{output_file}")