# python3 scripts/clothing/4.rename_round2.py "./clothing" --execute

# 第二轮 Regex 规则
# 保留原始 _1 / _10 / _11 序号
# 自动转换成 _001 / _010 / _011
# 目标文件已存在时自动追加 _2、_3……
# 同一批次内部也避免目标名称冲突
# 默认 DRY RUN，不修改文件
# --execute 才真正执行
# 图片 29.png 这种没有末尾数字的文件不会自动处理
# 不覆盖任何已有文件
from __future__ import annotations

import re
import argparse
from pathlib import Path


# ============================================================
# 图片扩展名
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
}


# ============================================================
# 第二轮 Regex → Canonical Prefix
#
# 格式：
#
# (
#     r"原始名称 Regex",
#     "新的标准 Prefix",
# )
#
# 注意：
# Regex 匹配的是去掉最后 _数字 后的部分。
#
# 例如：
#
# 1991年的Chanel秀场_1.png
#
# 实际匹配：
#
# 1991年的Chanel秀场
# ============================================================

RENAME_RULES = [

    # --------------------------------------------------------
    # YSL
    # --------------------------------------------------------

    (
        r"^1986\s*圣罗兰经典秀场$",
        "YSL_1986_Runway",
    ),

    # --------------------------------------------------------
    # Chanel
    # --------------------------------------------------------

    (
        r"^1991年?的?Chanel秀场$",
        "Chanel_1991_Runway",
    ),

    (
        r"^94年的香奶奶$",
        "Chanel_1994",
    ),

    # --------------------------------------------------------
    # Zuhair Murad
    # --------------------------------------------------------

    (
        r"^2009年Zuhair\s*Murad$",
        "ZuhairMurad_2009",
    ),

    # --------------------------------------------------------
    # Topic
    # --------------------------------------------------------

    (
        r"^BILLIOOON\s+CHIC\s*$",
        "BillionChic",
    ),
]


# ============================================================
# 编译 Regex
# ============================================================

COMPILED_RULES = [
    (
        re.compile(
            pattern,
            re.IGNORECASE,
        ),
        replacement,
    )
    for pattern, replacement in RENAME_RULES
]


# ============================================================
# 判断是否为图片
# ============================================================

def is_image(path: Path) -> bool:

    return (
        path.is_file()
        and path.suffix.lower()
        in IMAGE_EXTENSIONS
    )


# ============================================================
# 扫描图片
# ============================================================

def scan(folder: Path):

    return sorted(
        [
            p
            for p in folder.iterdir()
            if is_image(p)
        ],
        key=lambda p: p.name.lower(),
    )


# ============================================================
# 提取末尾序号
#
# 例如：
#
# Chanel_1
# Chanel_10
# Chanel_001
#
# → 1 / 10 / 1
# ============================================================

def extract_sequence(stem: str):

    match = re.search(
        r"_(\d+)$",
        stem,
    )

    if not match:
        return None

    return int(
        match.group(1)
    )


# ============================================================
# 提取 Prefix
#
# 例如：
#
# 1991年的Chanel秀场_10
#
# →
#
# 1991年的Chanel秀场
# ============================================================

def extract_prefix(stem: str):

    match = re.search(
        r"_(\d+)$",
        stem,
    )

    if not match:
        return None

    return stem[
        :match.start()
    ].rstrip()


# ============================================================
# 根据 Regex 找到标准 Prefix
# ============================================================

def match_prefix(prefix: str):

    for regex, replacement in COMPILED_RULES:

        if regex.fullmatch(prefix):

            return replacement

    return None


# ============================================================
# 生成基础新文件名
#
# 例如：
#
# 1991年的Chanel秀场_10.png
#
# →
#
# Chanel_1991_Runway_010.png
# ============================================================

def make_new_name(path: Path):

    stem = path.stem

    prefix = extract_prefix(stem)

    sequence = extract_sequence(stem)

    # 没有 _数字
    if prefix is None or sequence is None:
        return None

    new_prefix = match_prefix(prefix)

    # 没有匹配任何 Regex
    if new_prefix is None:
        return None

    new_stem = (
        f"{new_prefix}_"
        f"{sequence:03d}"
    )

    return path.with_name(
        new_stem + path.suffix
    )


# ============================================================
# 查找可用文件名
#
# 正常：
#
# Chanel_1994_001.png
#
# 如果已经存在：
#
# Chanel_1994_001_2.png
#
# 如果还存在：
#
# Chanel_1994_001_3.png
#
# ...
# ============================================================

def find_available_name(
    path: Path,
    reserved: set[Path],
) -> Path:

    # --------------------------------------------------------
    # 目标不存在，并且没有被本轮其他文件占用
    # --------------------------------------------------------

    if (
        not path.exists()
        and path not in reserved
    ):

        return path

    # --------------------------------------------------------
    # 发生冲突
    # --------------------------------------------------------

    counter = 2

    while True:

        candidate = path.with_name(
            f"{path.stem}_{counter}"
            f"{path.suffix}"
        )

        if (
            not candidate.exists()
            and candidate not in reserved
        ):

            return candidate

        counter += 1


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Second-round image renaming tool"
        )
    )

    parser.add_argument(
        "folder",
        type=Path,
        help="图片目录",
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="真正执行重命名；默认只是预览",
    )

    args = parser.parse_args()

    folder = args.folder.resolve()

    # --------------------------------------------------------
    # 检查目录
    # --------------------------------------------------------

    if not folder.exists():

        raise SystemExit(
            f"目录不存在：{folder}"
        )

    if not folder.is_dir():

        raise SystemExit(
            f"不是目录：{folder}"
        )

    # --------------------------------------------------------
    # 扫描
    # --------------------------------------------------------

    files = scan(folder)

    rename_pairs = []

    manual_review = []

    reserved = set()

    # ========================================================
    # 分析每一个文件
    # ========================================================

    for path in files:

        new_path = make_new_name(path)

        # ----------------------------------------------------
        # 无法自动处理
        # ----------------------------------------------------

        if new_path is None:

            # 有末尾数字，但是没有匹配规则
            # → 进入人工确认列表
            if extract_sequence(path.stem) is not None:

                manual_review.append(path)

            continue

        # ----------------------------------------------------
        # 如果新旧名称完全相同
        # ----------------------------------------------------

        if new_path == path:

            continue

        # ----------------------------------------------------
        # 找一个真正可用的目标名称
        # ----------------------------------------------------

        new_path = find_available_name(
            new_path,
            reserved,
        )

        reserved.add(
            new_path
        )

        rename_pairs.append(
            (path, new_path)
        )

    # ========================================================
    # DRY RUN 输出
    # ========================================================

    print()
    print("=" * 90)
    print("SECOND ROUND RENAME")
    print("=" * 90)

    print(
        f"图片总数：       {len(files)}"
    )

    print(
        f"准备重命名：     {len(rename_pairs)}"
    )

    print(
        f"人工确认：       {len(manual_review)}"
    )

    print()

    # --------------------------------------------------------
    # 重命名列表
    # --------------------------------------------------------

    if rename_pairs:

        print("=" * 90)
        print("RENAME PREVIEW")
        print("=" * 90)

        for old, new in rename_pairs:

            print()
            print(
                f"{old.name}"
            )

            print(
                f"    -> {new.name}"
            )

    else:

        print(
            "没有发现可以自动重命名的文件。"
        )

    # ========================================================
    # 人工确认
    # ========================================================

    if manual_review:

        print()
        print("=" * 90)
        print("MANUAL REVIEW")
        print("=" * 90)

        print(
            "以下文件有序号，但没有匹配当前 Regex："
        )

        for path in manual_review:

            print(
                f"    {path.name}"
            )

    # ========================================================
    # DRY RUN
    # ========================================================

    if not args.execute:

        print()
        print("=" * 90)
        print("DRY RUN")
        print("=" * 90)

        print(
            "当前没有修改任何文件。"
        )

        print()

        print(
            "确认上面的结果无误后执行："
        )

        print()

        print(
            f'python "{Path(__file__).name}" '
            f'"{folder}" --execute'
        )

        print()

        return

    # ========================================================
    # 正式执行
    # ========================================================

    print()
    print("=" * 90)
    print("EXECUTE")
    print("=" * 90)

    success_count = 0

    for old, new in rename_pairs:

        # ----------------------------------------------------
        # 最后一次安全检查
        #
        # 防止 DRY RUN 后到真正执行之间，
        # 有其他文件占用了目标名称。
        # ----------------------------------------------------

        if new.exists():

            # 再寻找一个新的可用名称
            new = find_available_name(
                new,
                set(),
            )

        old.rename(new)

        print(
            f"OK  {old.name}"
            f" -> "
            f"{new.name}"
        )

        success_count += 1

    # ========================================================
    # 完成
    # ========================================================

    print()
    print("=" * 90)
    print("DONE")
    print("=" * 90)

    print(
        f"成功重命名：{success_count} 个文件"
    )

    if manual_review:

        print(
            f"待人工确认：{len(manual_review)} 个文件"
        )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()