#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bazi_engine.py 单元测试

测试覆盖：
- 纳音五行查询
- 空亡/旬空计算
- 结构化输出 to_dict() / to_json()
- 四柱排盘（含纳音和空亡）
- 神煞系统(上)：天乙贵人、文昌贵人、太极贵人、学堂词馆
"""

import sys
import os
import json

# 确保可以 import bazi_engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bazi_engine import (
    BaziCalculator, BaziAnalyzer, ShenshaCalculator,
    NAYIN, NAYIN_WUXING, XUNKONG,
    TIANGAN, DIZHI,
)


def test_nayin_table():
    """测试：纳音五行表完整性"""
    # 六十甲子应全部覆盖
    for i in range(60):
        gz = TIANGAN[i % 10] + DIZHI[i % 12]
        assert gz in NAYIN, f"缺少 {gz} 的纳音"
        assert NAYIN[gz] in NAYIN_WUXING, f"缺少 {NAYIN[gz]} 的五行"
    print("✅ test_nayin_table: 六十甲子纳音完整覆盖")


def test_get_nayin():
    """测试：get_nayin() 方法"""
    calc = BaziCalculator()
    
    # 甲子乙丑海中金
    result = calc.get_nayin("甲子")
    assert result["nayin"] == "海中金"
    assert result["wuxing"] == "金"

    # 丙午丁未天河水
    result = calc.get_nayin("丙午")
    assert result["nayin"] == "天河水"
    assert result["wuxing"] == "水"

    # 庚申辛酉石榴木
    result = calc.get_nayin("庚申")
    assert result["nayin"] == "石榴木"
    assert result["wuxing"] == "木"

    print("✅ test_get_nayin: 纳音查询正确")


def test_xunkong_table():
    """测试：空亡表完整性"""
    for i in range(60):
        gz = TIANGAN[i % 10] + DIZHI[i % 12]
        assert gz in XUNKONG, f"缺少 {gz} 的空亡"
        assert len(XUNKONG[gz]) == 2, f"{gz} 空亡数据格式错误"
    print("✅ test_xunkong_table: 六十甲子空亡完整覆盖")


def test_get_xunkong():
    """测试：get_xunkong() 方法"""
    calc = BaziCalculator()

    # 甲子旬 → 戌亥空
    for gz in ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉"]:
        result = calc.get_xunkong(gz)
        assert set(result) == {"戌", "亥"}, f"{gz} 空亡应为戌亥，实际 {result}"

    # 甲寅旬 → 子丑空
    for gz in ["甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"]:
        result = calc.get_xunkong(gz)
        assert set(result) == {"子", "丑"}, f"{gz} 空亡应为子丑，实际 {result}"

    print("✅ test_get_xunkong: 空亡计算正确")


def test_calculate_sizhu_extended():
    """测试：扩展排盘（含纳音和空亡）"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")

    # 基础字段
    assert "year" in sz
    assert "month" in sz
    assert "day" in sz
    assert "hour" in sz

    # 纳音字段
    assert "year_nayin" in sz, "缺少 year_nayin"
    assert "month_nayin" in sz, "缺少 month_nayin"
    assert "day_nayin" in sz, "缺少 day_nayin"
    assert "hour_nayin" in sz, "缺少 hour_nayin"

    for key in ["year_nayin", "month_nayin", "day_nayin", "hour_nayin"]:
        assert "nayin" in sz[key], f"{key} 缺少 nayin"
        assert "wuxing" in sz[key], f"{key} 缺少 wuxing"

    # 空亡字段
    assert "xunkong" in sz, "缺少 xunkong"
    assert isinstance(sz["xunkong"], list)
    assert len(sz["xunkong"]) == 2, f"空亡应为2个，实际 {len(sz['xunkong'])}"

    print(f"✅ test_calculate_sizhu_extended: 扩展排盘正常")
    print(f"   1990-06-15 12:00 男")
    print(f"   年柱: {sz['year']} 纳音: {sz['year_nayin']['nayin']}")
    print(f"   月柱: {sz['month']} 纳音: {sz['month_nayin']['nayin']}")
    print(f"   日柱: {sz['day']} 纳音: {sz['day_nayin']['nayin']}")
    print(f"   时柱: {sz['hour']} 纳音: {sz['hour_nayin']['nayin']}")
    print(f"   空亡: {sz['xunkong']}")


def test_to_dict():
    """测试：to_dict() 结构化输出"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    az = BaziAnalyzer(sz)

    result = az.to_dict()

    # 验证顶层结构
    assert "命盘总览" in result
    assert "十神分析" in result
    assert "五行力量" in result
    assert "旺衰分析" in result
    assert "格局分析" in result
    assert "大运" in result

    # 验证命盘总览
    mp = result["命盘总览"]
    for pillar in ["年柱", "月柱", "日柱", "时柱"]:
        assert pillar in mp
        assert "干支" in mp[pillar]
        assert "纳音" in mp[pillar]
        assert "藏干" in mp[pillar]

    # 日柱标记
    assert mp["日柱"]["日主"] is True

    # 空亡
    assert "空亡" in mp
    assert len(mp["空亡"]) == 2

    # 旺衰
    assert "评分" in result["旺衰分析"]
    assert "结果" in result["旺衰分析"]

    # 格局
    assert "格局" in result["格局分析"]
    assert "喜用神" in result["格局分析"]
    assert "忌神" in result["格局分析"]
    assert "策略" in result["格局分析"]

    print("✅ test_to_dict: 结构化输出完整")


def test_to_json():
    """测试：to_json() JSON 输出"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    az = BaziAnalyzer(sz)

    json_str = az.to_json()
    data = json.loads(json_str)

    assert "命盘总览" in data
    assert "十神分析" in data
    assert "旺衰分析" in data

    # 验证可以二次序列化
    json_str2 = az.to_json(indent=4)
    assert len(json_str2) > len(json_str)  # indent=4 应该有更多空白

    print("✅ test_to_json: JSON 输出正常")
    print(f"   JSON 长度: {len(json_str)} 字符")


def test_backward_compat():
    """测试：向后兼容性 — 不带纳音/空亡的旧数据仍可正常工作"""
    old_data = {
        "year": "庚午",
        "month": "壬午",
        "day": "辛亥",
        "hour": "甲午",
        "yuejian": "午",
        "dayun": [],
        "dayun_direction": "顺排",
    }
    az = BaziAnalyzer(old_data)

    # to_dict 不应崩溃
    result = az.to_dict()
    assert "命盘总览" in result

    # to_json 不应崩溃
    json_str = az.to_json()
    assert isinstance(json_str, str)

    print("✅ test_backward_compat: 向后兼容性正常")


# ============================================================
# v1.1.1 神煞系统（上）测试
# ============================================================

def test_tianyi_guiren():
    """测试：天乙贵人日干/年干双查"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    sc = ShenshaCalculator(sz)

    result = sc.tianyi_guiren()
    assert "日干查" in result
    assert "年干查" in result
    assert "贵人地支" in result
    assert "所在柱位" in result
    assert isinstance(result["贵人地支"], list)

    # 1990年6月15日12时 男: 年庚午, 月壬午, 日辛亥, 时甲午
    # 日干辛: 天乙贵人在寅/午
    # 年干庚: 天乙贵人在丑/未
    assert "午" in result["贵人地支"], f"日干辛应有贵人午，实际: {result['贵人地支']}"

    print(f"✅ test_tianyi_guiren: 天乙贵人计算正常")
    print(f"   日干辛: 贵人地支 {result['贵人地支']}")
    print(f"   日干查: {result['日干查']}")
    print(f"   年干查: {result['年干查']}")


def test_tianyi_table():
    """测试：天乙贵人表完整性 — 十天干全覆盖"""
    from bazi_engine import TIANGAN
    for gan in TIANGAN:
        assert gan in ShenshaCalculator._TIANYI, f"缺少 {gan} 天乙贵人"
        zhi_list = ShenshaCalculator._TIANYI[gan]
        assert len(zhi_list) == 2, f"{gan} 天乙贵人应为2个，实际 {len(zhi_list)}"
    print("✅ test_tianyi_table: 天乙贵人表完整覆盖十天干")


def test_wenchang_xueren():
    """测试：文昌贵人日干查"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1984, 2, 4, 8, "男")
    sc = ShenshaCalculator(sz)

    result = sc.wenchang_xueren()
    assert "文昌地支" in result
    assert "所在柱位" in result
    assert "有文昌" in result

    # 1984年2月4日8时 男: 年癸亥, 月乙丑, 日戊辰, 时丙辰
    # 日干戊: 文昌在申
    assert result["文昌地支"] == "申", f"日干戊文昌应为申，实际: {result['文昌地支']}"

    print(f"✅ test_wenchang_xueren: 文昌贵人计算正常")
    print(f"   日干戊: 文昌在{result['文昌地支']}, 有文昌={result['有文昌']}")


def test_wenchang_table():
    """测试：文昌贵人表完整性"""
    for gan in TIANGAN:
        assert gan in ShenshaCalculator._WENCHANG, f"缺少 {gan} 文昌"
        assert ShenshaCalculator._WENCHANG[gan] in DIZHI, \
            f"{gan} 文昌地支不在十二地支中"
    print("✅ test_wenchang_table: 文昌贵人表完整")


def test_taiji_guiren():
    """测试：太极贵人日干/年干双查"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    sc = ShenshaCalculator(sz)

    result = sc.taiji_guiren()
    assert "日干查" in result
    assert "年干查" in result
    assert "贵人地支" in result

    # 日干辛: 太极在寅/亥
    # 年干庚: 太极在寅/亥
    assert "寅" in result["贵人地支"] or "亥" in result["贵人地支"], \
        f"日干辛太极应有寅或亥，实际: {result['贵人地支']}"

    print(f"✅ test_taiji_guiren: 太极贵人计算正常")
    print(f"   日干辛: 太极地支 {result['贵人地支']}")
    print(f"   日干查: {result['日干查']}")


def test_taiji_table():
    """测试：太极贵人表完整性"""
    for gan in TIANGAN:
        assert gan in ShenshaCalculator._TAIJI, f"缺少 {gan} 太极贵人"
    # 戊己应有四季(4个)
    for gan in ["戊", "己"]:
        assert len(ShenshaCalculator._TAIJI[gan]) == 4, \
            f"{gan} 太极贵人应为4个(四季)，实际 {len(ShenshaCalculator._TAIJI[gan])}"
    print("✅ test_taiji_table: 太极贵人表完整")


def test_xuetang_ciguan():
    """测试：学堂词馆日干查"""
    calc = BaziCalculator()
    # 日干甲 → 学堂亥, 词馆寅
    sz = calc.calculate_sizhu(1984, 2, 2, 8, "男")
    sc = ShenshaCalculator(sz)

    result = sc.xuetang_ciguan()
    assert "学堂" in result
    assert "词馆" in result
    assert "所在地支" in result["学堂"]
    assert "有学堂" in result["学堂"]
    assert "有词馆" in result["词馆"]

    print(f"✅ test_xuetang_ciguan: 学堂词馆计算正常")
    print(f"   学堂: {result['学堂']}")
    print(f"   词馆: {result['词馆']}")


def test_xuetang_ciguan_table():
    """测试：学堂词馆表完整性"""
    for gan in TIANGAN:
        assert gan in ShenshaCalculator._XUETANG, f"缺少 {gan} 学堂"
        assert ShenshaCalculator._XUETANG[gan] in DIZHI, \
            f"{gan} 学堂地支不在十二地支中"
        assert gan in ShenshaCalculator._CIGUAN, f"缺少 {gan} 词馆"
        assert ShenshaCalculator._CIGUAN[gan] in DIZHI, \
            f"{gan} 词馆地支不在十二地支中"
    print("✅ test_xuetang_ciguan_table: 学堂词馆表完整")


def test_get_shensha_integration():
    """测试：BaziAnalyzer.get_shensha() 集成入口 (v1.1.2 11神煞)"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    az = BaziAnalyzer(sz)

    result = az.get_shensha()
    assert "详细" in result
    assert "汇总" in result

    detail = result["详细"]
    for name in ["天乙贵人", "文昌贵人", "太极贵人", "学堂词馆",
                 "桃花", "羊刃", "驿马", "华盖", "将星", "孤辰寡宿", "红鸾天喜"]:
        assert name in detail, f"缺少 {name}"
        assert "data" in detail[name], f"{name} 缺少 data"
        assert "吉凶" in detail[name], f"{name} 缺少 吉凶"

    # 验证天乙贵人 data 结构
    ty = detail["天乙贵人"]["data"]
    assert "日干查" in ty
    assert "年干查" in ty

    # 验证汇总
    summary = result["汇总"]
    assert "吉神命中" in summary
    assert "凶煞命中" in summary
    assert "总计" in summary

    print("✅ test_get_shensha_integration: 集成入口正常 (v1.1.2 11神煞)")


def test_to_dict_with_shensha():
    """测试：to_dict() 包含完整11神煞数据"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    az = BaziAnalyzer(sz)

    result = az.to_dict()
    assert "神煞" in result, "to_dict 应包含 神煞 字段"
    shensha = result["神煞"]
    assert "详细" in shensha
    assert "汇总" in shensha
    detail = shensha["详细"]
    for name in ["天乙贵人", "文昌贵人", "太极贵人", "学堂词馆",
                 "桃花", "羊刃", "驿马", "华盖", "将星", "孤辰寡宿", "红鸾天喜"]:
        assert name in detail, f"to_dict 神煞缺少 {name}"

    print("✅ test_to_dict_with_shensha: to_dict 包含完整11神煞数据")


# ============================================================
# v1.1.3 胎元 + 命宫 测试
# ============================================================

def test_taiyuan():
    """测试：get_taiyuan() 胎元计算"""
    calc = BaziCalculator()

    # 胎元 = 月干顺推一位 + 月支顺推三位
    assert calc.get_taiyuan("甲子") == "乙卯", "甲子月胎元应为乙卯"
    assert calc.get_taiyuan("丙寅") == "丁巳", "丙寅月胎元应为丁巳"
    assert calc.get_taiyuan("庚申") == "辛亥", "庚申月胎元应为辛亥"
    # 边界：癸亥月 → 甲寅（天干地支均回环）
    assert calc.get_taiyuan("癸亥") == "甲寅", "癸亥月胎元应为甲寅"

    print("✅ test_taiyuan: 胎元计算正确（月干+1、月支+3）")


def test_minggong():
    """测试：get_minggong() 命宫计算（月支起子时逆数至生时）"""
    calc = BaziCalculator()

    # 甲子月甲子时 → 命宫在子
    assert calc.get_minggong("甲子", "甲子") == "子", "子月子时命宫应为子"
    # 丙寅月甲午时 → 命宫在申
    assert calc.get_minggong("丙寅", "甲午") == "申", "寅月午时命宫应为申"
    # 子月丑时 → 命宫在亥（逆数一位）
    assert calc.get_minggong("甲子", "乙丑") == "亥", "子月丑时命宫应为亥"

    print("✅ test_minggong: 命宫计算正确（月支起子逆数至生时）")


def test_calculate_sizhu_with_taiyuan_minggong():
    """测试：扩展排盘包含胎元/命宫及纳音"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")

    # 字段存在性
    assert "taiyuan" in sz, "缺少 taiyuan"
    assert "minggong" in sz, "缺少 minggong"
    assert "taiyuan_nayin" in sz, "缺少 taiyuan_nayin"
    assert "minggong_nayin" in sz, "缺少 minggong_nayin"

    # 干支格式（2字符）
    assert len(sz["taiyuan"]) == 2
    assert len(sz["minggong"]) == 2

    # 1990-06-15 12时 男: 月柱癸未 → 胎元甲戌；命宫丁丑
    assert sz["taiyuan"] == "甲戌", f"月柱癸未胎元应为甲戌，实际 {sz['taiyuan']}"
    assert sz["minggong"] == "丁丑", f"命宫应为丁丑，实际 {sz['minggong']}"

    # 纳音
    assert sz["taiyuan_nayin"]["nayin"] == "山头火"
    assert sz["minggong_nayin"]["nayin"] == "涧下水"

    print(f"✅ test_calculate_sizhu_with_taiyuan_minggong: 排盘含胎元命宫")
    print(f"   胎元: {sz['taiyuan']} ({sz['taiyuan_nayin']['nayin']})")
    print(f"   命宫: {sz['minggong']} ({sz['minggong_nayin']['nayin']})")


def test_to_dict_with_taiyuan_minggong():
    """测试：to_dict() 包含胎元/命宫字段（干支/藏干/纳音/十神）"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    az = BaziAnalyzer(sz)

    result = az.to_dict()
    mp = result["命盘总览"]

    # 命盘总览含胎元/命宫
    assert "胎元" in mp, "命盘总览缺少胎元"
    assert "命宫" in mp, "命盘总览缺少命宫"

    for name in ["胎元", "命宫"]:
        fu = mp[name]
        for key in ["干支", "天干", "地支", "五行", "阴阳", "藏干", "纳音", "十神"]:
            assert key in fu, f"{name} 缺少 {key}"
        assert fu["干支"], f"{name} 干支为空"
        assert fu["纳音"].get("nayin"), f"{name} 纳音为空"
        assert isinstance(fu["藏干"], list) and len(fu["藏干"]) > 0, f"{name} 藏干为空"
        assert fu["十神"], f"{name} 十神为空"

    # 十神分析含胎元/命宫
    tg = result["十神分析"]["天干十神"]
    assert "胎元干" in tg
    assert "命宫干" in tg
    dg = result["十神分析"]["地支藏干十神"]
    assert "胎元支" in dg
    assert "命宫支" in dg

    # 1990-06-15 日主辛，胎元干甲为正财、命宫干丁为七杀
    assert tg["胎元干"] == "正财", f"胎元干甲应为正财，实际 {tg['胎元干']}"
    assert tg["命宫干"] == "七杀", f"命宫干丁应为七杀，实际 {tg['命宫干']}"

    print("✅ test_to_dict_with_taiyuan_minggong: to_dict 包含胎元命宫完整信息")


def test_taiyuan_minggong_backward_compat():
    """测试：旧数据（无胎元/命宫）to_dict 不崩溃"""
    old_data = {
        "year": "庚午",
        "month": "壬午",
        "day": "辛亥",
        "hour": "甲午",
        "yuejian": "午",
        "dayun": [],
        "dayun_direction": "顺排",
    }
    az = BaziAnalyzer(old_data)
    result = az.to_dict()

    mp = result["命盘总览"]
    assert mp["胎元"]["干支"] == ""
    assert mp["命宫"]["干支"] == ""

    print("✅ test_taiyuan_minggong_backward_compat: 旧数据兼容正常")


if __name__ == "__main__":
    print("=" * 60)
    print("bazi_engine.py 单元测试 — v1.1.0 新增功能")
    print("=" * 60)
    print()

    tests = [
        test_nayin_table,
        test_get_nayin,
        test_xunkong_table,
        test_get_xunkong,
        test_calculate_sizhu_extended,
        test_to_dict,
        test_to_json,
        test_backward_compat,
        # v1.1.1 神煞系统（上）
        test_tianyi_table,
        test_tianyi_guiren,
        test_wenchang_table,
        test_wenchang_xueren,
        test_taiji_table,
        test_taiji_guiren,
        test_xuetang_ciguan_table,
        test_xuetang_ciguan,
        test_get_shensha_integration,
        test_to_dict_with_shensha,
        # v1.1.3 胎元 + 命宫
        test_taiyuan,
        test_minggong,
        test_calculate_sizhu_with_taiyuan_minggong,
        test_to_dict_with_taiyuan_minggong,
        test_taiyuan_minggong_backward_compat,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    print(f"结果: {passed}/{passed+failed} 通过, {failed} 失败")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
