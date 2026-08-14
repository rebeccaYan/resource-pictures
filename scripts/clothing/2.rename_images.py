# python3 scripts/clothing/2.rename_images.py "./clothing" --csv rename_plan.csv
# python3 scripts/clothing/2.rename_images.py "./clothing" --apply
from __future__ import annotations

import argparse
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

# True:
#   按原始文件名自然排序后重新编号
#
# False:
#   按目录迭代顺序
#
# 推荐 True，保证每次运行结果稳定。
SORT_FILES = True


# ============================================================
# Regex 规则
# ============================================================

SPECIAL_RULES = [
    # -------------------------
    # 人物
    # -------------------------
    (r"^(?:黛安娜|戴安娜)(?:王妃)?", "Diana"),
    (r"^Diana", "Diana"),

    (r"^林青霞", "LinQingxia"),
    (r"^格蕾丝凯利", "GraceKelly"),
    (r"^Elsa\s+Hosk", "ElsaHosk"),
    (r"^Karen\s+Gillan", "KarenGillan"),
    (r"^Rachel\s+Lai", "RachelLai"),
    (r"^Stacie\s+Flinner", "StacieFlinner"),
    (r"^ZhaoYaZhi", "ZhaoYazhi"),
    (r"^zhaoyazhi", "ZhaoYazhi"),
    (r"^金泰熙", "KimTaeHee"),

    # -------------------------
    # 特殊品牌
    # -------------------------
    (r"^Red\s+Valentino", "RedValentino"),
    (r"^Christian\s+Dior", "Dior"),
    (r"^Armani\s+Priv[eé]?", "ArmaniPrive"),
    (r"^Dolce\s*&\s*Gabbana", "DolceGabbana"),
    (r"^Oscar\s+de\s+la\s+Renta", "OscarDeLaRenta"),

    # -------------------------
    # AI：所有 AI 开头的全部归 AI
    # -------------------------
    (r"^AI", "AI"),

    # -------------------------
    # 品牌 + 专题
    # -------------------------
    (r"^Chanel\s*[｜|]\s*Knitting", "Chanel_Knitting"),
    (r"^Chanel\s*[｜|]\s*Waist\s*Line", "Chanel_WaistLine"),

    # -------------------------
    # 暂时独立
    # -------------------------
    (r"^CEE\s+CUBED", "CEECubed"),
    (r"^GIANA", "Giana"),
    (r"^KEA[_\s]+JIANG", "KeaJiang"),
    (r"^chuui", "Chuui"),
    (r"^mk_cat", "MKCat"),
    (r"^羲和Eclat", "Eclat"),
]


BRAND_RULES = [
    # Saint Laurent
    (r"^圣罗兰", "YSL"),
    (r"^YSL", "YSL"),

    # Chanel
    (r"^(?:\d{4}\s*)?Chanel", "Chanel"),
    (r"^香奈儿", "Chanel"),
    (r"^香奈兒", "Chanel"),
    (r"^Channel\b", "Chanel"),

    # Valentino
    (r"^Valentino", "Valentino"),

    # Ralph Lauren
    (r"^Ralph\s*Lauren", "RalphLauren"),

    # Dior
    (r"^Dior", "Dior"),

    # Celine
    (r"^Celine", "Celine"),

    # Chloe
    (r"^Chlo[eé]", "Chloe"),

    # Zuhair Murad
    (r"^(?:\d{4}\s*)?Zuhair\s+Murad", "ZuhairMurad"),

    # Andrew Gn
    (r"^Andrew\s+Gn", "AndrewGn"),

    # Belstaff
    (r"^Belstaff", "Belstaff"),

    # Betsey Johnson
    (r"^Betsey\s+Johnson", "BetseyJohnson"),

    # Blumarine
    (r"^Blumarine", "Blumarine"),

    # Elie Saab
    (r"^Elie\s+Saab", "ElieSaab"),

    # Elisabetta Franchi
    (r"^Elisabetta\s+Franchi", "ElisabettaFranchi"),

    # Emanuel Ungaro
    (r"^Emanuel\s+Ungaro", "EmanuelUngaro"),

    # Georges Hobeika
    (r"^Georges\s+Hobeika", "GeorgesHobeika"),

    # Isabel Marant
    (r"^Isabel\s+Marant", "IsabelMarant"),

    # Lolita Lempicka
    (r"^Lolita\s+Lempicka", "LolitaLempicka"),

    # Luisa Beccaria
    (r"^Luisa\s+Beccaria", "LuisaBeccaria"),

    # MaisonWester
    (r"^Maison\s*Wester", "MaisonWester"),

    # Max Mara
    (r"^Max\s+Mara", "MaxMara"),

    # Olympia Le-Tan
    (r"^Olympia\s+Le[-–—]Tan", "OlympiaLeTan"),

    # Ralph Russo
    (r"^ralprusso", "RalphRusso"),

    # Rochas
    (r"^Rochas", "Rochas"),

    # Sretsis
    (r"^Sretsis", "Sretsis"),

    # The Atelier
    (r"^The\s+Atelier", "TheAtelier"),

    # Tory Burch
    (r"^Tory\s*Burch", "ToryBurch"),
]


MEDIA_RULES = [
    (r"^Elle\(France\)", "ElleFrance"),
    (r"^Glamour\s+US", "GlamourUS"),
    (r"^(?:US\s+)?Vogue", "VogueUS"),
    (r"^Popeye", "Popeye"),
    (r"^renmin", "Renmin"),
]


STYLE_RULES = [
    # -------------------------
    # 年代
    # -------------------------
    (r"^80年代穿搭", "Vintage80s"),
    (r"^80年代经典穿搭", "Vintage80s"),

    (r"^90年代复古女绅士穿搭", "Vintage90s"),
    (r"^90年代秀场穿搭", "Vintage90s"),

    # 明确 1990：与 Vintage90s 暂时区分
    (r"^vintage1990_blue\s+storm", "Vintage1990_BlueStorm"),
    (r"^vintage1990", "Vintage1990"),

    # -------------------------
    # 老钱风
    # -------------------------
    (r"^温网老钱风", "TennisOldMoney"),
    (r"^老钱风", "OldMoney"),

    # -------------------------
    # OOTD
    # -------------------------
    (r"^OOTD法式", "OOTD_French"),
    (r"^OOTD", "OOTD"),

    # -------------------------
    # 日常
    # -------------------------
    (r"^日常穿搭", "DailyOutfit"),

    # -------------------------
    # 其他风格
    # -------------------------
    (r"^入秋穿搭", "FallOutfit"),
    (r"^前进学院风", "Preppy"),
    (r"^极简通勤", "MinimalWorkwear"),
    (r"^格雷系高级穿搭", "GreyStyle"),
    (r"^网球风", "TennisStyle"),
    (r"^复古宫廷风", "VintageRoyal"),
    (r"^复古", "Vintage"),
    (r"^印花", "Prints"),
    (r"^毛衣", "Knitwear"),
    (r"^礼裙", "EveningDress"),
    (r"^连衣裙", "Dress"),
    (r"^西裤后腰的艺术", "TrouserDetails"),
    (r"^魔法美学", "MagicAesthetic"),

    # 泛“穿搭”必须最后
    (r"^穿搭", "Outfit"),
]


OTHER_RULES = [
    (r"^人鱼小姐", "MissMermaid"),
    (r"^穿prada的女王", "DevilWearsPrada"),
]


# ============================================================
# 编译 Regex
# ============================================================

def compile_rules(rules):
    return [
        (re.compile(pattern, re.IGNORECASE), canonical)
        for pattern, canonical in rules
    ]


COMPILED_RULES = (
    compile_rules(SPECIAL_RULES)
    + compile_rules(BRAND_RULES)
    + compile_rules(MEDIA_RULES)
    + compile_rules(STYLE_RULES)
    + compile_rules(OTHER_RULES)
)


# ============================================================
# 年份
# ============================================================

YEAR_RE = re.compile(
    r"(?<!\d)(19\d{2}|20\d{2})(?!\d)"
)


# ============================================================
# 季节
# ============================================================

SEASON_PATTERNS = [
    (
        re.compile(
            r"春夏|春季|Spring\s*/?\s*Summer|"
            r"Spring\s+Summer|\bSS\b",
            re.IGNORECASE,
        ),
        "SS",
    ),
    (
        re.compile(
            r"秋冬|秋季|Fall\s*/?\s*Winter|"
            r"Fall\s+Winter|\bFW\b",
            re.IGNORECASE,
        ),
        "FW",
    ),
    (
        re.compile(
            r"早春|早秋|Pre[-\s]?Fall|Pre[-\s]?Spring",
            re.IGNORECASE,
        ),
        "PF",
    ),
]


# ============================================================
# Couture
# ============================================================

COUTURE_RE = re.compile(
    r"高定|Haute\s+Couture|Couture",
    re.IGNORECASE,
)


# ============================================================
# 月份
# ============================================================

MONTH_PATTERNS = [
    (re.compile(r"January|Jan|1月", re.I), "01"),
    (re.compile(r"February|Feb|2月", re.I), "02"),
    (re.compile(r"March|Mar|3月", re.I), "03"),
    (re.compile(r"April|Apr|4月", re.I), "04"),
    (re.compile(r"May|5月", re.I), "05"),
    (re.compile(r"June|Jun|6月", re.I), "06"),
    (re.compile(r"July|Jul|7月", re.I), "07"),
    (re.compile(r"August|Aug|8月", re.I), "08"),
    (re.compile(r"September|Sep|Sept|9月", re.I), "09"),
    (re.compile(r"October|Oct|10月", re.I), "10"),
    (re.compile(r"November|Nov|11月", re.I), "11"),
    (re.compile(r"December|Dec|12月", re.I), "12"),
]


# ============================================================
# 工具函数
# ============================================================

def natural_key(text: str):
    """
    自然排序：
    file2 < file10
    """
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", text)
    ]


def strip_old_suffix(stem: str) -> str:
    """
    删除旧文件名中的 _数字_new / _数字 / -数字 等尾部序号。

    例如：
        Chanel_10_new -> Chanel
        Diana10       -> Diana
        Outfit_3      -> Outfit
    """

    # _10_new
    stem = re.sub(r"[_\-\s]+\d+_new$", "", stem, flags=re.I)

    # _10
    stem = re.sub(r"[_\-\s]+\d+$", "", stem)

    return stem.strip()


def find_canonical(stem: str):
    """
    根据规则寻找 CanonicalName。
    """

    for regex, canonical in COMPILED_RULES:
        if regex.search(stem):
            return canonical

    return None


def extract_year(stem: str):
    match = YEAR_RE.search(stem)

    if match:
        return match.group(1)

    return None


def extract_season(stem: str):
    for regex, season in SEASON_PATTERNS:
        if regex.search(stem):
            return season

    return None


def extract_couture(stem: str):
    if COUTURE_RE.search(stem):
        return "Couture"

    return None


def extract_month(stem: str):
    for regex, month in MONTH_PATTERNS:
        if regex.search(stem):
            return month

    return None


# ============================================================
# Canonical Stem
# ============================================================

def build_canonical_stem(original_stem: str):
    """
    将原始文件名转换成：

        Brand
        Brand_Year
        Brand_Year_Season
        Brand_Year_Season_Couture
        etc.
    """

    cleaned = strip_old_suffix(original_stem)

    canonical = find_canonical(cleaned)

    if canonical is None:
        return None, {
            "canonical": None,
            "year": None,
            "season": None,
            "type": None,
            "month": None,
        }

    year = extract_year(cleaned)
    season = extract_season(cleaned)
    couture = extract_couture(cleaned)
    month = extract_month(cleaned)

    parts = [canonical]

    if year:
        parts.append(year)

    if season:
        parts.append(season)

    if couture:
        parts.append(couture)

    # 月份目前只给出版物使用
    if canonical in {
        "VogueUS",
        "ElleFrance",
        "GlamourUS",
        "Popeye",
    } and month:
        parts.append(month)

    canonical_stem = "_".join(parts)

    return canonical_stem, {
        "canonical": canonical,
        "year": year,
        "season": season,
        "type": couture,
        "month": month,
    }


# ============================================================
# 文件扫描
# ============================================================

def scan_files(folder: Path):
    files = [
        p
        for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    if SORT_FILES:
        files.sort(key=lambda p: natural_key(p.name))

    return files


# ============================================================
# 生成 Rename Plan
# ============================================================

def build_plan(folder: Path):
    files = scan_files(folder)

    groups = defaultdict(list)
    unknown = []

    parsed = []

    for path in files:
        canonical_stem, metadata = build_canonical_stem(path.stem)

        item = {
            "path": path,
            "original": path.name,
            "original_stem": path.stem,
            "canonical_stem": canonical_stem,
            **metadata,
        }

        parsed.append(item)

        if canonical_stem is None:
            unknown.append(item)
        else:
            groups[canonical_stem].append(item)

    # 为每个分类重新编号
    plan = []

    for canonical_stem, items in groups.items():
        for index, item in enumerate(items, start=1):
            new_name = (
                f"{canonical_stem}_{index:03d}"
                f"{item['path'].suffix.lower()}"
            )

            item["new_name"] = new_name
            plan.append(item)

    # 未识别文件
    for item in unknown:
        item["new_name"] = None
        plan.append(item)

    return plan


# ============================================================
# 检查目标文件冲突
# ============================================================

def check_conflicts(plan):
    targets = defaultdict(list)

    for item in plan:
        if item["new_name"]:
            targets[item["new_name"]].append(item)

    conflicts = {
        name: items
        for name, items in targets.items()
        if len(items) > 1
    }

    return conflicts


# ============================================================
# 输出 CSV
# ============================================================

def write_csv(plan, output_file: Path):
    with output_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "original",
            "canonical",
            "year",
            "season",
            "type",
            "month",
            "new_name",
        ])

        for item in plan:
            writer.writerow([
                item["original"],
                item["canonical"],
                item["year"],
                item["season"],
                item["type"],
                item["month"],
                item["new_name"],
            ])


# ============================================================
# Dry Run
# ============================================================

def print_plan(plan):
    print()
    print("=" * 100)
    print("DRY RUN")
    print("=" * 100)

    recognized = 0
    unknown = 0

    for item in plan:
        if item["new_name"]:
            recognized += 1

            print(
                f"{item['original']:<55}"
                f" -> "
                f"{item['new_name']}"
            )
        else:
            unknown += 1

            print(
                f"[UNMATCHED] {item['original']}"
            )

    print()
    print("=" * 100)
    print(f"识别成功：{recognized}")
    print(f"未识别：  {unknown}")
    print("=" * 100)


# ============================================================
# 执行 Rename
# ============================================================

def execute_rename(plan):
    """
    两阶段重命名：

    第一阶段：
        原文件 -> 临时文件

    第二阶段：
        临时文件 -> 最终文件

    防止：
        A -> B
        B -> C

    这种文件名互相覆盖的问题。
    """

    rename_items = [
        item
        for item in plan
        if item["new_name"]
        and item["original"] != item["new_name"]
    ]

    if not rename_items:
        print("没有需要重命名的文件。")
        return

    temp_items = []

    print()
    print("第一阶段：生成临时文件名...")

    for index, item in enumerate(rename_items, start=1):
        source = item["path"]

        temp_name = (
            f".__rename_tmp_{index:06d}"
            f"{source.suffix.lower()}"
        )

        temp_path = source.parent / temp_name

        if temp_path.exists():
            raise RuntimeError(
                f"临时文件已经存在：{temp_path}"
            )

        source.rename(temp_path)

        item["temp_path"] = temp_path
        temp_items.append(item)

    print("第二阶段：写入最终文件名...")

    for item in temp_items:
        target = item["path"].parent / item["new_name"]

        if target.exists():
            raise RuntimeError(
                f"目标文件已存在，停止操作：{target}"
            )

        item["temp_path"].rename(target)

    print()
    print(f"完成：{len(temp_items)} 个文件。")


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Fashion image filename normalizer"
    )

    parser.add_argument(
        "folder",
        type=Path,
        help="图片所在目录",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="真正执行重命名；默认仅 dry-run",
    )

    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="输出 CSV 映射表",
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

    plan = build_plan(folder)

    conflicts = check_conflicts(plan)

    if conflicts:
        print("发现目标文件名冲突：")

        for name, items in conflicts.items():
            print()
            print(name)

            for item in items:
                print(
                    f"    {item['original']}"
                )

        raise SystemExit(
            "存在文件名冲突，已停止。"
        )

    print_plan(plan)

    if args.csv:
        write_csv(plan, args.csv)
        print()
        print(
            f"CSV 已输出：{args.csv}"
        )

    if not args.apply:
        print()
        print(
            "当前为 DRY RUN，没有修改任何文件。"
        )
        print(
            "确认映射无误后，加 --apply 才会真正重命名。"
        )
        return

    # 执行前再次要求确认
    print()
    answer = input(
        "确认执行以上重命名？输入 YES 继续："
    )

    if answer != "YES":
        print("已取消。")
        return

    execute_rename(plan)


if __name__ == "__main__":
    main()