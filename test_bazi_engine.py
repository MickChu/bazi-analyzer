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
    """测试：BaziAnalyzer.get_shensha() 集成入口"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    az = BaziAnalyzer(sz)

    result = az.get_shensha()
    assert "天乙贵人" in result
    assert "文昌贵人" in result
    assert "太极贵人" in result
    assert "学堂词馆" in result

    # 验证结构完整性
    ty = result["天乙贵人"]
    assert "日干查" in ty
    assert "年干查" in ty
    assert "贵人地支" in ty
    assert "所在柱位" in ty

    wc = result["文昌贵人"]
    assert "文昌地支" in wc
    assert "有文昌" in wc

    xc = result["学堂词馆"]
    assert "有学堂" in xc["学堂"]
    assert "有词馆" in xc["词馆"]

    print("✅ test_get_shensha_integration: 集成入口正常")


def test_to_dict_with_shensha():
    """测试：to_dict() 包含神煞数据"""
    calc = BaziCalculator()
    sz = calc.calculate_sizhu(1990, 6, 15, 12, "男")
    az = BaziAnalyzer(sz)

    result = az.to_dict()
    assert "神煞" in result, "to_dict 应包含 神煞 字段"
    assert "天乙贵人" in result["神煞"]
    assert "文昌贵人" in result["神煞"]
    assert "太极贵人" in result["神煞"]
    assert "学堂词馆" in result["神煞"]

    print("✅ test_to_dict_with_shensha: to_dict 包含神煞数据")


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
