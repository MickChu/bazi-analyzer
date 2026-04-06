#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
子平命理规则引擎 - 独立模块
包含所有命理计算与分析逻辑，不依赖任何外部服务或API

可被任何程序 import 使用：
    from bazi_engine import BaziCalculator, BaziAnalyzer, get_shishen
"""

from datetime import datetime

# ============================================================
# 基础数据定义
# ============================================================

# 天干
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干五行
TIANGAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水"
}

# 天干阴阳
TIANGAN_YINYANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴",
    "戊": "阳", "己": "阴", "庚": "阳", "辛": "阴",
    "壬": "阳", "癸": "阴"
}

# 地支五行
DIZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 地支藏干
DIZHI_CANGGAN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
}

# 地支六合
LIUHE = [("子", "丑"), ("寅", "亥"), ("卯", "戌"), ("辰", "酉"), ("巳", "申"), ("午", "未")]

# 地支六冲
LIUCHONG = [("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]

# 地支三合
SANHE = {
    "水": ["申", "子", "辰"], "木": ["亥", "卯", "未"],
    "火": ["寅", "午", "戌"], "金": ["巳", "酉", "丑"]
}

# 地支三会
SANHUI = {
    "水": ["亥", "子", "丑"], "木": ["寅", "卯", "辰"],
    "火": ["巳", "午", "未"], "金": ["申", "酉", "戌"]
}

# 五行生克关系
SHENG_WO = {"水": "金", "木": "水", "火": "木", "土": "火", "金": "土"}   # 生我者
WO_SHENG = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}   # 我生者
KE_WO = {"金": "火", "水": "土", "木": "金", "火": "水", "土": "木"}     # 克我者
WO_KE = {"火": "金", "土": "水", "金": "木", "水": "火", "木": "土"}     # 我克者


# ============================================================
# 十神计算
# ============================================================

def get_shishen(day_gan, target_gan):
    """
    计算十神关系（以日干为中心）

    Args:
        day_gan: 日干天干
        target_gan: 目标天干

    Returns:
        str: 十神名称（比肩/劫财/食神/伤官/偏财/正财/七杀/正官/偏印/正印）
    """
    day_wx = TIANGAN_WUXING[day_gan]
    day_yy = TIANGAN_YINYANG[day_gan]
    target_wx = TIANGAN_WUXING[target_gan]
    target_yy = TIANGAN_YINYANG[target_gan]
    same_yy = (day_yy == target_yy)

    if target_wx == SHENG_WO[day_wx]:
        return "正印" if same_yy else "偏印"
    elif target_wx == WO_SHENG[day_wx]:
        return "伤官" if same_yy else "食神"
    elif target_wx == KE_WO[day_wx]:
        return "七杀" if same_yy else "正官"
    elif target_wx == WO_KE[day_wx]:
        return "偏财" if same_yy else "正财"
    else:
        return "比肩" if same_yy else "劫财"


# ============================================================
# 四柱排盘计算器
# ============================================================

class BaziCalculator:
    """八字排盘计算器，支持从公历日期计算四柱、大运"""

    BASE_YEAR = 1984  # 甲子年

    # --- 年柱 ---
    def get_year_ganzhi(self, year):
        """计算年柱干支"""
        offset = (year - self.BASE_YEAR) % 60
        return TIANGAN[offset % 10] + DIZHI[offset % 12]

    # --- 月柱（五虎遁） ---
    def get_month_ganzhi(self, year_gan, yuejian):
        """
        计算月柱干支

        Args:
            year_gan: 年干（如 '甲'）
            yuejian: 月建地支（如 '寅'）
        """
        _WUHU = {
            "甲": "丙", "己": "丙", "乙": "戊", "庚": "戊",
            "丙": "庚", "辛": "庚", "丁": "壬", "壬": "壬",
            "戊": "甲", "癸": "甲"
        }
        start_idx = TIANGAN.index(_WUHU[year_gan])
        yuejian_idx = DIZHI.index(yuejian)
        gan_idx = (start_idx + (yuejian_idx - 2)) % 10
        return TIANGAN[gan_idx] + yuejian

    # --- 日柱 ---
    def get_day_ganzhi(self, year, month, day):
        """
        计算日柱干支
        基准日：1900-01-31 = 甲子日
        """
        base = datetime(1900, 1, 31)
        diff = (datetime(year, month, day) - base).days
        offset = diff % 60
        return TIANGAN[offset % 10] + DIZHI[offset % 12]

    # --- 时柱（五鼠遁） ---
    def get_hour_ganzhi(self, day_gan, hour):
        """
        计算时柱干支

        Args:
            day_gan: 日柱干支（如 '甲子'）
            hour: 小时（0-23）
        """
        _WUSHU = {
            "甲": "甲", "己": "甲", "乙": "丙", "庚": "丙",
            "丙": "戊", "辛": "戊", "丁": "庚", "壬": "庚",
            "戊": "壬", "癸": "壬"
        }
        ri_gan = day_gan[0]
        start_idx = TIANGAN.index(_WUSHU[ri_gan])

        if hour == 23 or hour == 0:
            shi_zhi = "子"
        else:
            shi_zhi = DIZHI[((hour + 1) // 2) % 12]

        gan_idx = (start_idx + DIZHI.index(shi_zhi)) % 10
        return TIANGAN[gan_idx] + shi_zhi

    # --- 月建 ---
    def determine_yuejian(self, year, month, day):
        """
        确定月建（按节气简化近似）
        注意：精确节气需天文算法，此为近似值
        """
        _JIEQI_DAY = {
            1: 4, 2: 4, 3: 5, 4: 5, 5: 5, 6: 6,
            7: 7, 8: 7, 9: 7, 10: 8, 11: 7, 12: 6
        }
        _YUEJIAN_BEFORE = {
            1: "丑", 2: "寅", 3: "卯", 4: "辰",
            5: "巳", 6: "午", 7: "未", 8: "申",
            9: "酉", 10: "戌", 11: "亥", 12: "子"
        }
        _YUEJIAN_AFTER = {
            1: "寅", 2: "卯", 3: "辰", 4: "巳",
            5: "午", 6: "未", 7: "申", 8: "酉",
            9: "戌", 10: "亥", 11: "子", 12: "丑"
        }
        if day >= _JIEQI_DAY.get(month, 4):
            return _YUEJIAN_AFTER[month]
        else:
            return _YUEJIAN_BEFORE[month]

    # --- 大运 ---
    def calculate_dayun(self, year_gan, month_gan, month_zhi, gender, birth_year, count=8):
        """
        计算大运

        Args:
            year_gan: 年干
            month_gan: 月干
            month_zhi: 月支
            gender: '男' 或 '女'
            birth_year: 出生年份（用于计算起运年龄）
            count: 大运步数，默认8步
        """
        year_yang = TIANGAN_YINYANG[year_gan] == "阳"
        is_male = gender == "男"
        forward = (year_yang and is_male) or (not year_yang and not is_male)

        g_idx = TIANGAN.index(month_gan)
        z_idx = DIZHI.index(month_zhi)
        dayun = []

        for i in range(count):
            step = i + 1
            if forward:
                gi = (g_idx + step) % 10
                zi = (z_idx + step) % 12
            else:
                gi = (g_idx - step) % 10
                zi = (z_idx - step) % 10

            start_age = 3 + i * 10  # 简化：实际应按距月令节气天数计算
            dayun.append({
                "ganzhi": TIANGAN[gi] + DIZHI[zi],
                "start_age": start_age,
                "end_age": start_age + 9,
            })

        return dayun, forward

    # --- 完整排盘 ---
    def calculate_sizhu(self, year, month, day, hour, gender):
        """
        从公历日期计算完整四柱命盘

        Args:
            year: 出生年
            month: 出生月（1-12）
            day: 出生日
            hour: 出生时（0-23）
            gender: '男' 或 '女'

        Returns:
            dict: 完整命盘数据
        """
        year_gz = self.get_year_ganzhi(year)
        yuejian = self.determine_yuejian(year, month, day)
        month_gz = self.get_month_ganzhi(year_gz[0], yuejian)
        day_gz = self.get_day_ganzhi(year, month, day)
        hour_gz = self.get_hour_ganzhi(day_gz, hour)

        dayun, forward = self.calculate_dayun(
            year_gz[0], month_gz[0], month_gz[1], gender, year
        )

        return {
            "year": year_gz,
            "month": month_gz,
            "day": day_gz,
            "hour": hour_gz,
            "yuejian": yuejian,
            "dayun": dayun,
            "dayun_direction": "顺排" if forward else "逆排",
        }


# ============================================================
# 命局分析器
# ============================================================

class BaziAnalyzer:
    """
    命局分析器，提供旺衰、格局、喜用神、性格等分析

    Usage:
        calc = BaziCalculator()
        sizhu = calc.calculate_sizhu(1990, 6, 15, 12, "男")
        analyzer = BaziAnalyzer(sizhu)
        ws = analyzer.analyze_wangshuai()
        xy = analyzer.determine_xiyong(ws)
    """

    def __init__(self, sizhu_data):
        """
        Args:
            sizhu_data: BaziCalculator.calculate_sizhu() 的返回值，
                        或包含 year/month/day/hour/yuejian/dayun 的字典
        """
        self.data = sizhu_data
        self.day_gan = sizhu_data["day"][0]
        self.day_zhi = sizhu_data["day"][1]

    # --- 五行分布 ---
    def get_wuxing_distribution(self):
        """统计命局五行分布（仅天干+地支本气，各8个位置）"""
        dist = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        for gz in [self.data["year"], self.data["month"], self.data["day"], self.data["hour"]]:
            dist[TIANGAN_WUXING[gz[0]]] += 1
            dist[DIZHI_WUXING[gz[1]]] += 1
        return dist

    # --- 十神分布 ---
    def get_shishen_distribution(self):
        """统计十神分布（含地支藏干）"""
        dist = {}
        all_gans = [self.data["year"][0], self.data["month"][0],
                    self.data["day"][0], self.data["hour"][0]]
        for zhi in [self.data["year"][1], self.data["month"][1],
                    self.data["day"][1], self.data["hour"][1]]:
            all_gans.extend(DIZHI_CANGGAN[zhi])
        for gan in all_gans:
            ss = get_shishen(self.day_gan, gan)
            dist[ss] = dist.get(ss, 0) + 1
        return dist

    # --- 旺衰分析 ---
    def analyze_wangshuai(self):
        """
        日主旺衰判断（得令、得地、得势三维评分）

        Returns:
            dict: {score, result, details}
                score: 0-100+ 的旺衰评分
                result: "身强"/"中和偏强"/"中和偏弱"/"身弱"
                details: 评分明细列表
        """
        score = 0
        details = []
        day_wx = TIANGAN_WUXING[self.day_gan]
        yuejian_wx = DIZHI_WUXING[self.data["yuejian"]]

        # 1. 得令（月令）
        if yuejian_wx == day_wx:
            score += 30
            details.append(f"得令：月令{yuejian_wx}与日主同气，+30")
        elif yuejian_wx == SHENG_WO[day_wx]:
            score += 20
            details.append(f"得令：月令{yuejian_wx}生助日主，+20")
        else:
            details.append(f"不得令：月令{yuejian_wx}不助日主")

        # 2. 得地（地支藏干根气）
        for zhi in [self.data["year"][1], self.data["month"][1],
                    self.data["day"][1], self.data["hour"][1]]:
            for gan in DIZHI_CANGGAN[zhi]:
                if gan == self.day_gan:
                    score += 15
                    details.append(f"得地：{zhi}藏干含日主{self.day_gan}，+15")
                elif TIANGAN_WUXING[gan] == day_wx:
                    score += 8
                    details.append(f"得地：{zhi}藏干含同五行{gan}，+8")

        # 3. 得势（天干比劫）
        for gz in [self.data["year"], self.data["month"], self.data["hour"]]:
            if gz[0] == self.day_gan:
                score += 10
                details.append(f"得势：天干{gz[0]}即日主，+10")
            elif TIANGAN_WUXING[gz[0]] == day_wx:
                score += 5
                details.append(f"得势：天干{gz[0]}同五行，+5")

        if score >= 50:
            result = "身强"
        elif score >= 35:
            result = "中和偏强"
        elif score >= 25:
            result = "中和偏弱"
        else:
            result = "身弱"

        return {"score": score, "result": result, "details": details}

    # --- 喜用神 ---
    def determine_xiyong(self, wangshuai):
        """
        根据旺衰确定喜用神

        Args:
            wangshuai: analyze_wangshuai() 的返回值

        Returns:
            dict: {xishen: [...], jishen: [...], strategy: str}
        """
        day_wx = TIANGAN_WUXING[self.day_gan]

        if "身强" in wangshuai["result"]:
            xishen = [WO_KE[day_wx], WO_SHENG[day_wx], KE_WO[day_wx]]
            jishen = [SHENG_WO[day_wx], day_wx]
            strategy = "宜克泄耗，忌生扶"
        else:
            xishen = [SHENG_WO[day_wx], day_wx]
            jishen = [WO_KE[day_wx], WO_SHENG[day_wx], KE_WO[day_wx]]
            strategy = "宜生扶，忌克泄耗"

        return {"xishen": xishen, "jishen": jishen, "strategy": strategy}

    # --- 格局分析 ---
    def analyze_geju(self):
        """
        格局判断（月令透干 + 特殊组合检测）

        Returns:
            list[str]: 格局描述列表
        """
        geju = []
        yuejian = self.data["yuejian"]
        ss_dist = self.get_shishen_distribution()

        # 月令本气透干
        benqi = DIZHI_CANGGAN[yuejian][0]
        for gz in [self.data["year"], self.data["month"], self.data["day"], self.data["hour"]]:
            if gz[0] == benqi:
                ss = get_shishen(self.day_gan, gz[0])
                geju.append(f"月令{yuejian}本气{benqi}透出，可成{ss}格")

        # 特殊组合
        if ss_dist.get("伤官", 0) > 0 and ss_dist.get("正官", 0) > 0:
            geju.append("伤官见官组合，事业易有波折")
        if ss_dist.get("七杀", 0) > 0 and ss_dist.get("正印", 0) > 0:
            geju.append("杀印相生组合，有贵气")
        if ss_dist.get("正财", 0) > 0 and ss_dist.get("正官", 0) > 0:
            geju.append("财官相生组合，利于仕途")

        return geju or ["格局普通，以常规分析为主"]

    # --- 性格分析 ---
    def analyze_xingge(self, wangshuai, xiyong):
        """
        核心性格断语（日主五行 + 身强身弱）

        Returns:
            dict: {base: {优点, 缺点}, tendency: str}
        """
        day_wx = TIANGAN_WUXING[self.day_gan]
        _XINGGE = {
            "木": {"优点": "仁慈正直，有进取心", "缺点": "固执己见，不善变通"},
            "火": {"优点": "热情开朗，富有感染力", "缺点": "急躁冲动，缺乏耐心"},
            "土": {"优点": "诚实守信，稳重踏实", "缺点": "保守固执，反应较慢"},
            "金": {"优点": "果断刚毅，讲义气", "缺点": "过于严苛，不善妥协"},
            "水": {"优点": "聪明灵活，善于应变", "缺点": "多变不定，缺乏定力"},
        }
        base = _XINGGE.get(day_wx, {"优点": "性格平和", "缺点": "无明显特征"})
        tendency = ("自我意识强，独立性强，但易刚愎自用"
                    if "身强" in wangshuai["result"]
                    else "性格随和，善于配合，但易优柔寡断")
        return {"base": base, "tendency": tendency}

    # --- 大运分析 ---
    def analyze_dayun(self, current_age=30):
        """
        大运走势分析

        Args:
            current_age: 当前年龄

        Returns:
            list[dict]: 每步大运的详情
        """
        result = []
        for dy in self.data.get("dayun", []):
            if dy["start_age"] <= current_age <= dy["end_age"]:
                status = "当前大运"
            elif dy["start_age"] > current_age:
                status = "未来大运"
            else:
                status = "已过大运"

            gan_wx = TIANGAN_WUXING[dy["ganzhi"][0]]
            zhi_wx = DIZHI_WUXING[dy["ganzhi"][1]]

            result.append({
                "ganzhi": dy["ganzhi"],
                "age_range": f"{dy['start_age']}-{dy['end_age']}岁",
                "status": status,
                "wuxing": f"{gan_wx}+{zhi_wx}",
            })
        return result

    # --- 命局层次断语 ---
    def get_summary_verdict(self, wangshuai):
        """生成命局层次一句话断语"""
        ss = self.get_shishen_distribution()
        duanyu_parts = []

        if "身强" in wangshuai["result"]:
            if ss.get("正财", 0) + ss.get("偏财", 0) <= 1:
                duanyu_parts.append("身强财弱，劳碌求财之命")
            elif ss.get("七杀", 0) > 0 and ss.get("正印", 0) > 0:
                duanyu_parts.append("杀印相生，中上格局")
            else:
                duanyu_parts.append("身强有力，宜担当重任")
        else:
            if ss.get("正印", 0) + ss.get("偏印", 0) >= 2:
                duanyu_parts.append("身弱印旺，需贵人扶持")
            else:
                duanyu_parts.append("身弱需扶，宜借力发展")

        if ss.get("伤官", 0) > 0 and ss.get("正官", 0) > 0:
            duanyu_parts.append("伤官见官，事业多波折")

        return "；".join(duanyu_parts)

    # --- 建议类 ---
    def get_career_advice(self, xiyong):
        """基于喜用神的行业建议"""
        _HANGYE = {
            "木": "教育、文化、出版、林业、服装、纺织",
            "火": "能源、电力、餐饮、娱乐、传媒、互联网",
            "土": "房地产、建筑、农业、矿产、仓储、管理",
            "金": "金融、银行、机械、五金、汽车、法律",
            "水": "物流、贸易、旅游、水利、饮料、咨询",
        }
        return "、".join(_HANGYE.get(wx, "") for wx in xiyong["xishen"])

    def get_fangwei_advice(self, xiyong):
        """基于喜用神的方位建议"""
        _FANGWEI = {
            "木": "东方", "火": "南方", "土": "中央/本地",
            "金": "西方", "水": "北方",
        }
        return "、".join(_FANGWEI.get(wx, "") for wx in xiyong["xishen"])
