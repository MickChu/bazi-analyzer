#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
子平命理实战派宗师 - CLI 交互界面
依赖 bazi_engine.py 规则引擎（from bazi_engine import ...）
"""

import sys
from datetime import datetime

from bazi_engine import (
    TIANGAN, DIZHI, TIANGAN_WUXING, TIANGAN_YINYANG,
    DIZHI_WUXING, DIZHI_CANGGAN, LIUHE, LIUCHONG, SANHE, SANHUI,
    get_shishen, BaziCalculator, BaziAnalyzer,
)


# ============================================================
# 颜色工具
# ============================================================

class C:
    B = "\033[1m";  H = "\033[95m"; BL = "\033[94m"; CY = "\033[96m"
    G = "\033[92m";  Y = "\033[93m";  R = "\033[91m";  E = "\033[0m"

def _enable_ansi():
    if sys.platform == "win32":
        try:
            import ctypes; ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

def _banner():
    print(f"""{C.B}{C.Y}
╔══════════════════════════════════════════════════════════════╗
║          子平命理实战派宗师 · 命局分析系统【完全离线版】          ║
║    研习《滴天髓》《渊海子平》《三命通会》《穷通宝鉴》              ║
║         直断 · 重结构 · 轻神煞 · 重五行流通                     ║
╚══════════════════════════════════════════════════════════════╝
{C.E}""")

def _sec(t):
    print(f"\n{C.B}{C.G}【{t}】{C.E}\n{C.CY}{'─'*60}{C.E}")

def _sub(t):
    print(f"\n{C.B}{C.CY}▸ {t}{C.E}")

def _div(c="─", w=60):
    print(f"{C.CY}{c*w}{C.E}")


# ============================================================
# 输出模块
# ============================================================

def _sizhu(data):
    _sec("一、排盘结构（15%）")
    print(f"\n{C.B}四柱命盘：{C.E}")
    for label, gz in [("年柱", "year"), ("月柱", "month"),
                      ("日柱", "day"), ("时柱", "hour")]:
        tag = " ← 日主" if gz == "day" else ""
        g, z = data[gz][0], data[gz][1]
        print(f"  {label}：{C.Y}{data[gz]}{C.E}  "
              f"({TIANGAN_WUXING[g]}{TIANGAN_YINYANG[g]}{label[-1]}){tag}")

    print(f"\n{C.B}地支藏干：{C.E}")
    for label, gz in [("年支", "year"), ("月支", "month"),
                      ("日支", "day"), ("时支", "hour")]:
        cg = "、".join(f"{g}({TIANGAN_WUXING[g]})" for g in DIZHI_CANGGAN[data[gz][1]])
        print(f"  {label} {data[gz][1]}：{cg}")

def _shishen(az):
    print(f"\n{C.B}十神分布：{C.E}")
    dg = az.day_gan
    for label, gz in [("年干", "year"), ("月干", "month"),
                      ("日干", "day"), ("时干", "hour")]:
        tag = "日主" if gz == "day" else get_shishen(dg, az.data[gz][0])
        print(f"  {label}：{az.data[gz][0]} → {tag}")

    dist = az.get_shishen_distribution()
    print(f"\n  十神统计：", end="")
    for ss, n in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"{ss}:{n} ", end="")
    print()

def _wangshuai(az):
    _sec("二、原局深度分析（35%）")
    ws = az.analyze_wangshuai()
    _sub("日元旺衰判断")
    print(f"\n  日主：{az.day_gan} ({TIANGAN_WUXING[az.day_gan]})")
    print(f"  月令：{az.data['yuejian']} ({DIZHI_WUXING[az.data['yuejian']]})")
    print(f"\n  {C.B}旺衰评分：{ws['score']}分 - {ws['result']}{C.E}")
    print(f"\n  详细分析：")
    for d in ws["details"]:
        print(f"    · {d}")
    return ws

def _xiyong(az, ws):
    xy = az.determine_xiyong(ws)
    _sub("喜用神分析")
    print(f"  喜神（有利）：{C.G}{'、'.join(xy['xishen'])}{C.E}")
    print(f"  忌神（不利）：{C.R}{'、'.join(xy['jishen'])}{C.E}")
    print(f"  策略：{C.Y}{xy['strategy']}{C.E}")
    return xy

def _geju(az):
    _sub("格局判断")
    for g in az.analyze_geju():
        print(f"  · {g}")

def _wuxing(az):
    _sub("五行流通图解")
    dist = az.get_wuxing_distribution()
    for wx in ["金", "木", "水", "火", "土"]:
        bar = "█" * dist[wx] + "░" * (6 - dist[wx])
        tag = ""
        if dist[wx] >= 4:   tag = f" {C.R}【过旺】{C.E}"
        elif dist[wx] == 0: tag = f" {C.R}【缺失】{C.E}"
        elif dist[wx] <= 1: tag = f" {C.Y}【偏弱】{C.E}"
        print(f"    {wx}：{bar} ({dist[wx]}){tag}")

    mx, mn = max(dist, key=dist.get), min(dist, key=dist.get)
    print(f"\n  流通分析：")
    print(f"    · {mx}最旺，{mn}最弱")
    print(f"    · 注意{mx}过旺可能堵塞五行流通")

def _xingge(az, ws, xy):
    _sub("核心性格断语")
    xg = az.analyze_xingge(ws, xy)
    print(f"  日主五行特质：")
    print(f"    优点：{C.G}{xg['base']['优点']}{C.E}")
    print(f"    缺点：{C.R}{xg['base']['缺点']}{C.E}")
    print(f"\n  身强身弱倾向：{xg['tendency']}")

def _zongjie(az, ws):
    _sub("命局层次一句话总结")
    print(f"  {C.B}{C.Y}{az.get_summary_verdict(ws)}{C.E}")

def _dayun(az, age):
    _sec("三、大运与流年（30%）")
    _sub("大运走势")
    for dy in az.analyze_dayun(age):
        clr = C.G if "当前" in dy["status"] else C.CY
        print(f"  {clr}[{dy['status']}]{C.E} {dy['ganzhi']} ({dy['wuxing']}) {dy['age_range']}")

def _liunian():
    _sub("近2年流年")
    y = datetime.now().year
    print(f"  {y}年：需结合大运和原局分析")
    print(f"  {y+1}年：注意流年干支与命局互动")

def _fenlei(az, xy):
    _sub("分领域直断")
    ss = az.get_shishen_distribution()
    ws = az.analyze_wangshuai()

    print(f"\n  {C.B}财运：{C.E}")
    fc = ss.get("正财", 0) + ss.get("偏财", 0)
    if fc >= 2:
        print(f"    · 财星较旺，有求财意识  风险：中")
    else:
        print(f"    · 财星较弱，求财需努力  风险：低")

    print(f"\n  {C.B}事业：{C.E}")
    gc = ss.get("正官", 0) + ss.get("七杀", 0)
    sc = ss.get("食神", 0) + ss.get("伤官", 0)
    if gc >= 2:
        print(f"    · 官杀旺，事业心强，压力也大")
    elif sc >= 2:
        print(f"    · 食伤旺，适合创意、技术类工作")
    else:
        print(f"    · 事业平稳发展")

    print(f"\n  {C.B}感情：{C.E}")
    print(f"    · 日支配偶宫：{az.data['day'][1]} 藏 {DIZHI_CANGGAN[az.data['day'][1]]}")

    print(f"\n  {C.B}健康：{C.E}")
    dist = az.get_wuxing_distribution()
    for wx, n in dist.items():
        if n == 0:
            print(f"    · {wx}缺失，注意相关脏腑健康")
        elif n >= 4:
            print(f"    · {wx}过旺，注意五行失衡")

def _quji(az, xy):
    _sec("四、趋吉避凶（20%）")
    _sub("最佳行业方向"); print(f"  {az.get_career_advice(xy)}")
    _sub("有利方位");      print(f"  {az.get_fangwei_advice(xy)}")

    _sub("行为策略建议")
    dwx = TIANGAN_WUXING[az.day_gan]
    if dwx in xy["xishen"]:
        print(f"  · 日主五行{dwx}为喜，宜主动进取")
    else:
        print(f"  · 日主五行{dwx}非喜，宜守成稳健")

    _sub("投资节奏建议")
    print(f"  · 喜用神运：积极投资，把握机会")
    print(f"  · 忌神运：保守理财，避免冒险")

    _sub("性格修正建议")
    print(f"  · 发挥喜用神五行特质")
    print(f"  · 抑制忌神五行带来的负面影响")

def _zongping(az, ws, xy):
    print(f"\n{C.B}{C.Y}═══ 命局总评 ═══{C.E}\n")
    sc = ws["score"]
    level = "中上格局" if sc >= 50 else ("中等格局" if sc >= 35 else "普通格局")
    dwx = TIANGAN_WUXING[az.day_gan]

    print(f"  {C.B}格局层级：{level}{C.E}")
    contra = (f"身强{dwx}旺，需泄耗疏通" if "身强" in ws["result"]
              else f"身弱{dwx}虚，需生扶补益")
    print(f"  {C.B}核心矛盾：{contra}{C.E}")
    key = f"把握{xy['xishen'][0]}运，规避{xy['jishen'][0]}运"
    print(f"  {C.B}成败关键：{key}{C.E}")
    _div("═")


# ============================================================
# 用户输入
# ============================================================

def _input_datetime():
    print(f"\n{C.CY}请输入出生信息（公历）：{C.E}")
    y  = int(input("出生年份（如 1990）: ").strip())
    m  = int(input("出生月份（1-12）: ").strip())
    d  = int(input("出生日期（1-31）: ").strip())
    hi = input("出生时辰（0-23，不知道输 -1）: ").strip()
    h  = int(hi) if hi != "-1" else 12
    g  = input("性别（男/女）: ").strip()
    nm = input("姓名或称呼（回车跳过）: ").strip() or "命主"
    ai = input("当前年龄（用于大运，回车默认30）: ").strip()
    return {"type": "dt", "year": y, "month": m, "day": d,
            "hour": h, "gender": g, "name": nm,
            "age": int(ai) if ai else 30}

def _input_sizhu():
    print(f"\n{C.CY}请输入四柱（空格分隔）：{C.E}")
    print("示例：甲子 丙寅 戊午 庚申")
    parts = input("四柱: ").strip().split()
    if len(parts) != 4:
        print(f"{C.R}格式错误{C.E}"); return None
    g  = input("性别（男/女）: ").strip()
    ai = input("当前年龄（回车默认30）: ").strip()
    return {"type": "sz", "year": parts[0], "month": parts[1],
            "day": parts[2], "hour": parts[3], "gender": g,
            "name": "命主", "age": int(ai) if ai else 30}

def _collect():
    _sec("请输入出生信息")
    print(f"{C.Y}本程序完全离线运行，无需网络{C.E}\n")
    print("  1. 输入出生日期时间（自动排盘）")
    print("  2. 直接输入已排好的四柱")
    ch = input(f"\n{C.B}请选择 [1/2]: {C.E}").strip()
    return _input_datetime() if ch == "1" else _input_sizhu()


# ============================================================
# 主流程
# ============================================================

def _run():
    info = _collect()
    calc = BaziCalculator()

    if info["type"] == "dt":
        sz = calc.calculate_sizhu(info["year"], info["month"],
                                   info["day"], info["hour"], info["gender"])
    else:
        sz = {"year": info["year"], "month": info["month"],
              "day": info["day"], "hour": info["hour"],
              "yuejian": info["month"][1], "dayun": [],
              "dayun_direction": "未知"}

    az = BaziAnalyzer(sz)

    print(f"\n{C.B}{C.Y}═══ 宗师批命 ═══{C.E}\n")
    print(f"命主：{info['name']} | 性别：{info['gender']}")
    _div()

    _sizhu(sz);   _shishen(az)
    ws = _wangshuai(az); xy = _xiyong(az, ws)
    _geju(az);    _wuxing(az);   _xingge(az, ws, xy);   _zongjie(az, ws)
    _dayun(az, info["age"]); _liunian(); _fenlei(az, xy)
    _quji(az, xy); _zongping(az, ws, xy)

    return az, ws, xy, info

def _save(az, ws, xy, info):
    fn = f"{info['name']}_命局分析.txt"
    with open(fn, "w", encoding="utf-8-sig") as f:
        f.write("子平命理实战派宗师 · 命局分析报告（完全离线版）\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"命主：{info['name']}\n性别：{info['gender']}\n\n")
        f.write("【四柱命盘】\n")
        f.write(f"年柱：{az.data['year']}\n月柱：{az.data['month']}\n"
                f"日柱：{az.data['day']} (日主)\n时柱：{az.data['hour']}\n\n")
        f.write("【旺衰分析】\n")
        f.write(f"评分：{ws['score']}分\n结果：{ws['result']}\n\n")
        f.write("【喜用神】\n")
        f.write(f"喜神：{'、'.join(xy['xishen'])}\n"
                f"忌神：{'、'.join(xy['jishen'])}\n"
                f"策略：{xy['strategy']}\n\n")
        f.write("=" * 60 + "\n本报告由子平命理实战派宗师分析系统生成（完全离线版）\n")
    print(f"\n{C.G}✅ 已保存至：{fn}{C.E}")

def main():
    _enable_ansi()
    _banner()
    print(f"{C.G}✅ 系统就绪 - 完全离线，无需网络{C.E}")
    print(f"{C.Y}输入 quit 退出 | 分析完成后可选保存{C.E}\n")

    while True:
        try:
            az, ws, xy, info = _run()

            s = input(f"\n{C.B}保存报告？(y/n): {C.E}").strip().lower()
            if s == "y":
                _save(az, ws, xy, info)

            c = input(f"{C.B}分析新命局？(y/n): {C.E}").strip().lower()
            if c != "y":
                print(f"\n{C.Y}宗师已退堂，祝命主一切顺遂。{C.E}")
                break
        except KeyboardInterrupt:
            print(f"\n{C.Y}宗师已退堂。{C.E}"); break
        except Exception as e:
            print(f"\n{C.R}错误：{e}{C.E}")
            import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()
