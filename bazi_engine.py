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

    # --- 胎元 ---
    def get_taiyuan(self, month_ganzhi):
        """
        计算胎元（受胎月份的干支）

        依据：《渊海子平》胎元起法
        胎元 = 月干顺推一位 + 月支顺推三位
        例：月柱甲子 → 胎元乙卯（甲+1=乙，子+3=卯）

        Args:
            month_ganzhi: 月柱干支（如 '甲子'），2字符

        Returns:
            str: 胎元干支（如 '乙卯'）
        """
        gan_idx = TIANGAN.index(month_ganzhi[0])
        zhi_idx = DIZHI.index(month_ganzhi[1])
        return TIANGAN[(gan_idx + 1) % 10] + DIZHI[(zhi_idx + 3) % 12]

    # --- 命宫 ---
    def get_minggong(self, month_ganzhi, hour_ganzhi):
        """
        计算命宫地支

        依据：《渊海子平》《三命通会》命宫起法
        命宫 = 以月支起子时，逆数至生时，所至之支即命宫

        Args:
            month_ganzhi: 月柱干支（如 '甲子'）
            hour_ganzhi: 时柱干支（如 '丙子'）

        Returns:
            str: 命宫地支（如 '子'）
        """
        month_idx = DIZHI.index(month_ganzhi[1])
        hour_idx = DIZHI.index(hour_ganzhi[1])
        return DIZHI[(month_idx - hour_idx) % 12]

    # --- 身宫 ---
    def get_shengong(self, month_ganzhi, hour_ganzhi):
        """
        计算身宫地支

        依据：《三命通会》身宫起法
        身宫 = 以月支起子时，顺数至生时，所至之支即身宫
        （与命宫相对：命宫逆数、身宫顺数）

        Args:
            month_ganzhi: 月柱干支（如 '甲子'）
            hour_ganzhi: 时柱干支（如 '丙子'）

        Returns:
            str: 身宫地支（如 '子'）
        """
        month_idx = DIZHI.index(month_ganzhi[1])
        hour_idx = DIZHI.index(hour_ganzhi[1])
        return DIZHI[(month_idx + hour_idx) % 12]

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


# ============================================================
# 神煞计算器
# ============================================================

class ShenshaCalculator:
    """
    神煞计算器，负责查算八字常用吉神

    依据：《渊海子平》《三命通会》神煞章节
    """

    # 天乙贵人表：日干/年干 → 贵人地支对
    # 口诀：甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，
    #       壬癸兔蛇藏，六辛逢虎马，此是贵人方
    _TIANYI = {
        "甲": ["丑", "未"], "乙": ["子", "申"],
        "丙": ["亥", "酉"], "丁": ["亥", "酉"],
        "戊": ["丑", "未"], "己": ["子", "申"],
        "庚": ["丑", "未"], "辛": ["寅", "午"],
        "壬": ["卯", "巳"], "癸": ["卯", "巳"],
    }

    # 文昌贵人表：日干 → 文昌所在地支
    # 口诀：甲乙巳午报君知，丙戊申宫丁己鸡，
    #       庚猪辛鼠壬逢虎，癸人见卯入云梯
    _WENCHANG = {
        "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
        "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
        "壬": "寅", "癸": "卯",
    }

    # 太极贵人表：日干/年干 → 太极所在地支
    # 口诀：甲乙子午，丙丁卯酉，戊己四季辰戌丑未，
    #       庚辛寅亥，壬癸巳申
    _TAIJI = {
        "甲": ["子", "午"], "乙": ["子", "午"],
        "丙": ["卯", "酉"], "丁": ["卯", "酉"],
        "戊": ["辰", "戌", "丑", "未"], "己": ["辰", "戌", "丑", "未"],
        "庚": ["寅", "亥"], "辛": ["寅", "亥"],
        "壬": ["巳", "申"], "癸": ["巳", "申"],
    }

    # 学堂表：日干 → 长生位地支
    # 甲亥、乙午、丙寅、丁酉、戊寅、己酉、庚巳、辛子、壬申、癸卯
    _XUETANG = {
        "甲": "亥", "乙": "午", "丙": "寅", "丁": "酉",
        "戊": "寅", "己": "酉", "庚": "巳", "辛": "子",
        "壬": "申", "癸": "卯",
    }

    # 词馆表：日干 → 临官位地支
    # 甲寅、乙卯、丙巳、丁午、戊巳、己午、庚申、辛酉、壬亥、癸子
    _CIGUAN = {
        "甲": "寅", "乙": "卯", "丙": "巳", "丁": "午",
        "戊": "巳", "己": "午", "庚": "申", "辛": "酉",
        "壬": "亥", "癸": "子",
    }

    def __init__(self, sizhu_data):
        """
        Args:
            sizhu_data: BaziCalculator.calculate_sizhu() 返回值，
                        需包含 year/month/day/hour 四柱干支
        """
        self.data = sizhu_data
        self.year_gan = sizhu_data["year"][0]
        self.year_zhi = sizhu_data["year"][1]
        self.month_zhi = sizhu_data["month"][1]
        self.day_gan = sizhu_data["day"][0]
        self.day_zhi = sizhu_data["day"][1]
        self.hour_zhi = sizhu_data["hour"][1]

        # 四柱所有地支
        self.all_zhi = [
            self.year_zhi, self.month_zhi,
            self.day_zhi, self.hour_zhi,
        ]

    def tianyi_guiren(self, day_gan=None, year_gan=None):
        """
        天乙贵人 — 日干/年干双查

        天乙贵人为命中最吉之神，主遇难呈祥、贵人扶助。
        以日干为主，年干为辅，查四柱地支是否出现贵人。

        Args:
            day_gan: 日干（默认使用实例 day_gan）
            year_gan: 年干（默认使用实例 year_gan）

        Returns:
            dict: {
                "日干查": [贵人所在的四柱位置列表],
                "年干查": [贵人所在的四柱位置列表],
                "贵人地支": list[str],
                "所在柱位": list[str],
            }
        """
        day_gan = day_gan or self.day_gan
        year_gan = year_gan or self.year_gan

        result = {"日干查": [], "年干查": [], "贵人地支": set(), "所在柱位": []}

        # 日干查
        guiren_zhi = self._TIANYI.get(day_gan, [])
        for gz in guiren_zhi:
            result["贵人地支"].add(gz)
        
        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi in guiren_zhi:
                result["日干查"].append(f"{label}支/{zhi}")
                result["所在柱位"].append(label)

        # 年干查
        guiren_zhi_yr = self._TIANYI.get(year_gan, [])
        for gz in guiren_zhi_yr:
            result["贵人地支"].add(gz)

        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi in guiren_zhi_yr and f"{label}支/{zhi}" not in result["日干查"]:
                result["年干查"].append(f"{label}支/{zhi}")
                if label not in result["所在柱位"]:
                    result["所在柱位"].append(label)

        result["贵人地支"] = sorted(result["贵人地支"])
        return result

    def wenchang_xueren(self, day_gan=None):
        """
        文昌贵人 — 日干查地支

        文昌贵人主聪明好学、文采出众、考试运佳。
        以日干查四柱地支是否出现文昌。

        Args:
            day_gan: 日干（默认使用实例 day_gan）

        Returns:
            dict: {
                "文昌地支": str,
                "所在柱位": list[str] | None,
                "有文昌": bool,
            }
        """
        day_gan = day_gan or self.day_gan
        wenchang_zhi = self._WENCHANG.get(day_gan, "")

        positions = []
        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi == wenchang_zhi:
                positions.append(label)

        return {
            "文昌地支": wenchang_zhi,
            "所在柱位": positions or None,
            "有文昌": len(positions) > 0,
        }

    def taiji_guiren(self, day_gan=None, year_gan=None):
        """
        太极贵人 — 日干/年干双查

        太极贵人主聪明好学、喜神秘文化、有特殊才能。
        以日干为主，年干为辅，查四柱地支是否出现。

        Args:
            day_gan: 日干（默认使用实例 day_gan）
            year_gan: 年干（默认使用实例 year_gan）

        Returns:
            dict: 与 tianyi_guiren 结构相同
        """
        day_gan = day_gan or self.day_gan
        year_gan = year_gan or self.year_gan

        result = {"日干查": [], "年干查": [], "贵人地支": set(), "所在柱位": []}

        taiji_zhi = self._TAIJI.get(day_gan, [])
        for gz in taiji_zhi:
            result["贵人地支"].add(gz)

        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi in taiji_zhi:
                result["日干查"].append(f"{label}支/{zhi}")
                result["所在柱位"].append(label)

        taiji_zhi_yr = self._TAIJI.get(year_gan, [])
        for gz in taiji_zhi_yr:
            result["贵人地支"].add(gz)

        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi in taiji_zhi_yr and f"{label}支/{zhi}" not in result["日干查"]:
                result["年干查"].append(f"{label}支/{zhi}")
                if label not in result["所在柱位"]:
                    result["所在柱位"].append(label)

        result["贵人地支"] = sorted(result["贵人地支"])
        return result

    def xuetang_ciguan(self, day_gan=None):
        """
        学堂词馆 — 日干查地支

        学堂词馆主学业有成、科甲功名、聪明俊秀。
        学堂在长生位，词馆在临官位。

        Args:
            day_gan: 日干（默认使用实例 day_gan）

        Returns:
            dict: {
                "学堂": {"所在地支": str, "所在柱位": list | None, "有学堂": bool},
                "词馆": {"所在地支": str, "所在柱位": list | None, "有词馆": bool},
            }
        """
        day_gan = day_gan or self.day_gan

        xuetang_zhi = self._XUETANG.get(day_gan, "")
        ciguan_zhi = self._CIGUAN.get(day_gan, "")

        xt_positions = []
        cg_positions = []

        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi == xuetang_zhi:
                xt_positions.append(label)
            if zhi == ciguan_zhi:
                cg_positions.append(label)

        return {
            "学堂": {
                "所在地支": xuetang_zhi,
                "所在柱位": xt_positions or None,
                "有学堂": len(xt_positions) > 0,
            },
            "词馆": {
                "所在地支": ciguan_zhi,
                "所在柱位": cg_positions or None,
                "有词馆": len(cg_positions) > 0,
            },
        }

    # --- 三合局辅助 ---
    @staticmethod
    def _get_sanhe_ju(zhi):
        """
        根据地支返回所在三合局

        申子辰(水)、寅午戌(火)、亥卯未(木)、巳酉丑(金)
        返回 (局名, 局中地支列表)
        """
        for ju_name, ju_zhi in [("申子辰水局", ["申", "子", "辰"]),
                                ("寅午戌火局", ["寅", "午", "戌"]),
                                ("亥卯未木局", ["亥", "卯", "未"]),
                                ("巳酉丑金局", ["巳", "酉", "丑"])]:
            if zhi in ju_zhi:
                return ju_name, ju_zhi
        return None, []

    @staticmethod
    def _get_sanhui_ju(zhi):
        """
        根据地支返回所在三会局（季节局）

        寅卯辰(春木)、巳午未(夏火)、申酉戌(秋金)、亥子丑(冬水)
        返回 (局名, 局中地支列表)
        """
        for ju_name, ju_zhi in [("寅卯辰木局", ["寅", "卯", "辰"]),
                                ("巳午未火局", ["巳", "午", "未"]),
                                ("申酉戌金局", ["申", "酉", "戌"]),
                                ("亥子丑水局", ["亥", "子", "丑"])]:
            if zhi in ju_zhi:
                return ju_name, ju_zhi
        return None, []

    # --- 桃花/咸池 ---
    # 口诀：申子辰在酉，寅午戌在卯，亥卯未在子，巳酉丑在午
    _TAOHUA = {
        "申": "酉", "子": "酉", "辰": "酉",
        "寅": "卯", "午": "卯", "戌": "卯",
        "亥": "子", "卯": "子", "未": "子",
        "巳": "午", "酉": "午", "丑": "午",
    }

    def taohua(self, day_zhi=None, year_zhi=None):
        """
        桃花/咸池 — 日支+年支双查

        桃花主异性缘、人缘、艺术天赋，亦含情欲纠纷。
        在时柱为墙外桃花，主晚年异性缘重。

        Args:
            day_zhi: 日支（默认使用实例 day_zhi）
            year_zhi: 年支（默认使用实例 year_zhi）

        Returns:
            dict: {
                "日支查": list[str],
                "年支查": list[str],
                "桃花地支": str,
                "所在柱位": list[str],  # 日/时支为"墙内桃花"，年/月支为"墙外桃花"
                "桃花类型": str,  # "墙内桃花"或"墙外桃花"或"无"
            }
        """
        day_zhi = day_zhi or self.day_zhi
        year_zhi = year_zhi or self.year_zhi

        result = {"日支查": [], "年支查": [], "桃花地支": None, "所在柱位": [], "桃花类型": "无"}

        # 日支查桃花位
        taohua_zhi = self._TAOHUA.get(day_zhi)
        if taohua_zhi:
            result["桃花地支"] = taohua_zhi
            for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                               ("日", self.day_zhi), ("时", self.hour_zhi)]:
                if zhi == taohua_zhi:
                    result["日支查"].append(f"{label}支/{zhi}")
                    result["所在柱位"].append(label)

        # 年支查（若与日支桃花不同位，也标记）
        taohua_zhi_yr = self._TAOHUA.get(year_zhi)
        if taohua_zhi_yr and taohua_zhi_yr != taohua_zhi:
            for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                               ("日", self.day_zhi), ("时", self.hour_zhi)]:
                if zhi == taohua_zhi_yr:
                    result["年支查"].append(f"{label}支/{zhi}")
                    if label not in result["所在柱位"]:
                        result["所在柱位"].append(label)

        # 判断桃花类型
        if result["所在柱位"]:
            if "日" in result["所在柱位"] or "时" in result["所在柱位"]:
                result["桃花类型"] = "墙内桃花"
            else:
                result["桃花类型"] = "墙外桃花"

        return result

    # --- 羊刃 ---
    # 阳干帝旺位为羊刃，阴干以墓库位论
    # 口诀：甲刃在卯，丙戊刃在午，庚刃在酉，壬刃在子
    # 阴干：乙刃在辰，丁己刃在未，辛刃在戌，癸刃在丑
    _YANGREN = {
        "甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子",
        "乙": "辰", "丁": "未", "己": "未", "辛": "戌", "癸": "丑",
    }

    def yangren(self, day_gan=None):
        """
        羊刃 — 日干查地支

        羊刃为旺极之刃，阳干帝旺位、阴干墓库位。
        羊刃主性格刚强、果断，但易冲动、克父克妻。
        有制化者可掌兵权、为将星。

        Args:
            day_gan: 日干（默认使用实例 day_gan）

        Returns:
            dict: {
                "羊刃地支": str,
                "天干阴阳": str,
                "所在柱位": list[str] | None,
                "有羊刃": bool,
            }
        """
        day_gan = day_gan or self.day_gan
        yangren_zhi = self._YANGREN.get(day_gan, "")

        positions = []
        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi == yangren_zhi:
                positions.append(label)

        gan_yy = TIANGAN_YINYANG.get(day_gan, "?")

        return {
            "羊刃地支": yangren_zhi,
            "天干阴阳": gan_yy,
            "所在柱位": positions or None,
            "有羊刃": len(positions) > 0,
            "备注": f"{day_gan}为{gan_yy}干，羊刃在{yangren_zhi}" + (
                "（帝旺位）" if gan_yy == "阳" else "（墓库位）"
            ),
        }

    # --- 驿马 ---
    # 口诀：申子辰在寅，寅午戌在申，亥卯未在巳，巳酉丑在亥
    _YIMA = {
        "申": "寅", "子": "寅", "辰": "寅",
        "寅": "申", "午": "申", "戌": "申",
        "亥": "巳", "卯": "巳", "未": "巳",
        "巳": "亥", "酉": "亥", "丑": "亥",
    }

    def yima(self, day_zhi=None, year_zhi=None):
        """
        驿马 — 日支+年支双查

        驿马主动、奔波、迁移、出国。
        命带驿马者一生多动，适合外出发展。
        驿马逢冲则动得更急，逢合则动而有所牵制。

        Args:
            day_zhi: 日支（默认使用实例 day_zhi）
            year_zhi: 年支（默认使用实例 year_zhi）

        Returns:
            dict: {
                "日支查": list[str],
                "年支查": list[str],
                "驿马地支": str,
                "所在柱位": list[str],
            }
        """
        day_zhi = day_zhi or self.day_zhi
        year_zhi = year_zhi or self.year_zhi

        result = {"日支查": [], "年支查": [], "驿马地支": None, "所在柱位": []}

        yima_zhi = self._YIMA.get(day_zhi)
        if yima_zhi:
            result["驿马地支"] = yima_zhi
            for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                               ("日", self.day_zhi), ("时", self.hour_zhi)]:
                if zhi == yima_zhi:
                    result["日支查"].append(f"{label}支/{zhi}")
                    result["所在柱位"].append(label)

        yima_zhi_yr = self._YIMA.get(year_zhi)
        if yima_zhi_yr and yima_zhi_yr != yima_zhi:
            for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                               ("日", self.day_zhi), ("时", self.hour_zhi)]:
                if zhi == yima_zhi_yr:
                    result["年支查"].append(f"{label}支/{zhi}")
                    if label not in result["所在柱位"]:
                        result["所在柱位"].append(label)

        return result

    # --- 华盖 ---
    # 口诀：申子辰见辰，寅午戌见戌，亥卯未见未，巳酉丑见丑
    _HUAGAI = {
        "申": "辰", "子": "辰", "辰": "辰",
        "寅": "戌", "午": "戌", "戌": "戌",
        "亥": "未", "卯": "未", "未": "未",
        "巳": "丑", "酉": "丑", "丑": "丑",
    }

    def huagai(self, day_zhi=None):
        """
        华盖 — 日支查地支

        华盖主孤独、清高、聪明、喜神秘文化。
        命带华盖者对哲学、宗教、命理、艺术有天赋。
        华盖过多则孤芳自赏，不利婚姻。

        Args:
            day_zhi: 日支（默认使用实例 day_zhi）

        Returns:
            dict: {
                "华盖地支": str,
                "所在柱位": list[str] | None,
                "有华盖": bool,
            }
        """
        day_zhi = day_zhi or self.day_zhi
        huagai_zhi = self._HUAGAI.get(day_zhi, "")

        positions = []
        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi == huagai_zhi:
                positions.append(label)

        return {
            "华盖地支": huagai_zhi,
            "所在柱位": positions or None,
            "有华盖": len(positions) > 0,
        }

    # --- 将星 ---
    # 口诀：申子辰见子，寅午戌见午，亥卯未见卯，巳酉丑见酉
    _JIANGXING = {
        "申": "子", "子": "子", "辰": "子",
        "寅": "午", "午": "午", "戌": "午",
        "亥": "卯", "卯": "卯", "未": "卯",
        "巳": "酉", "酉": "酉", "丑": "酉",
    }

    def jiangxing(self, day_zhi=None):
        """
        将星 — 日支查地支

        将星主领导力、决断力、统御才能。
        命带将星者适合管理岗位、军警、体育竞技。
        将星配合吉神则权重威显，配合凶煞则暴戾。

        Args:
            day_zhi: 日支（默认使用实例 day_zhi）

        Returns:
            dict: {
                "将星地支": str,
                "所在柱位": list[str] | None,
                "有将星": bool,
            }
        """
        day_zhi = day_zhi or self.day_zhi
        jiangxing_zhi = self._JIANGXING.get(day_zhi, "")

        positions = []
        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi == jiangxing_zhi:
                positions.append(label)

        return {
            "将星地支": jiangxing_zhi,
            "所在柱位": positions or None,
            "有将星": len(positions) > 0,
        }

    # --- 孤辰寡宿 ---
    # 孤辰：亥子丑见寅，寅卯辰见巳，巳午未见申，申酉戌见亥
    # 寡宿：亥子丑见戌，寅卯辰见丑，巳午未见辰，申酉戌见未
    _GUCHEN = {
        "亥": "寅", "子": "寅", "丑": "寅",
        "寅": "巳", "卯": "巳", "辰": "巳",
        "巳": "申", "午": "申", "未": "申",
        "申": "亥", "酉": "亥", "戌": "亥",
    }
    _GUASU = {
        "亥": "戌", "子": "戌", "丑": "戌",
        "寅": "丑", "卯": "丑", "辰": "丑",
        "巳": "辰", "午": "辰", "未": "辰",
        "申": "未", "酉": "未", "戌": "未",
    }

    def guchen_guasu(self, day_zhi=None):
        """
        孤辰寡宿 — 日支查地支

        孤辰主孤僻、寡合、与六亲缘浅。
        寡宿主孤独、配偶缘薄。
        男怕孤辰，女怕寡宿，但配合华盖则利于修行学术。

        Args:
            day_zhi: 日支（默认使用实例 day_zhi）

        Returns:
            dict: {
                "孤辰": {"地支": str, "所在柱位": list | None, "有孤辰": bool},
                "寡宿": {"地支": str, "所在柱位": list | None, "有寡宿": bool},
            }
        """
        day_zhi = day_zhi or self.day_zhi

        guchen_zhi = self._GUCHEN.get(day_zhi, "")
        guasu_zhi = self._GUASU.get(day_zhi, "")

        gc_positions = []
        gs_positions = []

        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi == guchen_zhi:
                gc_positions.append(label)
            if zhi == guasu_zhi:
                gs_positions.append(label)

        return {
            "孤辰": {
                "地支": guchen_zhi,
                "所在柱位": gc_positions or None,
                "有孤辰": len(gc_positions) > 0,
            },
            "寡宿": {
                "地支": guasu_zhi,
                "所在柱位": gs_positions or None,
                "有寡宿": len(gs_positions) > 0,
            },
        }

    # --- 红鸾天喜 ---
    # 红鸾：卯起子逆数
    # 子→卯,丑→寅,寅→丑,卯→子,辰→亥,巳→戌,午→酉,未→申,
    # 申→未,酉→午,戌→巳,亥→辰
    _HONGLUAN = {
        "子": "卯", "丑": "寅", "寅": "丑", "卯": "子",
        "辰": "亥", "巳": "戌", "午": "酉", "未": "申",
        "申": "未", "酉": "午", "戌": "巳", "亥": "辰",
    }

    def hongluan_tianxi(self, day_zhi=None):
        """
        红鸾天喜 — 日支查地支

        红鸾主婚恋喜事、桃花正缘、喜庆之事。
        天喜主添丁、升迁、吉庆。
        红鸾天喜同现则婚期将近或家有喜事。

        Args:
            day_zhi: 日支（默认使用实例 day_zhi）

        Returns:
            dict: {
                "红鸾": {"地支": str, "所在柱位": list | None, "有红鸾": bool},
                "天喜": {"地支": str, "所在柱位": list | None, "有天喜": bool},
            }
        """
        day_zhi = day_zhi or self.day_zhi

        hongluan_zhi = self._HONGLUAN.get(day_zhi, "")
        # 天喜 = 红鸾的对冲位（地支+6）
        tianxi_zhi = ""
        if hongluan_zhi:
            hl_idx = DIZHI.index(hongluan_zhi)
            tianxi_zhi = DIZHI[(hl_idx + 6) % 12]

        hl_positions = []
        tx_positions = []

        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                           ("日", self.day_zhi), ("时", self.hour_zhi)]:
            if zhi == hongluan_zhi:
                hl_positions.append(label)
            if tianxi_zhi and zhi == tianxi_zhi:
                tx_positions.append(label)

        return {
            "红鸾": {
                "地支": hongluan_zhi,
                "所在柱位": hl_positions or None,
                "有红鸾": len(hl_positions) > 0,
            },
            "天喜": {
                "地支": tianxi_zhi,
                "所在柱位": tx_positions or None,
                "有天喜": len(tx_positions) > 0,
            },
        }


# ============================================================
# 纳音五行（六十甲子纳音表）
# ============================================================

# 六十甲子纳音五行对照表（以干支对为 key）
NAYIN = {
    "甲子": "海中金", "乙丑": "海中金", "丙寅": "炉中火", "丁卯": "炉中火",
    "戊辰": "大林木", "己巳": "大林木", "庚午": "路旁土", "辛未": "路旁土",
    "壬申": "剑锋金", "癸酉": "剑锋金", "甲戌": "山头火", "乙亥": "山头火",
    "丙子": "涧下水", "丁丑": "涧下水", "戊寅": "城头土", "己卯": "城头土",
    "庚辰": "白蜡金", "辛巳": "白蜡金", "壬午": "杨柳木", "癸未": "杨柳木",
    "甲申": "泉中水", "乙酉": "泉中水", "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹雳火", "己丑": "霹雳火", "庚寅": "松柏木", "辛卯": "松柏木",
    "壬辰": "长流水", "癸巳": "长流水", "甲午": "沙中金", "乙未": "沙中金",
    "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金",
    "甲辰": "覆灯火", "乙巳": "覆灯火", "丙午": "天河水", "丁未": "天河水",
    "戊申": "大驿土", "己酉": "大驿土", "庚戌": "钗钏金", "辛亥": "钗钏金",
    "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水",
    "丙辰": "沙中土", "丁巳": "沙中土", "戊午": "天上火", "己未": "天上火",
    "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水",
}

# 纳音五行反查表（纳音名 → 五行）
NAYIN_WUXING = {
    "海中金": "金", "炉中火": "火", "大林木": "木", "路旁土": "土",
    "剑锋金": "金", "山头火": "火", "涧下水": "水", "城头土": "土",
    "白蜡金": "金", "杨柳木": "木", "泉中水": "水", "屋上土": "土",
    "霹雳火": "火", "松柏木": "木", "长流水": "水", "沙中金": "金",
    "山下火": "火", "平地木": "木", "壁上土": "土", "金箔金": "金",
    "覆灯火": "火", "天河水": "水", "大驿土": "土", "钗钏金": "金",
    "桑柘木": "木", "大溪水": "水", "沙中土": "土", "天上火": "火",
    "石榴木": "木", "大海水": "水",
}


# ============================================================
# 旬空（空亡）
# ============================================================

# 旬空表：六甲旬 → 空亡地支对
# 甲子旬（甲子→癸酉）戌亥空
# 甲戌旬（甲戌→癸未）申酉空
# 甲申旬（甲申→癸巳）午未空
# 甲午旬（甲午→癸卯）辰巳空
# 甲辰旬（甲辰→癸丑）寅卯空
# 甲寅旬（甲寅→癸亥）子丑空
XUNKONG = {
    "甲子": ("戌", "亥"), "乙丑": ("戌", "亥"), "丙寅": ("戌", "亥"), "丁卯": ("戌", "亥"),
    "戊辰": ("戌", "亥"), "己巳": ("戌", "亥"), "庚午": ("戌", "亥"), "辛未": ("戌", "亥"),
    "壬申": ("戌", "亥"), "癸酉": ("戌", "亥"),
    "甲戌": ("申", "酉"), "乙亥": ("申", "酉"), "丙子": ("申", "酉"), "丁丑": ("申", "酉"),
    "戊寅": ("申", "酉"), "己卯": ("申", "酉"), "庚辰": ("申", "酉"), "辛巳": ("申", "酉"),
    "壬午": ("申", "酉"), "癸未": ("申", "酉"),
    "甲申": ("午", "未"), "乙酉": ("午", "未"), "丙戌": ("午", "未"), "丁亥": ("午", "未"),
    "戊子": ("午", "未"), "己丑": ("午", "未"), "庚寅": ("午", "未"), "辛卯": ("午", "未"),
    "壬辰": ("午", "未"), "癸巳": ("午", "未"),
    "甲午": ("辰", "巳"), "乙未": ("辰", "巳"), "丙申": ("辰", "巳"), "丁酉": ("辰", "巳"),
    "戊戌": ("辰", "巳"), "己亥": ("辰", "巳"), "庚子": ("辰", "巳"), "辛丑": ("辰", "巳"),
    "壬寅": ("辰", "巳"), "癸卯": ("辰", "巳"),
    "甲辰": ("寅", "卯"), "乙巳": ("寅", "卯"), "丙午": ("寅", "卯"), "丁未": ("寅", "卯"),
    "戊申": ("寅", "卯"), "己酉": ("寅", "卯"), "庚戌": ("寅", "卯"), "辛亥": ("寅", "卯"),
    "壬子": ("寅", "卯"), "癸丑": ("寅", "卯"),
    "甲寅": ("子", "丑"), "乙卯": ("子", "丑"), "丙辰": ("子", "丑"), "丁巳": ("子", "丑"),
    "戊午": ("子", "丑"), "己未": ("子", "丑"), "庚申": ("子", "丑"), "辛酉": ("子", "丑"),
    "壬戌": ("子", "丑"), "癸亥": ("子", "丑"),
}


# ============================================================
# BaziCalculator 扩展方法
# ============================================================

# 以下方法通过 monkey-patch 添加到 BaziCalculator 类
# 或直接修改类的定义

import json as _json


def _get_nayin(self, ganzhi):
    """
    根据干支查询纳音五行

    依据：《渊海子平》六十甲子纳音歌诀

    Args:
        ganzhi: 干支组合（如 '甲子'、'丙寅'），2字符

    Returns:
        dict: {"ganzhi": "甲子", "nayin": "海中金", "wuxing": "金"}
    """
    nayin_name = NAYIN.get(ganzhi, "未知")
    return {
        "ganzhi": ganzhi,
        "nayin": nayin_name,
        "wuxing": NAYIN_WUXING.get(nayin_name, "未知"),
    }


def _get_xunkong(self, day_ganzhi):
    """
    根据日柱干支计算空亡地支（旬空）

    依据：《渊海子平》六甲旬空法
    甲子旬戌亥空……以此类推，以日柱所在旬为准

    Args:
        day_ganzhi: 日柱干支（如 '甲子'）

    Returns:
        list[str]: 空亡地支列表（2个）
    """
    return list(XUNKONG.get(day_ganzhi, ("未知", "未知")))


def _calculate_sizhu_extended(self, year, month, day, hour, gender):
    """
    扩展版排盘：在原有基础上增加纳音和空亡

    Returns:
        dict: 包含完整命盘数据，比基类多了每个柱的纳音和空亡信息
    """
    result = self._calculate_sizhu_original(year, month, day, hour, gender)

    # 为每个柱添加纳音
    for key in ["year", "month", "day", "hour"]:
        result[f"{key}_nayin"] = _get_nayin(self, result[key])

    # 空亡：以日柱为基准
    result["xunkong"] = _get_xunkong(self, result["day"])

    # 胎元：月干顺推一位 + 月支顺推三位
    taiyuan_gz = self.get_taiyuan(result["month"])
    result["taiyuan"] = taiyuan_gz
    result["taiyuan_nayin"] = _get_nayin(self, taiyuan_gz)

    # 命宫：月支起子时逆数至生时，天干用五虎遁（年上起月）
    minggong_zhi = self.get_minggong(result["month"], result["hour"])
    minggong_gz = self.get_month_ganzhi(result["year"][0], minggong_zhi)
    result["minggong"] = minggong_gz
    result["minggong_nayin"] = _get_nayin(self, minggong_gz)

    # 身宫：月支起子时顺数至生时，天干用五虎遁（年上起月）
    shengong_zhi = self.get_shengong(result["month"], result["hour"])
    shengong_gz = self.get_month_ganzhi(result["year"][0], shengong_zhi)
    result["shengong"] = shengong_gz
    result["shengong_nayin"] = _get_nayin(self, shengong_gz)

    return result


# ============================================================
# BaziAnalyzer 扩展方法
# ============================================================

def _build_fu_zhu(self, ganzhi, nayin_key):
    """
    构建胎元/命宫等辅助柱的结构化字典

    Args:
        ganzhi: 干支字符串（如 '乙卯'），可为空字符串
        nayin_key: 纳音字段名（如 'taiyuan_nayin'）

    Returns:
        dict: {干支, 天干, 地支, 五行, 阴阳, 藏干, 纳音, 十神}
    """
    gan = ganzhi[0] if ganzhi else ""
    zhi = ganzhi[1] if ganzhi else ""
    return {
        "干支": ganzhi,
        "天干": gan,
        "地支": zhi,
        "五行": TIANGAN_WUXING.get(gan, "?") if gan else "?",
        "阴阳": TIANGAN_YINYANG.get(gan, "?") if gan else "?",
        "藏干": DIZHI_CANGGAN.get(zhi, []) if zhi else [],
        "纳音": self.data.get(nayin_key, {}),
        "十神": get_shishen(self.day_gan, gan) if gan else "",
    }


def _to_dict(self):
    """
    将完整命盘分析数据转为结构化字典

    为 AI 代理（如 OpenClaw）和外部程序提供标准化的数据接口。
    所有命理数据均以字典形式组织，可直接用于 JSON 序列化。

    Returns:
        dict: 包含命盘总览、十神、五行、旺衰、格局、大运等完整数据结构
    """
    wangshuai = self.analyze_wangshuai()
    xiyong = self.determine_xiyong(wangshuai)

    result = {
        "命盘总览": {
            "年柱": {
                "干支": self.data.get("year", ""),
                "天干": self.data["year"][0] if self.data.get("year") else "",
                "地支": self.data["year"][1] if self.data.get("year") else "",
                "五行": TIANGAN_WUXING.get(self.data["year"][0], "?") if self.data.get("year") else "?",
                "阴阳": TIANGAN_YINYANG.get(self.data["year"][0], "?") if self.data.get("year") else "?",
                "藏干": DIZHI_CANGGAN.get(self.data["year"][1], []) if self.data.get("year") else [],
                "纳音": self.data.get("year_nayin", {}),
            },
            "月柱": {
                "干支": self.data.get("month", ""),
                "天干": self.data["month"][0] if self.data.get("month") else "",
                "地支": self.data["month"][1] if self.data.get("month") else "",
                "五行": TIANGAN_WUXING.get(self.data["month"][0], "?") if self.data.get("month") else "?",
                "阴阳": TIANGAN_YINYANG.get(self.data["month"][0], "?") if self.data.get("month") else "?",
                "藏干": DIZHI_CANGGAN.get(self.data["month"][1], []) if self.data.get("month") else [],
                "纳音": self.data.get("month_nayin", {}),
            },
            "日柱": {
                "干支": self.data.get("day", ""),
                "天干": self.data["day"][0] if self.data.get("day") else "",
                "地支": self.data["day"][1] if self.data.get("day") else "",
                "五行": TIANGAN_WUXING.get(self.data["day"][0], "?") if self.data.get("day") else "?",
                "阴阳": TIANGAN_YINYANG.get(self.data["day"][0], "?") if self.data.get("day") else "?",
                "藏干": DIZHI_CANGGAN.get(self.data["day"][1], []) if self.data.get("day") else [],
                "纳音": self.data.get("day_nayin", {}),
                "日主": True,
            },
            "时柱": {
                "干支": self.data.get("hour", ""),
                "天干": self.data["hour"][0] if self.data.get("hour") else "",
                "地支": self.data["hour"][1] if self.data.get("hour") else "",
                "五行": TIANGAN_WUXING.get(self.data["hour"][0], "?") if self.data.get("hour") else "?",
                "阴阳": TIANGAN_YINYANG.get(self.data["hour"][0], "?") if self.data.get("hour") else "?",
                "藏干": DIZHI_CANGGAN.get(self.data["hour"][1], []) if self.data.get("hour") else [],
                "纳音": self.data.get("hour_nayin", {}),
            },
            "月令": self.data.get("yuejian", ""),
            "空亡": self.data.get("xunkong", []),
            "胎元": _build_fu_zhu(self, self.data.get("taiyuan", ""), "taiyuan_nayin"),
            "命宫": _build_fu_zhu(self, self.data.get("minggong", ""), "minggong_nayin"),
            "身宫": _build_fu_zhu(self, self.data.get("shengong", ""), "shengong_nayin"),
        },
        "十神分析": {
            "天干十神": {},
            "地支藏干十神": {},
            "十神统计": self.get_shishen_distribution(),
        },
        "五行力量": {
            "天干": {},
            "地支": {},
            "分布统计": self.get_wuxing_distribution(),
            "加权得分": self.get_wuxing_score(),
        },
        "旺衰分析": {
            "日主": f"{self.day_gan}({TIANGAN_WUXING.get(self.day_gan, '?')})",
            "评分": wangshuai["score"],
            "结果": wangshuai["result"],
            "详细": wangshuai["details"],
        },
        "格局分析": {
            "格局": self.analyze_geju(),
            "喜用神": xiyong["xishen"],
            "忌神": xiyong["jishen"],
            "策略": xiyong["strategy"],
        },
        "神煞": self.get_shensha(),
        "大运": self.data.get("dayun", []),
        "大运方向": self.data.get("dayun_direction", "未知"),
    }

    # 填充天干十神
    for label, key in [("年干", "year"), ("月干", "month"), ("日干", "day"), ("时干", "hour")]:
        if self.data.get(key):
            gan = self.data[key][0]
            if key == "day":
                result["十神分析"]["天干十神"][label] = "日主"
            else:
                result["十神分析"]["天干十神"][label] = get_shishen(self.day_gan, gan)

    # 胎元/命宫/身宫 天干十神
    for label, key in [("胎元干", "taiyuan"), ("命宫干", "minggong"), ("身宫干", "shengong")]:
        if self.data.get(key):
            gan = self.data[key][0]
            result["十神分析"]["天干十神"][label] = get_shishen(self.day_gan, gan)

    # 填充地支藏干十神
    for label, key in [("年支", "year"), ("月支", "month"), ("日支", "day"), ("时支", "hour")]:
        if self.data.get(key):
            zhi = self.data[key][1]
            canggan_list = []
            for cg in DIZHI_CANGGAN.get(zhi, []):
                ss = get_shishen(self.day_gan, cg)
                canggan_list.append(f"{cg}({ss})")
            result["十神分析"]["地支藏干十神"][label] = canggan_list

    # 胎元/命宫/身宫 地支藏干十神
    for label, key in [("胎元支", "taiyuan"), ("命宫支", "minggong"), ("身宫支", "shengong")]:
        if self.data.get(key):
            zhi = self.data[key][1]
            canggan_list = []
            for cg in DIZHI_CANGGAN.get(zhi, []):
                ss = get_shishen(self.day_gan, cg)
                canggan_list.append(f"{cg}({ss})")
            result["十神分析"]["地支藏干十神"][label] = canggan_list

    # 填充天干/地支五行
    for label, key in [("年柱", "year"), ("月柱", "month"), ("日柱", "day"), ("时柱", "hour")]:
        if self.data.get(key):
            g, z = self.data[key][0], self.data[key][1]
            result["五行力量"]["天干"][label] = f"{g}({TIANGAN_WUXING.get(g, '?')})"
            result["五行力量"]["地支"][label] = f"{z}({DIZHI_WUXING.get(z, '?')})"

    return result


def _to_json(self, indent=2, ensure_ascii=False):
    """
    将命盘分析数据转为 JSON 字符串

    Args:
        indent: JSON 缩进空格数（默认2）
        ensure_ascii: 是否转义非 ASCII 字符（默认 False，保留中文）

    Returns:
        str: JSON 字符串
    """
    return _json.dumps(_to_dict(self), indent=indent, ensure_ascii=ensure_ascii)


def _get_wuxing_score(self):
    """
    五行力量加权量化评分

    依据：子平命理"得令最重、得地次之、得势再次"的旺衰法则，
    对天干、地支藏干、月令分别赋予权重，量化五行力量对比。

    权重规则：
        - 天干 ×1.0（四柱各天干各计1）
        - 地支本气 ×1.0（每支第一藏干）
        - 地支中气 ×0.6（每支第二藏干）
        - 地支余气 ×0.3（每支第三藏干）
        - 月令 ×1.5（月支本气五行额外加成，得令最重）

    Returns:
        dict: {
            "得分": {"金": x, "木": x, "水": x, "火": x, "土": x},
            "占比": {"金": p, ...},   # 百分比(0-100，保留1位小数)
            "最强五行": "土",
            "最弱五行": "木",
            "明细": [...],             # 加权明细列表
        }
    """
    weights = {"金": 0.0, "木": 0.0, "水": 0.0, "火": 0.0, "土": 0.0}
    details = []

    # 藏干权重：本气/中气/余气
    canggan_weight = [1.0, 0.6, 0.3]

    # 1. 天干 ×1.0
    for label, key in [("年干", "year"), ("月干", "month"),
                       ("日干", "day"), ("时干", "hour")]:
        if self.data.get(key):
            gan = self.data[key][0]
            wx = TIANGAN_WUXING.get(gan)
            if wx:
                weights[wx] += 1.0
                details.append(f"天干{label}{gan}({wx}) +1.0")

    # 2. 地支藏干（本气1.0、中气0.6、余气0.3）
    for label, key in [("年支", "year"), ("月支", "month"),
                       ("日支", "day"), ("时支", "hour")]:
        if self.data.get(key):
            zhi = self.data[key][1]
            for i, cg in enumerate(DIZHI_CANGGAN.get(zhi, [])):
                w = canggan_weight[i] if i < len(canggan_weight) else 0.3
                wx = TIANGAN_WUXING.get(cg)
                if wx:
                    weights[wx] += w
                    details.append(f"地支{label}{zhi}藏干{cg}({wx}) +{w}")

    # 3. 月令 ×1.5（月支本气五行额外加成）
    yuejian = self.data.get("yuejian", "")
    if yuejian and DIZHI_CANGGAN.get(yuejian):
        benqi = DIZHI_CANGGAN[yuejian][0]
        wx = TIANGAN_WUXING.get(benqi)
        if wx:
            weights[wx] += 1.5
            details.append(f"月令{yuejian}本气{benqi}({wx}) +1.5")

    # 汇总：得分（保留1位）、占比、最强/最弱
    total = sum(weights.values())
    score = {wx: round(v, 1) for wx, v in weights.items()}
    ratio = {wx: round(v / total * 100, 1) if total > 0 else 0.0
             for wx, v in weights.items()}

    if total > 0:
        sorted_wx = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
        strongest = sorted_wx[0][0]
        weakest = sorted_wx[-1][0]
    else:
        strongest = "无"
        weakest = "无"

    return {
        "得分": score,
        "占比": ratio,
        "最强五行": strongest,
        "最弱五行": weakest,
        "明细": details,
    }


# ============================================================
# 将扩展方法注入到类中
# ============================================================

def _get_shensha(self):
    """
    神煞查询入口 — 返回11类神煞在四柱中的分布

    吉神：天乙贵人、文昌贵人、太极贵人、学堂词馆、
          华盖、将星、红鸾天喜
    中性：驿马、桃花
    凶煞：羊刃、孤辰寡宿

    Returns:
        dict: 包含所有神煞的查询结果，每个神煞含所在柱位和吉凶标注
    """
    sc = ShenshaCalculator(self.data)

    # 收集所有神煞
    all_shensha = {
        # --- 吉神 ---
        "天乙贵人": {"data": sc.tianyi_guiren(), "吉凶": "吉", "含义": "遇难呈祥、贵人扶助"},
        "文昌贵人": {"data": sc.wenchang_xueren(), "吉凶": "吉", "含义": "聪明好学、文采出众"},
        "太极贵人": {"data": sc.taiji_guiren(), "吉凶": "吉", "含义": "聪明好学、有特殊才能"},
        "学堂词馆": {"data": sc.xuetang_ciguan(), "吉凶": "吉", "含义": "学业有成、科甲功名"},
        "华盖": {"data": sc.huagai(), "吉凶": "吉", "含义": "清高聪明、喜神秘文化"},
        "将星": {"data": sc.jiangxing(), "吉凶": "吉", "含义": "领导力、决断力、统御才能"},
        "红鸾天喜": {"data": sc.hongluan_tianxi(), "吉凶": "吉", "含义": "婚恋喜事、添丁升迁"},
        # --- 中性 ---
        "桃花": {"data": sc.taohua(), "吉凶": "中性", "含义": "异性缘、人缘、艺术天赋"},
        "驿马": {"data": sc.yima(), "吉凶": "中性", "含义": "奔波、迁移、宜外出发展"},
        # --- 凶煞 ---
        "羊刃": {"data": sc.yangren(), "吉凶": "凶", "含义": "刚强果断、易冲动克亲"},
        "孤辰寡宿": {"data": sc.guchen_guasu(), "吉凶": "凶", "含义": "孤僻寡合、六亲缘浅"},
    }

    # 汇总：统计哪些神煞确实出现在命局中
    吉神命中 = []
    中性命中 = []
    凶煞命中 = []

    for name, info in all_shensha.items():
        d = info["data"]
        present = False

        # 根据返回结构判断是否存在
        if isinstance(d, dict):
            for key in d:
                if isinstance(d[key], dict):
                    # 嵌套结构如 "学堂"/"词馆"、"红鸾"/"天喜"
                    if d[key].get("有学堂") or d[key].get("有词馆") or \
                       d[key].get("有华盖") or d[key].get("有将星") or \
                       d[key].get("有羊刃") or d[key].get("有孤辰") or \
                       d[key].get("有寡宿") or d[key].get("有红鸾") or \
                       d[key].get("有天喜"):
                        present = True
                        break
                elif isinstance(d[key], list) and len(d[key]) > 0:
                    present = True
                    break
                elif isinstance(d[key], dict) and d[key].get("所在柱位"):
                    present = True
                    break
                elif isinstance(d[key], dict) and d[key].get("桃花类型") and d[key]["桃花类型"] != "无":
                    present = True
                    break
            # 兼容简单结构
            if d.get("所在柱位") or d.get("有文昌") or d.get("桃花类型", "无") != "无":
                present = True
            if d.get("日干查") and len(d.get("日干查", [])) > 0:
                present = True
            if d.get("年干查") and len(d.get("年干查", [])) > 0:
                present = True

        if present:
            if info["吉凶"] == "吉":
                吉神命中.append(name)
            elif info["吉凶"] == "凶":
                凶煞命中.append(name)
            else:
                中性命中.append(name)

    return {
        "详细": all_shensha,
        "汇总": {
            "吉神命中": 吉神命中,
            "中性命中": 中性命中,
            "凶煞命中": 凶煞命中,
            "总计": len(吉神命中) + len(中性命中) + len(凶煞命中),
        },
    }


BaziCalculator.get_nayin = _get_nayin
BaziCalculator.get_xunkong = _get_xunkong
BaziCalculator._calculate_sizhu_original = BaziCalculator.calculate_sizhu
BaziCalculator.calculate_sizhu = _calculate_sizhu_extended
BaziAnalyzer.to_dict = _to_dict
BaziAnalyzer.to_json = _to_json
BaziAnalyzer.get_shensha = _get_shensha
BaziAnalyzer.get_wuxing_score = _get_wuxing_score
