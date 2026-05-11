# 进化路线图 (Evolution Roadmap)

八字命理分析系统迭代计划。每两周一个小迭代，持续精进。

## 总览

| 版本 | 迭代窗口 | 状态 | 模块 | 内容概要 |
|------|---------|------|------|----------|
| v1.1.0 | 第1周 | ✅ 已完成 | bazi_engine.py | 结构化输出 + 纳音五行 + 空亡计算 |
| v1.1.1 | 第3周 | ⬜ 待开始 | bazi_engine.py | 神煞系统(上)：天乙贵人、文昌贵人、太极贵人、学堂词馆 |
| v1.1.2 | 第5周 | ⬜ 待开始 | bazi_engine.py | 神煞系统(下)：桃花(咸池)、羊刃、驿马、华盖、将星、孤辰、寡宿、红鸾天喜 |
| v1.1.3 | 第7周 | ⬜ 待开始 | bazi_engine.py | 胎元 + 命宫计算（含天干地支、纳音、十神） |
| v1.1.4 | 第9周 | ⬜ 待开始 | bazi_engine.py | 身宫计算 + 五行力量加权量化评分 |
| v1.2.0 | 第11周 | ⬜ 待开始 | excel_report.py | 框架搭建 + 样式系统；Sheet 1：命盘总览 |
| v1.2.1 | 第13周 | ⬜ 待开始 | excel_report.py | Sheet 2-3：十神分析（天干+藏干） + 五行力量含量化得分 |
| v1.2.2 | 第15周 | ⬜ 待开始 | excel_report.py | Sheet 4-5：格局分析（含喜用神） + 神煞系统 |
| v1.2.3 | 第17周 | ⬜ 待开始 | excel_report.py | Sheet 6-7：胎元命宫身宫 + 大运流年；图表可视化 |
| v1.3.0 | 第19周 | ⬜ 待开始 | bazi_engine.py | 节气精确化（ephem库）+ 大运起运年龄精确计算 |
| v1.3.1 | 第21周 | ⬜ 待开始 | bazi_engine.py | 从格判定算法（从旺/从强/从势/从儿）+ 润下格等特殊格局 |
| v1.3.2 | 第23周 | ⬜ 待开始 | bazi_engine.py | 《穷通宝鉴》调候用神体系 + 流年深度分析（天干地支分别作用） |
| v1.4.0 | 第25周 | ⬜ 待开始 | 全局 | CLI 入口重构（bazi_cli.py 命令行一次性调用） + 文档接口说明 |
| v1.4.1 | 第27周 | ⬜ 待开始 | SKILL | SKILL.md 框架搭建：创建 bazi-skill 目录结构 |
| v1.4.2 | 第29周 | ⬜ 待开始 | SKILL | SKILL 指令细化：定义 OpenClaw 调用八字引擎的标准流程、输出模板 |
| v1.4.3 | 第31周 | ⬜ 待开始 | SKILL/MCP | MCP Server 框架：stdio JSON-RPC 骨架 + tools/list + tools/call |
| v1.4.4 | 第33周 | ⬜ 待开始 | SKILL/MCP | MCP 工具实现：bazi_paipan、bazi_dayun、bazi_liunian 三个工具 |
| v1.4.5 | 第35周 | ⬜ 待开始 | SKILL/MCP | MCP 工具补充 + 测试：bazi_shensha、bazi_geju、bazi_excel |
| v1.4.6 | 第37周 | ⬜ 待开始 | SKILL/MCP | 集成联调 + README 更新：OpenClaw 侧配置说明、示例对话 |

**总计：17个版本，34周覆盖，每步改动量小、风险可控。**

---

## 详细迭代内容

### v1.1.0 — 结构化输出 + 纳音 + 空亡
**文件：** `bazi_engine.py`

- [ ] `BaziAnalyzer.to_dict()` — 将完整命盘数据转为结构化字典
- [ ] `BaziAnalyzer.to_json()` — 调用 to_dict() 后 json.dumps 输出
- [ ] `NAYIN` 六十甲子纳音五行对照表
- [ ] `BaziCalculator.get_nayin(ganzhi)` — 根据干支查询纳音
- [ ] `XUNKONG` 旬空/空亡计算：甲子旬戌亥空、甲戌旬申酉空……
- [ ] `BaziCalculator.get_xunkong(day_ganzhi)` — 根据日柱计算空亡地支
- [ ] 单元测试覆盖（test_bazi_engine.py 基础框架）

### v1.1.1 — 神煞系统（上）
**文件：** `bazi_engine.py`

- [ ] `ShenshaCalculator` 类
- [ ] `tianyi_guiren(day_gan, year_gan)` — 天乙贵人（日干+年干双查）
- [ ] `wenchang_xueren(day_gan)` — 文昌贵人（日干查地支）
- [ ] `taiji_guiren(day_gan, year_gan)` — 太极贵人
- [ ] `xuetang_ciguan(day_gan)` — 学堂词馆
- [ ] `BaziAnalyzer.get_shensha()` 集成入口

### v1.1.2 — 神煞系统（下）
**文件：** `bazi_engine.py`

- [ ] `taohua(day_zhi, year_zhi)` — 桃花/咸池
- [ ] `yangren(day_gan)` — 羊刃（阳干帝旺位）
- [ ] `yima(day_zhi, year_zhi)` — 驿马
- [ ] `huagai(day_zhi)` — 华盖
- [ ] `jiangxing(day_zhi)` — 将星
- [ ] `guchen_guasu(day_zhi)` — 孤辰、寡宿
- [ ] `hongluan_tianxi(day_zhi)` — 红鸾、天喜
- [ ] 神煞汇总输出（去重、标注吉凶）

### v1.1.3 — 胎元 + 命宫
**文件：** `bazi_engine.py`

- [ ] `BaziCalculator.get_taiyuan(month_ganzhi)` — 胎元 = 月干前一位 + 月支前三位
- [ ] `BaziCalculator.get_minggong(month_ganzhi, hour_ganzhi)` — 命宫 = 月支+时支→子位逆数
- [ ] 胎元/命宫的纳音、藏干、十神推导
- [ ] `to_dict()` 增加 `taiyuan`、`minggong` 字段

### v1.1.4 — 身宫 + 五行量化
**文件：** `bazi_engine.py`

- [ ] `BaziCalculator.get_shengong(month_ganzhi, hour_ganzhi)` — 身宫计算
- [ ] 五行力量加权评分：天干×1、地支本气×1、地支中气×0.6、地支余气×0.3、月令×1.5
- [ ] `BaziAnalyzer.get_wuxing_score()` — 返回带权重的五行得分字典
- [ ] 身宫十神、纳音推导

### v1.2.0 — Excel 报告框架
**文件：** `excel_report.py`（独立可运行）

- [ ] `openpyxl` 依赖声明（唯一外部依赖）
- [ ] 样式系统：标题字体/副标题字体/正文字体/边框/对齐/颜色
- [ ] Sheet 1：命盘总览 — 四柱表格（天干/地支/藏干/纳音/空亡/十神）
- [ ] `generate_report(sizhu_data, output_path)` 入口函数
- [ ] CLI 独立运行：`python excel_report.py --year 1990 --month 6 --day 15 --hour 12 --gender 男`

### v1.2.1 — Excel Sheet 2-3
**文件：** `excel_report.py`

- [ ] Sheet 2：十神分析 — 天干十神表 + 地支藏干十神表 + 十神统计
- [ ] Sheet 3：五行力量 — 天干/地支/藏干分别统计 + 加权得分 + 强弱柱状图

### v1.2.2 — Excel Sheet 4-5
**文件：** `excel_report.py`

- [ ] Sheet 4：格局分析 — 月令格局判定 + 特殊组合 + 身强身弱判断 + 喜用神+忌神
- [ ] Sheet 5：神煞系统 — 所有神煞列表 + 所在地支 + 吉凶标注

### v1.2.3 — Excel Sheet 6-7 + 可视化
**文件：** `excel_report.py`

- [ ] Sheet 6：胎元命宫身宫 — 三柱天干地支纳音十神
- [ ] Sheet 7：大运流年 — 10步大运表 + 流年概览
- [ ] 图表：五行雷达图 + 十神条形图（openpyxl chart）

### v1.3.0 — 节气与大运精确化
**文件：** `bazi_engine.py`

- [ ] 引入 `ephem` 库进行精确节气计算（误差 < 1小时）
- [ ] `get_jieqi_datetime(year, jieqi_name)` — 返回精确节气时刻
- [ ] `calculate_qiyun_age()` — 根据距节气天数÷3 计算起运年龄（可精确到几岁几个月）
- [ ] 大运排盘精度提升

### v1.3.1 — 从格判定
**文件：** `bazi_engine.py`

- [ ] `analyze_congge()` — 从格判定主函数
- [ ] 从旺格/从强格：日干旺极，全局生扶日干，无克泄耗
- [ ] 从势格/从杀格：日干弱极，全局克泄耗日干，无生扶
- [ ] 从儿格：食伤极旺，日干从之
- [ ] 润下格/稼穑格/从革格/曲直格/炎上格 等特殊格局

### v1.3.2 — 调候用神 + 流年深度分析
**文件：** `bazi_engine.py`

- [ ] `get_tiaohou_yongsh` — 《穷通宝鉴》调候用神表（日干×月令 查表）
- [ ] `analyze_liunian_deep(year)` — 深度流年分析：天干作用/地支作用/岁运并临/天克地冲
- [ ] 调候+扶抑 综合用神推荐

### v1.4.0 — CLI 入口重构
**文件：** `bazi_cli.py`（新）、`README.md`

**目标：** 让八字引擎可以被命令行一次性调用（非交互），为任何程序（包括OpenClaw）提供基础调用入口。

- [ ] `bazi_cli.py` — 命令行入口
  - `python bazi_cli.py 1990 6 15 12 男` → 文本输出
  - `python bazi_cli.py 1990 6 15 12 男 --json` → JSON 输出（基于 to_dict）
  - `python bazi_cli.py 1990 6 15 12 男 --excel report.xlsx` → xlsx 输出
- [ ] 更新 README 增加 CLI 用法说明

### v1.4.1 — SKILL 框架搭建
**文件：** `skills/bazi/SKILL.md`（新）

**目标：** 创建 OpenClaw Skill 目录结构和基础 SKILL.md，定义八字引擎调用的顶层指令。

- [ ] 创建 `skills/bazi/` 目录
- [ ] `SKILL.md`：定义 skill 名称、描述、触发条件
- [ ] 定义调用协议：何时触发（如用户提到八字/排盘/命理）、如何调用 bazi_cli
- [ ] 输出模板：命局分析的标准文本格式

### v1.4.2 — SKILL 指令细化
**文件：** `skills/bazi/SKILL.md`（修改）

**目标：** 完善 SKILL 指令，定义完整的人机对话→引擎调用→结果展示流程。

- [ ] 用户输入解析：公历日期提取、性别识别、时辰推算
- [ ] 引擎调用规范：命令行参数组装、结果捕获
- [ ] 输出美化模板：命盘总览、十神、五行、格局、神煞等七个Section
- [ ] 错误处理：无效输入、引擎异常的友好提示

### v1.4.3 — MCP Server 框架
**文件：** `mcp_server.py`（新）

**目标：** 实现 MCP (Model Context Protocol) stdio JSON-RPC 骨架，让八字引擎成为可被任意 AI 客户端调用的标准工具服务。

- [ ] MCP 协议基础：`tools/list` + `tools/call` 两个核心方法
- [ ] stdio 通信：stdin 读请求、stdout 写响应
- [ ] 工具注册框架：`register_tool(name, description, schema, handler)`
- [ ] 错误处理：无效工具名、参数缺失、异常捕获

### v1.4.4 — MCP 核心工具实现
**文件：** `mcp_server.py`（修改）

**目标：** 实现前三个 MCP 工具，覆盖八字排盘、大运、流年核心功能。

- [ ] `bazi_paipan` 工具：输入年月日时性别 → 返回完整命盘（四柱、十神、纳音、空亡）
- [ ] `bazi_dayun` 工具：输入命盘 + 当前年龄 → 返回大运走势
- [ ] `bazi_liunian` 工具：输入命盘 + 目标年份 → 返回流年分析

### v1.4.5 — MCP 扩展工具实现
**文件：** `mcp_server.py`（修改）

**目标：** 补充神煞、格局、Excel 三个工具，完整覆盖所有八字分析维度。

- [ ] `bazi_shensha` 工具：返回完整神煞（天乙贵人、文昌、桃花、羊刃等）
- [ ] `bazi_geju` 工具：返回格局判定 + 喜用神
- [ ] `bazi_excel` 工具：生成 Excel 报告，返回文件路径

### v1.4.6 — 集成联调 + 文档
**文件：** `README.md`、`CHANGELOG.md`、`skills/bazi/install.md`（新）

**目标：** 端到端测试 + 完整文档，确保 OpenClaw 和其他 MCP 客户端可直接使用。

- [ ] OpenClaw 侧 MCP 配置说明（config.toml 中的 mcp_servers 段）
- [ ] SKILL 安装说明（复制到哪里、如何启用）
- [ ] 示例对话：用户在 OpenClaw 中说"帮我排个八字"的完整交互流程
- [ ] CHANGELOG.md 汇总所有版本变更
- [ ] 端到端测试：SKILL 触发 → bazi_cli 调用 → 结果返回

---

## 状态标识

- ⬜ 待开始
- 🔄 进行中
- ✅ 已完成
- ❌ 已取消

---

## 命理专业层面改进清单

以下为 bazi_engine.py 在命理学术层面的已知不足，将在对应版本中修正：

| # | 问题 | 严重度 | 计划修复版本 | 说明 |
|----|------|--------|------------|------|
| 1 | 节气判断为固定日期近似 | 中 | v1.3.0 | 当前 `determine_yuejian()` 将立春写死为2月4日，引入 ephem 精确化 |
| 2 | 大运起运年龄写死为3+10n | 高 | v1.3.0 | 应据"距节气天数÷3"计算，是命理排盘的核心参数 |
| 3 | 从格判定未实现 | 中 | v1.3.1 | 仅提及概念，未实现从旺格/从强格/从势格/从儿格算法 |
| 4 | 调候用神缺失 | 高 | v1.3.2 | 当前仅用扶抑用神，缺少《穷通宝鉴》调候用神体系 |
| 5 | 地支合化条件不完整 | 低 | 待排期 | 六合/三合/三会只检测组合，不判断化气是否成功 |
| 6 | 日柱计算基准日有限 | 低 | — | 1900-01-31基准，1900年前命例有偏差（当前不影响现代命例） |
| 7 | 流年分析太简陋 | 中 | v1.3.2 | 当前只描述五行和冲合，缺少天干地支分别作用、岁运并临 |
| 8 | 缺少命宫/胎元/身宫 | 高 | v1.1.3-v1.1.4 | 三柱完全缺失，为八字排盘基本组成部分 |

---

## 自动化执行说明

每次迭代由 cron 任务触发，执行流程：

1. 读取本 ROADMAP.md，找到第一个 `⬜ 待开始` 项
2. 将其标记为 `🔄 进行中`
3. 按照该版本的 checkbox 任务逐项实现
4. 完成后 `git add` → `git commit`（遵循 Conventional Commits）→ `git push`
5. 将其标记为 `✅ 已完成`
6. 更新 CHANGELOG.md
7. 向老板汇报进展
