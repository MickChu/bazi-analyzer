# CHANGELOG

所有值得注意的变更记录于此，遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

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
