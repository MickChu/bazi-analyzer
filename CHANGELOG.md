# CHANGELOG

所有值得注意的变更记录于此，遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

---

## v1.3.0 — 节气与大运精确化 (2026-11-09)

### 新增

- **`bazi_engine.py`** 引入 `ephem` 库精确计算节气（误差 < 1 小时；`ephem` 缺失时回退到低精度天文近似，误差仍 < 1 小时）：
  - `BaziCalculator.get_jieqi_datetime(year, jieqi_name)` — 返回精确节气时刻（北京时间 naive datetime）
  - 天文辅助函数：`_datetime_to_jd` / `_jd_to_datetime`（儒略日与北京时间互转）、`_sun_ecliptic_longitude`（太阳视黄经，含岁差修正）、`_signed_lon_delta`（黄经带符号差定位）
  - 24 节气黄经表 `JIEQI_DEG`、十二「节」月建对照 `JIE_YUEJIAN`、近似日期表 `JIEQI_APPROX`
- **精确年柱/月建分界：**
  - `BaziCalculator.determine_year_ganzhi(year, month, day, hour)` — 以立春精确时刻为年柱分界
  - `BaziCalculator.determine_yuejian_precise(year, month, day, hour)` — 以十二「节」精确时刻为月建分界
- **`BaziCalculator.calculate_qiyun_age(year, month, day, hour, gender)`** — 按「距节天数÷3」计算起运年龄，返回岁/月/虚岁/距节天数/节气/方向；顺逆排按阳年男/阴年女规则
- **大运排盘精度提升：**
  - `calculate_dayun()` 支持传入精确起运虚岁（`qiyun_virtual_age`），替代固定 3+10n 近似
  - `calculate_sizhu()` 改用精确年柱/月建，新增 `qiyun` 字段
  - `to_dict()` 新增「起运」字段

### 修复

- **`bazi_engine.py`** — 修复固定日期近似的月建整体偏移：原 `determine_yuejian()` 在节令边界前后月建错位一个地支（如 6 月 15 日被误判为未月，实际应为午月）。精确化后 1990-06-15 月柱由「癸未」修正为「壬午」，胎元/命宫/身宫及五行得分随之校正。
- **`bazi_engine.py`** — 修复逆排大运地支取模错误：`calculate_dayun()` 逆排地支 `% 10` 应为 `% 12`。
- **`bazi_engine.py`** — 修复 `get_month_ganzhi()` 月干偏移：子/丑月（寅月之前）的偏移量未按 12 地支回环，导致月干错位。

### 测试

- 新增 `test_get_jieqi_datetime`、`test_determine_year_ganzhi`、`test_determine_yuejian_precise`、`test_calculate_qiyun_age`、`test_dayun_uses_precise_qiyun`、`test_dayun_dizhi_mod_fix` 共 6 项；同步校正受月建修正影响的胎元/命宫/身宫/五行得分/流年冲合断言。测试总计 39 项全部通过。

### 已知问题（待后续版本）

- 十神「印/食伤」阴阳判定与子平标准相反（ROADMAP 命理改进清单 #9），本次仅记录未改动，避免影响既有 Excel 输出与既有断言。

### 依据

- 节气（定气法）：太阳视黄经每 15° 为一节气，立春 315° 起算；月建以十二「节」为界、年柱以立春为界
- 起运：《渊海子平》阳年男顺阴年女逆，距节天数÷3 折算（三天一岁、一天四个月）
- 天文：ephem 星历 + 岁差修正（general precession in longitude，J2000.0 → 当日平春分点）

---

## v1.2.3 — Excel Sheet 6-7：胎元命宫身宫 + 大运流年；图表可视化 (2026-10-26)

### 新增

- **`excel_report.py`** 新增两个 Sheet，报告由 5 个 Sheet 扩展为 7 个：
  - **Sheet 6「胎元命宫身宫」**：
    - 胎元 / 命宫 / 身宫三柱详表（干支、天干、地支、藏干、纳音、十神）
    - 五行力量雷达图（以加权得分占比为数据源，openpyxl RadarChart）
  - **Sheet 7「大运流年」**：
    - 大运排盘表：8 步大运（大运干支、年龄区间、天干十神、地支本气、五行）
    - 流年概览表：近五年流年（年份、虚岁、流年干支、十神、五行、日支关系、命局冲合）
    - 十神数量条形图（openpyxl BarChart）
- 新增数据构建函数：`_fusanzhu_rows`、`_dayun_rows`、`_liunian_rows`；新增 `_build_sheet6`、`_build_sheet7`

- **`bazi_engine.py`** 新增流年概览能力：
  - `BaziAnalyzer.analyze_liunian(year)` — 流年概览：流年干支、天干十神（以日干论）、地支五行、与日支的六合/六冲、与命局四柱地支的冲合关系
  - `BaziAnalyzer.get_liunian_overview(start_year, count)` — 连续多年流年概览列表（含虚岁）
  - `to_dict()` 新增「流年概览」字段；扩展排盘新增 `birth_year` 等出生信息字段
  - 说明：此为概览层；深度流年分析（天干地支分别作用、岁运并临、天克地冲）在 v1.3.2 实现

### 测试

- 新增 `test_analyze_liunian`、`test_get_liunian_overview`、`test_dayun_data`，测试总计 33 项全部通过。

### 依据

- 胎元/命宫/身宫：《渊海子平》《三命通会》起法（复用 v1.1.3 / v1.1.4 引擎计算结果）
- 大运：《渊海子平》阳年男顺阴年女逆排法；流年天干以日干论十神、地支以日支论冲合

---

## v1.2.2 — Excel Sheet 4-5：格局分析 + 神煞系统 (2026-10-12)

### 新增

- **`excel_report.py`** 新增两个 Sheet，报告由 3 个 Sheet 扩展为 5 个：
  - **Sheet 4「格局分析」**：
    - 身强身弱判断：日主、旺衰评分、旺衰结果、逐项评分明细（得令/得地/得势）
    - 格局判定：月令透干成格 + 特殊组合断语（杀印相生、伤官见官等）
    - 喜用神与忌神：喜用神 / 忌神五行 + 取用策略
  - **Sheet 5「神煞系统」**：
    - 命中汇总行：吉神 / 中性 / 凶煞命中数量与清单
    - 神煞详表：11 类神煞（吉 / 中性 / 凶排序），含所在地支、命中柱位、吉凶标注、含义
- 新增数据构建函数：`_wangshuai_rows`、`_geju_rows`、`_xiyong_rows`、`_shensha_rows`
- 数据全部复用 `bazi_engine.py` 的 `to_dict()` 中「旺衰分析」「格局分析」「神煞」数据段

### 修复

- **`bazi_engine.py`** — 修复 `get_shensha()` 神煞命中判定：原实现对天乙/太极贵人的 `贵人地支`（查询用参考地支）误判为命中证据，导致命局无该贵人地支时仍被计入「吉神命中」。新增 `_shensha_present()` 按各神煞实际返回结构精确判定命中。
- 新增回归测试 `test_shensha_summary_accuracy`，测试总计 30 项全部通过。

### 依据

- 《渊海子平》格局体系、子平扶抑取用法；《渊海子平》《三命通会》神煞章节

---

## v1.2.1 — Excel Sheet 2-3：十神分析 + 五行力量 (2026-09-28)

### 新增

- **`excel_report.py`** 新增两个 Sheet，报告由 1 个 Sheet 扩展为 3 个：
  - **Sheet 2「十神分析」**：
    - 天干十神表：年/月/日/时四干 + 胎元/命宫/身宫天干的十神（日干标为「日主」）
    - 地支藏干十神表：四支 + 胎元/命宫/身宫地支的藏干十神（逐干标注）
    - 十神统计：按数量降序统计各十神出现次数（含藏干），附合计
  - **Sheet 3「五行力量」**：
    - 五行分布统计：天干 / 地支 / 藏干分别计数后汇总
    - 五行加权得分表：复用 `get_wuxing_score()` 的得分与占比
    - 最强 / 最弱五行标注
    - **五行强弱柱状图**（openpyxl BarChart，以加权得分为数据源）
- 新增样式辅助：`_write_sheet_header`、`_write_table`、`_section_label` 等复用函数，三个 Sheet 共用同一套朱砂红样式系统

### 依据

- 《渊海子平》十神体系；子平旺衰法则「得令最重、得地次之、得势再次」
- 数据复用 `bazi_engine.py` 的 `to_dict()` 中「十神分析」「五行力量」两个数据段，保证三端一致

---

## v1.2.0 — Excel 报告框架 (2026-09-14)

### 新增

- **`excel_report.py`** — 独立可运行的 Excel 报告生成模块
  - 引入 `openpyxl`（本项目唯一外部依赖，`pip install openpyxl`）
  - 样式系统：标题/副标题/正文字体、表头底色、隔行浅底、细边框、居中对齐（传统朱砂红主题色）
  - **Sheet 1「命盘总览」**：
    - 基本信息区：出生时间、四柱、月令、空亡、大运方向
    - 四柱详表：柱位 / 天干 / 地支 / 藏干 / 纳音 / 空亡 / 十神（日柱行加粗突出日主）
- **`generate_report(sizhu_data, output_path)`** — 入口函数，接受 `calculate_sizhu()` 返回值，生成 .xlsx
- **CLI 独立运行** — `python excel_report.py --year 1990 --month 6 --day 15 --hour 12 --gender 男`
  - 支持 `--output` 自定义输出路径，默认自动命名 `bazi_report_YYYY-MM-DD.xlsx`

### 依据

- 《渊海子平》《三命通会》排盘体系
- 数据复用 `bazi_engine.py` 的 `to_dict()` 结构化输出，保证 CLI/GUI/Excel 三端一致

---

## v1.1.4 — 身宫 + 五行力量加权量化评分 (2026-08-31)

### 新增

- **`BaziCalculator.get_shengong(month_ganzhi, hour_ganzhi)`** — 身宫地支计算：月支起子时顺数至生时（与命宫逆数相对）
- **扩展排盘 `calculate_sizhu()`** — 新增 `shengong`、`shengong_nayin` 字段
- **身宫天干** — 采用五虎遁（年上起月法）由年干推出
- **`BaziAnalyzer.get_wuxing_score()`** — 五行力量加权量化评分
  - 权重规则：天干×1、地支本气×1、地支中气×0.6、地支余气×0.3、月令×1.5
  - 返回：五行得分、占比、最强/最弱五行、加权明细
- **`to_dict()` 扩展** — `命盘总览` 新增 `身宫`；`十神分析` 新增 `身宫干`、`身宫支`；`五行力量` 新增 `加权得分`
- 测试新增 6 项，29/29 全部通过

### 依据

- 《三命通会》身宫起法
- 身宫诀：以月支起子时，顺数至生时，所至之支即身宫
- 子平旺衰法则：得令最重、得地次之、得势再次

---

## v1.1.3 — 胎元 + 命宫 (2026-08-17)

### 新增

- **`BaziCalculator.get_taiyuan(month_ganzhi)`** — 胎元计算：月干顺推一位 + 月支顺推三位
- **`BaziCalculator.get_minggong(month_ganzhi, hour_ganzhi)`** — 命宫地支计算：月支起子时逆数至生时
- **扩展排盘 `calculate_sizhu()`** — 新增 `taiyuan`、`minggong`、`taiyuan_nayin`、`minggong_nayin` 字段
- **命宫天干** — 采用五虎遁（年上起月法）由年干推出
- **`to_dict()` 扩展** — `命盘总览` 新增 `胎元`、`命宫` 两项（干支/天干/地支/五行/阴阳/藏干/纳音/十神）；`十神分析` 新增 `胎元干`、`命宫干`（天干十神）与 `胎元支`、`命宫支`（藏干十神）
- 测试新增 5 项，23/23 全部通过

### 依据

- 《渊海子平》《三命通会》胎元、命宫起法
- 胎元诀：以月柱为基，天干顺进一位、地支顺进三位
- 命宫诀：以月支起子时，逆数至生时，所至之支即命宫

---

## v1.1.2 — 神煞系统（下） (2026-07-06)

### 新增

- **ShenshaCalculator 扩展 7 个神煞方法：**
  - `taohua()` — 桃花/咸池，日支+年支双查四柱地支，区分墙内/墙外桃花
  - `yangren()` — 羊刃，阳干帝旺位、阴干墓库位
  - `yima()` — 驿马，日支+年支双查，主动、奔波、迁移
  - `huagai()` — 华盖，日支查地支，主清高聪明、喜神秘文化
  - `jiangxing()` — 将星，日支查地支，主领导力、决断力
  - `guchen_guasu()` — 孤辰寡宿，日支查地支，主孤僻寡合
  - `hongluan_tianxi()` — 红鸾天喜，日支查地支，主婚恋喜事
- **神煞汇总输出重构：** `get_shensha()` 返回结构改为 `{"详细": {...}, "汇总": {...}}`
  - `详细` 中每项含 `data`（查询结果）、`吉凶`（吉/中性/凶）、`含义`（一句话说明）
  - `汇总` 含 `吉神命中`、`中性命中`、`凶煞命中` 分类列表
- **ShenshaCalculator 辅助方法：** `_get_sanhe_ju()`、`_get_sanhui_ju()`
- 测试更新：2 个旧测试适配新结构，18/18 全部通过

### 依据

- 《渊海子平》《三命通会》神煞章节
- 桃花诀：申子辰在酉，寅午戌在卯……
- 羊刃诀：甲刃在卯，丙戊刃在午，庚刃在酉，壬刃在子
- 驿马诀：申子辰在寅，寅午戌在申……
- 华盖诀：申子辰见辰，寅午戌见戌……
- 将星诀：申子辰见子，寅午戌见午……
- 红鸾诀：卯起子逆数……

---

## v1.1.1 — 神煞系统（上） (2026-06-22)

### 新增

- **ShenshaCalculator 类**：独立的神煞计算模块，负责查算八字常用吉神
  - `tianyi_guiren()` — 天乙贵人，日干/年干双查四柱地支
  - `wenchang_xueren()` — 文昌贵人，日干查地支
  - `taiji_guiren()` — 太极贵人，日干/年干双查
  - `xuetang_ciguan()` — 学堂词馆，日干查长生/临官位
- **BaziAnalyzer.get_shensha()** — 神煞集成入口，返回四类吉神完整分布
- **to_dict() 扩展** — 新增 `神煞` 数据段

### 依据

- 《渊海子平》神煞章节
- 《三命通会》神煞篇
- 天乙贵人诀：甲戊庚牛羊，乙己鼠猴乡……
- 文昌贵人诀：甲乙巳午报君知……
- 太极贵人诀：甲乙子午，丙丁卯酉……
- 学堂在长生位，词馆在临官位

---

## v1.1.0 — 结构化输出 + 纳音 + 空亡 (2026-06-??)

### 新增

- `BaziAnalyzer.to_dict()` — 完整命盘结构化字典输出
- `BaziAnalyzer.to_json()` — JSON 序列化
- `NAYIN` 六十甲子纳音五行对照表
- `BaziCalculator.get_nayin()` — 纳音查询
- `XUNKONG` 旬空空亡对照表
- `BaziCalculator.get_xunkong()` — 空亡计算
- `calculate_sizhu()` 扩展版 — 自动计算纳音和空亡
- 8 个单元测试
