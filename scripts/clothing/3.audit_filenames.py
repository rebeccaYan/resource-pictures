# python3 scripts/clothing/3.audit_filenames.py "./clothing" --csv filename_audit.csv
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


# ============================================================
# 配置
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
# Regex
# ============================================================

YEAR_RE = re.compile(
    r"(19\d{2}|20\d{2})"
)

STANDARD_NAME_RE = re.compile(
    r"^.+_\d{3}$"
)

SEQUENCE_RE = re.compile(
    r"_(\d{1,4})$"
)

OLD_SEQUENCE_RE = re.compile(
    r"_\d+_new$",
    re.IGNORECASE,
)


# ============================================================
# 扫描图片
# ============================================================

def scan(folder: Path):

    files = [
        p
        for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    return sorted(
        files,
        key=lambda p: p.name.lower()
    )


# ============================================================
# 提取年份
# ============================================================

def extract_year(text: str):

    match = YEAR_RE.search(text)

    if match:
        return match.group(1)

    return ""


# ============================================================
# 判断文件是否已经规范
# ============================================================

def analyze(path: Path):

    stem = path.stem

    # --------------------------------------------------------
    # 1. 已经是：
    #
    # Brand_001
    # Brand_1988_SS_001
    # Chanel_1997_SS_Couture_001
    #
    # 认为暂时 OK
    # --------------------------------------------------------

    if STANDARD_NAME_RE.match(stem):

        return None


    # --------------------------------------------------------
    # 2. _1 / _10 / _100
    #
    # 例如：
    # Diana_1
    # Diana_10
    #
    # 需要统一成 _001 / _010
    # --------------------------------------------------------

    match = SEQUENCE_RE.search(stem)

    if match:

        sequence = match.group(1)

        # _001 已经被上面的 STANDARD_NAME_RE 拦截
        if len(sequence) != 3:

            prefix = stem[
                :match.start()
            ].rstrip("_")

            return {
                "original": path.name,
                "status": "SEQUENCE_FORMAT",
                "prefix": prefix,
                "year": extract_year(prefix),
                "suggested": "",
            }


    # --------------------------------------------------------
    # 3. 旧格式 _10_new
    # --------------------------------------------------------

    if OLD_SEQUENCE_RE.search(stem):

        prefix = OLD_SEQUENCE_RE.sub(
            "",
            stem
        ).rstrip("_")

        return {
            "original": path.name,
            "status": "OLD_SEQUENCE",
            "prefix": prefix,
            "year": extract_year(prefix),
            "suggested": "",
        }


    # --------------------------------------------------------
    # 4. 其他没有标准编号的文件
    # --------------------------------------------------------

    return {
        "original": path.name,
        "status": "NO_SEQUENCE",
        "prefix": stem,
        "year": extract_year(stem),
        "suggested": "",
    }


# ============================================================
# 建立 Audit
# ============================================================

def build_audit(folder: Path):

    rows = []

    for path in scan(folder):

        result = analyze(path)

        # None = 已经规范，不进入 CSV
        if result is None:
            continue

        rows.append(result)

    return rows


# ============================================================
# 输出 CSV
# ============================================================

def write_csv(
    rows,
    output: Path,
):

    fieldnames = [
        "original",
        "status",
        "prefix",
        "year",
        "suggested",
    ]

    with output.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(rows)


# ============================================================
# 按 Prefix 分组
# ============================================================

def print_groups(rows):

    groups = defaultdict(list)

    for row in rows:

        groups[row["prefix"]].append(
            row["original"]
        )

    print()
    print("=" * 90)
    print("需要处理的文件分组")
    print("=" * 90)

    for prefix, files in sorted(
        groups.items(),
        key=lambda item: (
            -len(item[1]),
            item[0].lower(),
        )
    ):

        print()
        print(
            f"[{len(files)}] {prefix}"
        )

        for filename in files:

            print(
                f"    {filename}"
            )


# ============================================================
# Main
# ============================================================

def main():

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Audit image filenames and "
            "export only files that need renaming."
        )
    )

    parser.add_argument(
        "folder",
        type=Path,
        help="图片目录",
    )

    parser.add_argument(
        "--csv",
        type=Path,
        default=Path(
            "filename_audit.csv"
        ),
        help="输出 CSV 文件",
    )

    args = parser.parse_args()

    folder = args.folder.resolve()

    if not folder.exists():
        raise SystemExit(
            f"目录不存在：{folder}"
        )

    if not folder.is_dir():
        raise SystemExit(
            f"不是目录：{folder}"
        )

    rows = build_audit(folder)

    # --------------------------------------------------------
    # 统计
    # --------------------------------------------------------

    total = len(scan(folder))
    need_rename = len(rows)

    print()
    print("=" * 90)
    print("FILENAME AUDIT")
    print("=" * 90)

    print(
        f"图片总数：       {total}"
    )

    print(
        f"需要进一步处理： {need_rename}"
    )

    print(
        f"已经规范：       {total - need_rename}"
    )

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    write_csv(
        rows,
        args.csv,
    )

    print()
    print(
        f"Audit CSV：{args.csv}"
    )

    # --------------------------------------------------------
    # 分组
    # --------------------------------------------------------

    print_groups(rows)


if __name__ == "__main__":
    main()