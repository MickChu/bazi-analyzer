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
    from openpyxl.chart import BarChart, Reference
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "缺少 openpyxl 依赖。请先安装：pip install openpyxl"
    ) from exc

from bazi_engine import (
    BaziCalculator, BaziAnalyzer,
    DIZHI_CANGGAN, DIZHI_WUXING, TIANGAN_WUXING,
)

# 十神与五行的固定展示顺序（保证输出稳定）
_SHISHEN_ORDER = [
    "比肩", "劫财", "食神", "伤官", "偏财",
    "正财", "七杀", "正官", "偏印", "正印",
]
_WUXING_ORDER = ["金", "木", "水", "火", "土"]


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
# Sheet 2 / Sheet 3 数据构建
# ============================================================

def _tiangan_shishen_rows(data):
    """天干十神表数据：[(位置, 天干, 十神), ...]"""
    mp = data["命盘总览"]
    tgs = data["十神分析"]["天干十神"]
    mapping = [
        ("年干", mp["年柱"]["天干"]),
        ("月干", mp["月柱"]["天干"]),
        ("日干", mp["日柱"]["天干"]),
        ("时干", mp["时柱"]["天干"]),
        ("胎元干", mp["胎元"]["天干"]),
        ("命宫干", mp["命宫"]["天干"]),
        ("身宫干", mp["身宫"]["天干"]),
    ]
    return [[label, gan, tgs.get(label, "—")] for label, gan in mapping if gan]


def _dizhi_canggan_shishen_rows(data):
    """地支藏干十神表数据：[(位置, 地支, 藏干十神), ...]"""
    mp = data["命盘总览"]
    cgs = data["十神分析"]["地支藏干十神"]
    mapping = [
        ("年支", mp["年柱"]["地支"]),
        ("月支", mp["月柱"]["地支"]),
        ("日支", mp["日柱"]["地支"]),
        ("时支", mp["时柱"]["地支"]),
        ("胎元支", mp["胎元"]["地支"]),
        ("命宫支", mp["命宫"]["地支"]),
        ("身宫支", mp["身宫"]["地支"]),
    ]
    rows = []
    for label, zhi in mapping:
        if not zhi:
            continue
        shishen = "、".join(cgs.get(label, [])) if cgs.get(label) else "—"
        rows.append([label, zhi, shishen])
    return rows


def _shishen_stat_rows(data):
    """十神统计表数据：[(十神, 数量), ...]（按数量降序，同数按固定顺序）"""
    dist = data["十神分析"]["十神统计"]

    def _key(kv):
        name, count = kv
        order = (_SHISHEN_ORDER.index(name)
                 if name in _SHISHEN_ORDER else len(_SHISHEN_ORDER))
        return (-count, order)

    return [[name, count] for name, count in sorted(dist.items(), key=_key)]


def _wuxing_dist_rows(data):
    """
    五行力量分布表：[(五行, 天干数, 地支数, 藏干数, 合计), ...]

    依据子平命理：天干、地支、藏干分别统计后再汇总。
    天干以天干五行计，地支以地支本气五行计，藏干逐干统计。
    """
    mp = data["命盘总览"]
    tian = {wx: 0 for wx in _WUXING_ORDER}
    dizhi = {wx: 0 for wx in _WUXING_ORDER}
    canggan = {wx: 0 for wx in _WUXING_ORDER}

    for label in ["年柱", "月柱", "日柱", "时柱"]:
        wx_g = TIANGAN_WUXING.get(mp[label]["天干"])
        wx_z = DIZHI_WUXING.get(mp[label]["地支"])
        if wx_g in tian:
            tian[wx_g] += 1
        if wx_z in dizhi:
            dizhi[wx_z] += 1
        for cg in mp[label].get("藏干", []):
            wx_c = TIANGAN_WUXING.get(cg)
            if wx_c in canggan:
                canggan[wx_c] += 1

    rows = []
    for wx in _WUXING_ORDER:
        rows.append([wx, tian[wx], dizhi[wx], canggan[wx],
                     tian[wx] + dizhi[wx] + canggan[wx]])
    return rows


def _wuxing_score_rows(data):
    """五行加权得分表：[(五行, 得分, 占比), ...]"""
    wscore = data["五行力量"]["加权得分"]
    score = wscore.get("得分", {})
    ratio = wscore.get("占比", {})
    return [
        [wx, score.get(wx, 0.0), f"{ratio.get(wx, 0.0)}%"]
        for wx in _WUXING_ORDER
    ]


def _write_sheet_header(ws, title, subtitle, ncols):
    """写入标题（第1行）与副标题（第2行），返回第3行为内容起始"""
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    c = ws.cell(row=1, column=1, value=title)
    c.font = _title_font(18)
    c.alignment = _center_alignment()
    ws.row_dimensions[1].height = 34

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    c = ws.cell(row=2, column=1, value=subtitle)
    c.font = _subtitle_font(12)
    c.alignment = _center_alignment()
    ws.row_dimensions[2].height = 22


def _write_table(ws, start_row, headers, rows, widths):
    """
    写入一张带表头的表格，返回下一可用行号

    Args:
        ws: 工作表
        start_row: 表头所在行号
        headers: list[str] 表头
        rows: list[list] 数据行
        widths: list[int] 各列宽
    """
    for col, text in enumerate(headers, start=1):
        cell = ws.cell(row=start_row, column=col, value=text)
        cell.font = _header_font()
        cell.fill = _header_fill()
        cell.alignment = _center_alignment()
        cell.border = _thin_border()
    ws.row_dimensions[start_row].height = 22

    for r, row_data in enumerate(rows, start=start_row + 1):
        for col, value in enumerate(row_data, start=1):
            cell = ws.cell(row=r, column=col, value=value)
            cell.font = _body_font(11)
            cell.alignment = _center_alignment()
            cell.border = _thin_border()
            if r % 2 == 0:
                cell.fill = _alt_fill()

    for i, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    return start_row + len(rows) + 1


def _section_label(ws, row, ncols, text):
    """写入节标题，返回该节内容起始行（row+1）"""
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = _subtitle_font(11)
    c.alignment = Alignment(horizontal="left", vertical="center")
    return row + 1


def _build_sheet2(wb, data):
    """Sheet 2：十神分析 — 天干十神表 + 地支藏干十神表 + 十神统计"""
    ws = wb.create_sheet("十神分析")
    _write_sheet_header(ws, "八字命盘分析报告", "十神分析", 3)

    row = 4
    row = _section_label(ws, row, 3, "一、天干十神")
    row = _write_table(ws, row, ["位置", "天干", "十神"],
                       _tiangan_shishen_rows(data), [14, 10, 12])

    row += 1
    row = _section_label(ws, row, 3, "二、地支藏干十神")
    row = _write_table(ws, row, ["位置", "地支", "藏干十神"],
                       _dizhi_canggan_shishen_rows(data), [14, 10, 28])

    row += 1
    row = _section_label(ws, row, 3, "三、十神统计（含地支藏干）")
    stat_rows = _shishen_stat_rows(data)
    total = sum(cnt for _, cnt in stat_rows)
    stat_rows.append(["合计", total])
    _write_table(ws, row, ["十神", "数量"], stat_rows, [16, 10])

    footer_row = ws.max_row + 1
    ws.merge_cells(start_row=footer_row, start_column=1,
                   end_row=footer_row, end_column=3)
    foot = ws.cell(row=footer_row, column=1,
                   value="依据：《渊海子平》十神体系 · 由 bazi_engine 计算")
    foot.font = _body_font(9, color="888888")
    foot.alignment = Alignment(horizontal="center", vertical="center")


def _build_sheet3(wb, data):
    """Sheet 3：五行力量 — 分布统计 + 加权得分 + 强弱柱状图"""
    ws = wb.create_sheet("五行力量")
    _write_sheet_header(ws, "八字命盘分析报告", "五行力量", 5)

    row = 4
    row = _section_label(ws, row, 5, "一、五行分布统计（天干 / 地支 / 藏干）")
    row = _write_table(ws, row, ["五行", "天干", "地支", "藏干", "合计"],
                       _wuxing_dist_rows(data), [10, 10, 10, 10, 10])

    row += 1
    row = _section_label(
        ws, row, 5,
        "二、五行加权得分（天干×1 · 地支本气×1 · 中气×0.6 · 余气×0.3 · 月令×1.5）",
    )
    score_rows = _wuxing_score_rows(data)
    score_table_start = row
    row = _write_table(ws, row, ["五行", "得分", "占比"], score_rows,
                       [10, 10, 10])

    # 最强 / 最弱五行
    row += 1
    wscore = data["五行力量"]["加权得分"]
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
    c1 = ws.cell(row=row, column=1,
                 value=f"最强五行：{wscore.get('最强五行', '—')}")
    c1.font = _body_font(11, bold=True)
    c1.alignment = Alignment(horizontal="left", vertical="center")
    ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=5)
    c2 = ws.cell(row=row, column=3,
                 value=f"最弱五行：{wscore.get('最弱五行', '—')}")
    c2.font = _body_font(11, bold=True)
    c2.alignment = Alignment(horizontal="left", vertical="center")

    # 三、强弱柱状图
    row += 2
    row = _section_label(ws, row, 5, "三、五行强弱柱状图")

    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = "五行力量加权得分"
    chart.y_axis.title = "得分"
    chart.x_axis.title = "五行"
    chart.legend = None
    data_ref = Reference(ws, min_col=2, min_row=score_table_start,
                         max_row=score_table_start + len(score_rows))
    cats_ref = Reference(ws, min_col=1, min_row=score_table_start + 1,
                         max_row=score_table_start + len(score_rows))
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    ws.add_chart(chart, f"A{row}")


# ============================================================
# 报告生成入口
# ============================================================

def generate_report(sizhu_data, output_path):
    """
    生成 Excel 命盘报告

    包含三个 Sheet：
        - Sheet 1「命盘总览」：基本信息 + 四柱详表
        - Sheet 2「十神分析」：天干十神 + 地支藏干十神 + 十神统计
        - Sheet 3「五行力量」：分布统计 + 加权得分 + 强弱柱状图

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

    # --- Sheet 2 / Sheet 3 ---
    _build_sheet2(wb, data)
    _build_sheet3(wb, data)

    # --- 保存 ---
    output_path = os.path.abspath(output_path)
    wb.save(output_path)
    return output_path


# ============================================================
# CLI 入口
# ============================================================

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="八字命盘 Excel 报告生成器（命盘总览 / 十神分析 / 五行力量）",
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
