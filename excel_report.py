#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 报告生成器 - 独立可运行模块

依赖：
    openpyxl（本项目唯一外部依赖，用于生成 .xlsx 文件）
    安装：pip install openpyxl

用法（CLI）：
    python excel_report.py --year 1990 --month 6 --day 15 --hour 12 --gender 男
    python excel_report.py --year 1990 --month 6 --day 15 --hour 12 --gender 男 --output report.xlsx

用法（库调用）：
    from excel_report import generate_report
    from bazi_engine import BaziCalculator

    sz = BaziCalculator().calculate_sizhu(1990, 6, 15, 12, "男")
    generate_report(sz, "report.xlsx")

依据：
    - 命盘总览四柱表格：天干/地支/藏干/纳音/空亡/十神
    - 数据来源：《渊海子平》《三命通会》排盘体系，由 bazi_engine 计算
"""

import os
import sys
import argparse

# 确保可以 import 同目录下的 bazi_engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "缺少 openpyxl 依赖。请先安装：pip install openpyxl"
    ) from exc

from bazi_engine import BaziCalculator, BaziAnalyzer, DIZHI_CANGGAN, TIANGAN_WUXING


# ============================================================
# 样式系统
# ============================================================

# 主题色（传统朱砂红 + 灰）
_COLOR_TITLE = "8B1A1A"      # 标题深红
_COLOR_SUBTITLE = "4A4A4A"   # 副标题深灰
_COLOR_HEADER_FILL = "A93226"  # 表头底色（朱砂红）
_COLOR_HEADER_FONT = "FFFFFF"  # 表头文字（白）
_COLOR_BODY_FONT = "333333"    # 正文字色
_COLOR_ALT_FILL = "FDF2F0"     # 隔行浅红底
_COLOR_BORDER = "C9C9C9"       # 边框灰

_FONT_NAME = "微软雅黑"


def _title_font(size=18, bold=True, color=_COLOR_TITLE):
    return Font(name=_FONT_NAME, size=size, bold=bold, color=color)


def _subtitle_font(size=12, bold=True, color=_COLOR_SUBTITLE):
    return Font(name=_FONT_NAME, size=size, bold=bold, color=color)


def _body_font(size=11, bold=False, color=_COLOR_BODY_FONT):
    return Font(name=_FONT_NAME, size=size, bold=bold, color=color)


def _header_font(size=11, bold=True, color=_COLOR_HEADER_FONT):
    return Font(name=_FONT_NAME, size=size, bold=bold, color=color)


def _thin_border():
    side = Side(style="thin", color=_COLOR_BORDER)
    return Border(left=side, right=side, top=side, bottom=side)


def _center_alignment(wrap=True, vertical="center", horizontal="center"):
    return Alignment(horizontal=horizontal, vertical=vertical, wrap_text=wrap)


def _header_fill():
    return PatternFill(fill_type="solid", fgColor=_COLOR_HEADER_FILL)


def _alt_fill():
    return PatternFill(fill_type="solid", fgColor=_COLOR_ALT_FILL)


# ============================================================
# 数据构建
# ============================================================

def _pillar_rows(data):
    """
    从 to_dict() 结果中提取四柱表格数据行

    返回：
        list[list[str]] — 每行 [柱位, 天干, 地支, 藏干, 纳音, 空亡, 十神]
    """
    mp = data["命盘总览"]
    ss = data["十神分析"]["天干十神"]

    xunkong = mp.get("空亡", [])
    xunkong_str = "、".join(xunkong) if xunkong else "—"

    rows = []
    for label, pillar_key, gan_key in [
        ("年柱", "年柱", "年干"),
        ("月柱", "月柱", "月干"),
        ("日柱", "日柱", "日干"),
        ("时柱", "时柱", "时干"),
    ]:
        pillar = mp[pillar_key]
        gan = pillar["天干"]
        zhi = pillar["地支"]
        canggan = "、".join(pillar["藏干"]) if pillar.get("藏干") else "—"
        nayin = pillar["纳音"].get("nayin", "—") if isinstance(pillar.get("纳音"), dict) else "—"
        # 空亡以日柱为基准，仅在日柱行标注
        kong = xunkong_str if label == "日柱" else "—"
        shishen = ss.get(gan_key, "—")

        rows.append([label, gan, zhi, canggan, nayin, kong, shishen])

    return rows


def _basic_info(data, sizhu_data):
    """
    提取基本信息（出生时间、性别、四柱干支、月令、大运方向）

    返回：
        list[tuple[str, str]] — [(标签, 值), ...]
    """
    mp = data["命盘总览"]
    info = []

    # 出生时间 / 性别（如 sizhu_data 附带，则展示）
    if isinstance(sizhu_data, dict) and sizhu_data.get("birth_info"):
        info.append(("出生时间", sizhu_data["birth_info"]))
    else:
        # 尽力从四柱拼接展示，不做农历换算
        info.append(("性别", sizhu_data.get("gender", "未知") if isinstance(sizhu_data, dict) else "未知"))

    sizhu = "  ".join([
        mp["年柱"]["干支"], mp["月柱"]["干支"],
        mp["日柱"]["干支"], mp["时柱"]["干支"],
    ])
    info.append(("四柱", sizhu))
    info.append(("月令", mp.get("月令", "—")))
    info.append(("空亡", "、".join(mp.get("空亡", [])) if mp.get("空亡") else "—"))
    info.append(("大运方向", data.get("大运方向", "—")))

    return info


# ============================================================
# 报告生成入口
# ============================================================

def generate_report(sizhu_data, output_path):
    """
    生成 Excel 命盘报告（当前包含 Sheet 1：命盘总览）

    Args:
        sizhu_data: BaziCalculator.calculate_sizhu() 的返回值
        output_path: 输出 .xlsx 文件路径

    Returns:
        str: 生成的文件绝对路径
    """
    # 兼容直接传入 to_dict() 结果的情况
    if isinstance(sizhu_data, dict) and "命盘总览" in sizhu_data:
        data = sizhu_data
    else:
        analyzer = BaziAnalyzer(sizhu_data)
        data = analyzer.to_dict()

    wb = Workbook()
    ws = wb.active
    ws.title = "命盘总览"

    # --- 标题 ---
    ws.merge_cells("A1:G1")
    title_cell = ws["A1"]
    title_cell.value = "八字命盘分析报告"
    title_cell.font = _title_font(18)
    title_cell.alignment = _center_alignment()
    ws.row_dimensions[1].height = 34

    # --- 副标题 ---
    ws.merge_cells("A2:G2")
    subtitle_cell = ws["A2"]
    subtitle_cell.value = "命盘总览"
    subtitle_cell.font = _subtitle_font(12)
    subtitle_cell.alignment = _center_alignment()
    ws.row_dimensions[2].height = 22

    # --- 基本信息 ---
    info = _basic_info(data, sizhu_data)
    info_start_row = 4
    for i, (label, value) in enumerate(info):
        row = info_start_row + i
        ws.merge_cells(f"A{row}:B{row}")
        ws.merge_cells(f"C{row}:G{row}")
        lab = ws.cell(row=row, column=1, value=label)
        val = ws.cell(row=row, column=3, value=value)
        lab.font = _body_font(11, bold=True)
        val.font = _body_font(11)
        lab.alignment = Alignment(horizontal="right", vertical="center")
        val.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # --- 四柱表格 ---
    header_row = info_start_row + len(info) + 1
    headers = ["柱位", "天干", "地支", "藏干", "纳音", "空亡", "十神"]

    for col, text in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col, value=text)
        cell.font = _header_font()
        cell.fill = _header_fill()
        cell.alignment = _center_alignment()
        cell.border = _thin_border()
    ws.row_dimensions[header_row].height = 22

    rows = _pillar_rows(data)
    for r, row_data in enumerate(rows, start=header_row + 1):
        for col, value in enumerate(row_data, start=1):
            cell = ws.cell(row=r, column=col, value=value)
            cell.font = _body_font(11)
            cell.alignment = _center_alignment()
            cell.border = _thin_border()
            if r % 2 == 0:
                cell.fill = _alt_fill()
        # 日柱行加粗突出日主
        if row_data[0] == "日柱":
            for col in range(1, len(headers) + 1):
                ws.cell(row=r, column=col).font = _body_font(11, bold=True)

    # --- 列宽 ---
    _COL_WIDTHS = [10, 10, 10, 22, 14, 12, 12]
    for i, width in enumerate(_COL_WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # --- 页脚说明 ---
    footer_row = header_row + len(rows) + 1
    ws.merge_cells(f"A{footer_row}:G{footer_row}")
    foot = ws.cell(row=footer_row, column=1,
                   value="依据：《渊海子平》《三命通会》排盘体系 · 由 bazi_engine 计算")
    foot.font = _body_font(9, color="888888")
    foot.alignment = Alignment(horizontal="center", vertical="center")

    # --- 保存 ---
    output_path = os.path.abspath(output_path)
    wb.save(output_path)
    return output_path


# ============================================================
# CLI 入口
# ============================================================

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="八字命盘 Excel 报告生成器（Sheet 1：命盘总览）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python excel_report.py --year 1990 --month 6 --day 15 --hour 12 --gender 男\n"
            "  python excel_report.py --year 1990 --month 6 --day 15 --hour 12 --gender 男 --output report.xlsx\n"
        ),
    )
    parser.add_argument("--year", type=int, required=True, help="出生年（公历）")
    parser.add_argument("--month", type=int, required=True, help="出生月（1-12）")
    parser.add_argument("--day", type=int, required=True, help="出生日（1-31）")
    parser.add_argument("--hour", type=int, required=True, help="出生时（0-23）")
    parser.add_argument("--gender", type=str, required=True, choices=["男", "女"], help="性别")
    parser.add_argument("--output", type=str, default=None, help="输出 .xlsx 路径（默认自动命名）")

    args = parser.parse_args(argv)

    calc = BaziCalculator()
    sizhu = calc.calculate_sizhu(args.year, args.month, args.day, args.hour, args.gender)

    # 附带性别信息供报告展示
    sizhu["gender"] = args.gender
    sizhu["birth_info"] = f"{args.year}年{args.month}月{args.day}日 {args.hour}时"

    if args.output is None:
        output_path = f"bazi_report_{args.year}-{args.month:02d}-{args.day:02d}.xlsx"
    else:
        output_path = args.output

    path = generate_report(sizhu, output_path)
    print(f"[OK] 报告已生成：{path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
