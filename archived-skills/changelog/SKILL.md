---
name: changelog
description: 建立與維護遵循 Keep a Changelog (1.1.0) 與 SemVer 規範之 CHANGELOG.md。在記錄 Unreleased 變更、版本發布切版（Release / Bump Version）、歷史版本歸檔拆分、初始化更新日誌或使用者提及 Changelog / 更新日誌時使用。
---

# Keep a Changelog 更新日誌規範

> 建立日期：2026-08-24
> 最後更新：2026-10-07

本技能遵循 [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) 與 [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) 規範，指導 `CHANGELOG.md` 的初始化、日常累積記錄、版本發布切版以及檔案過長時的歷史歸檔管理。

---

## 1. 核心原則（Core Principles）

1. **人本導向（For Humans, Not Machines）**：更新日誌是給使用者和開發者閱讀的，**絕對嚴禁直接傾倒 Git Log（Git log dump）**。每個項目應說明「帶來什麼價值或改變」，而非「改了哪幾行程式碼」。
2. **反向時序（Reverse Chronological）**：最新發布的版本與未發布區塊（`[Unreleased]`）永遠置於最上方。
3. **單一不可變性（Immutable Releases）**：一旦版本發布並標記日期，該版本的歷史紀錄即不可再追溯修改；後續修正應記錄於下一版本。
4. **標準分類（Standard Categories）**：嚴格使用 6 大標準分類標頭，不自創分類。
5. **語意化版本與比對連結（SemVer & Compare Links）**：遵循 `MAJOR.MINOR.PATCH` 規範，並於文件底部維護版本間的 Git 比對連結。
6. **自包含性（Self-contained Archives）**：歷史版本歸檔拆分後，每份文件保留自身使用的所有連結定義，並依所在目錄解析相對路徑，無懸空死連結。

---

## 2. 6 大標準變更分類（Change Types）

所有變更必須歸類於以下 6 種標準英文標頭之一（內文描述語言依專案主要語言撰寫）：

| 分類標頭 | 適用情境與說明 | 範例 |
| :--- | :--- | :--- |
| `### Added` | 新增的功能、模組、命令或使用者介面 | `- 新增 adr-writing 自建技能，支援 5 態生命週期管理。` |
| `### Changed` | 現有功能的邏輯變更、重構、效能改善或行為調整 | `- 調整 shared/ 模組標題階層為 H2/H3 以適配全域 Rules 語意。` |
| `### Deprecated` | 即將在未來版本中移除的功能（預先告知使用者進行遷移） | `- 標記舊版 fetch_skills.py 為廢棄狀態，將於 v0.2.0 完全移除。` |
| `### Removed` | 本版本中正式移除的功能、檔案、依賴或 API | `- 移除自研 manifest.json 解析器與舊版下載腳本。` |
| `### Fixed` | 任何錯誤修復、例外排除或非預期行為修正 | `- 修復多目標派發時全域備份檔路徑未正確解析副檔名的問題。` |
| `### Security` | 安全漏洞修復、弱點修補、相依性漏洞升級 | `- 升級套件相依性以防範路徑穿越弱點。` |

---

## 3. CHANGELOG 標準模板

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 新增 ...

### Fixed
- 修復 ...

## [1.0.0] - 2026-08-24

### Added
- 初始正式版本發布。

## Historical Releases

- [v0.x.x 歷史紀錄](docs/changelogs/CHANGELOG-v0.md)（涵蓋 v0.1.0 ~ v0.9.0）

[Unreleased]: https://github.com/<owner>/<repo>/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/<owner>/<repo>/releases/tag/v1.0.0
```

---

## 4. 核心工作流程（Standard Operating Procedures）

### SOP 1：初始化 CHANGELOG.md（全新專案）

1. 檢視專案根目錄是否已有 `CHANGELOG.md`。
2. 若無，依上方標準模板建立，包含 Preamble、`## [Unreleased]` 與當前初始版本或首個發布版本。
3. 取得專案 Git Remote URL（若有），於底部配置對應的 GitHub / GitLab 比較連結。

### SOP 2：日常記錄（記錄至 Unreleased）

當完成一項功能開發、Bug 修復或重構時：

1. **定位 Unreleased**：在 `## [Unreleased]` 區塊下找到對應的分類標頭（如 `### Added`、`### Fixed`）；若該分類不存在則新增之。
2. **轉譯 Git Log 為人本語言**：
   - 提取使用者/開發者視角的實質影響。
   - 使用簡潔的動詞起頭（新增、修復、調整、重構、移除）。
   - 附上重要 issue 或 PR 連結（例如 `([#12](https://...))`）。
3. **保持分類排序**：分類標頭建議依序排列：`Added` ➔ `Changed` ➔ `Deprecated` ➔ `Removed` ➔ `Fixed` ➔ `Security`。

### SOP 3：版本發布切版（Bump Version & Release）

當準備進行版本發布時：

1. **評估版本號（SemVer 判定）**：
   - 包含破壞性變更（Breaking Changes） ➔ **MAJOR** 升版（`X.0.0`）
   - 僅包含向後相容的新功能（`Added` / `Deprecated`） ➔ **MINOR** 升版（`0.X.0`）
   - 僅包含向後相容的修復與細節變更（`Fixed` / `Security`） ➔ **PATCH** 升版（`0.0.X`）
2. **切版搬移**：
   - 將 `## [Unreleased]` 旗下的所有分類與項目搬移至新版本標題：`## [X.Y.Z] - YYYY-MM-DD`（使用 ISO 8601 日期格式）。
   - 保留空的 `## [Unreleased]` 區塊於最上方供後續開發使用。
3. **更新底部比對連結**：
   - 更新 `[Unreleased]` 指向 `vX.Y.Z...HEAD`。
   - 新增 `[X.Y.Z]` 指向 `v<PREV>...vX.Y.Z`。
4. **長度檢查**：檢查主檔案總行數，若超過門檻則接續執行 SOP 4。

---

## 5. 長度控制與歷史歸檔指引（Long Changelog Archiving SOP）

當專案長期迭代導致 `CHANGELOG.md` 過長時，依以下流程進行結構化歸檔：

### 觸發門檻

- **行數門檻**：`CHANGELOG.md` 總行數超過 **500 ~ 800 行**。
- **體積門檻**：檔案體積大於 **50 KB**。

### 歸檔操作步驟（SOP 4）

1. **確定歸檔範圍與檔名**：
   - 依 Major 版本或年份切分早期版本，建立存放目錄 `docs/changelogs/`。
   - 命名範例：`docs/changelogs/CHANGELOG-v1.md`、`docs/changelogs/CHANGELOG-v0.md` 或 `docs/changelogs/CHANGELOG-2025.md`。
2. **遷移歷史條目與連結依賴**：
   - 將已過期的歷史版本區塊自主 `CHANGELOG.md` 剪下，寫入目標歸檔檔案中。
   - 收集移動區塊使用的所有 reference link 定義，包含版本、issue、PR、圖片及完整／折疊／簡寫引用，複製到歸檔檔；主檔仍使用的定義保留，僅刪除主檔已無引用的定義。
   - 依移動前的文件位置解析行內連結、圖片及連結定義的目標，再改寫為相對於歸檔目錄的路徑，保留查詢參數與錨點。例如根目錄的 `docs/guide.md#usage` 搬到 `docs/changelogs/` 後改為 `../guide.md#usage`。
   - 頁內錨點依目標標題的實際去向調整；主檔指向已搬移標題的連結也需更新。保留歷史條目語意，僅調整搬移所需的連結位置。
3. **建立主檔索引連結**：
   - 在主 `CHANGELOG.md` 底部（在比對連結上方）建立 `## Historical Releases` 區塊。
   - 加入指向該歸檔檔案之相對路徑連結與版本涵蓋說明（例如 `- [v1.x.x 歷史紀錄](docs/changelogs/CHANGELOG-v1.md)`）。
4. **驗證搬移結果**：
   - 比對搬移前後的版本與條目，確認無遺漏或重複；逐份檢查引用定義、相對路徑與錨點，確認仍指向原本目標。
   - 缺少定義或無法確認目標時，列出所在檔案、引用與原因，回報歸檔驗證未完成。

---

## 6. Git Log 轉譯轉化指引

| 原始 Git Commit（禁止直接照搬） | 分類 | Keep a Changelog 條目範例 |
| :--- | :--- | :--- |
| `fix: change regex in utils.py line 42` | `Fixed` | `- 修復包含特殊字元的路徑解析失敗問題。` |
| `feat: add adr-writing/SKILL.md and tests` | `Added` | `- 新增架構決策紀錄（ADR）撰寫技能，支援 5 態生命週期與三大門檻檢核。` |
| `refactor: extract helper function` | `Changed` | `- 重構技能編譯管線，提升模板遞迴展開效能。` |
| `wip: update stuff` | （略過） | 忽略內部中間過渡 commit，僅提煉最終對外具體變更。 |

---

## 7. 品質驗收檢核表（Quality Checklist）

在完成 CHANGELOG.md 的編輯、切版或歸檔後，依序檢核：

| 檢核項目 | 合格標準 |
| :--- | :--- |
| **頂層格式** | 包含 Keep a Changelog 與 SemVer 宣告前言 |
| **Unreleased 存在** | 頂部保留 `## [Unreleased]` 區塊 |
| **日期格式** | 已發布版本標題符合 `## [X.Y.Z] - YYYY-MM-DD`（ISO 8601） |
| **分類精確** | 僅使用 6 大標準英文分類（`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`） |
| **人本語意** | 條目清楚揭露影響與價值，無原始 commit hash 堆砌 |
| **連結有效** | 版本與 Unreleased 具備 compare / tag 連結；每份文件使用的引用定義完整，相對路徑與錨點仍指向正確目標，未驗證項目已明列 |
| **歸檔完整** | 超過 500~800 行時已於 `docs/changelogs/` 建立歸檔檔，主檔包含 `## Historical Releases` 導覽且無懸空連結 |
