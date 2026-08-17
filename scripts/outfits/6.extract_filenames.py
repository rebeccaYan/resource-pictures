# python3 scripts/clothing/6.extract_filenames.py
from pathlib import Path
import re

# 输入文件
input_file = Path("./filenames.txt")

# 输出文件
output_file = Path("./prefixes.txt")

# 用于保存去重后的前缀
prefixes = set()

# 匹配末尾的序列：
# _001
# _001_2
# _123
# _123_456
pattern = re.compile(r"^(.*?)(?:_\d+)+$")

with input_file.open("r", encoding="utf-8") as f:
    for line in f:
        filename = line.strip()

        if not filename:
            continue

        # 去掉扩展名
        name = Path(filename).stem

        # 去掉末尾的 _数字 部分
        match = pattern.match(name)

        if match:
            prefix = match.group(1)
        else:
            prefix = name

        prefixes.add(prefix)

# 排序后写入
prefixes = sorted(prefixes)

output_file.write_text(
    "\n".join(prefixes),
    encoding="utf-8"
)

print(f"原始文件名数量：{sum(1 for _ in input_file.open('r', encoding='utf-8'))}")
print(f"去重后的前缀数量：{len(prefixes)}")
print(f"结果已保存到：{output_file}")