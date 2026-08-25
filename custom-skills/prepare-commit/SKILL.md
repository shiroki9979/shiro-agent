---
name: prepare-commit
description: 準備 Git 提交前的工作流程。掃描變更、清理 Notebook 輸出、檢核文件同步狀態（sync-docs）、規劃 Branch 分支、分析 Commit 拆分策略、撰寫 CHANGELOG 條目與 Conventional Commit 訊息，並輸出安全的執行指令建議。在 git commit 前、準備提交、review 變更或規劃 branch 時使用。
---

# 提交前準備工作流程（Prepare Commit）

本技能用於指導工作區在執行 Git Commit 前的完整準備與檢查流程。透過掃描工作區變更、清理暫存與 Notebook 輸出、依據業界最佳實踐規劃 Branch 命名與 Commit 拆分，並自動生成符合規範的 CHANGELOG 條目與 Conventional Commit 訊息。

---

## 核心原則與安全邊界

1. **安全無副作用（Non-destructive Suggestions）**：本技能**絕不自動執行** `git checkout`、`git commit` 或 `git push` 等變更版本歷史之指令；僅輸出具體指令供使用者手動執行或確認。
2. **原子性提交（Atomic Commits）**：每個 Commit 應代表一個單一且完整的邏輯變更。
3. **主線保護（Mainline Protection）**：避免直接在 `main` 或 `master` 主線上進行實質程式碼提交，強制引導切出語意明確的 Topic Branch。
4. **人本日誌與規範提交（Keep a Changelog & Conventional Commits）**：日誌與 Commit 訊息皆以人類可讀為核心，清楚交代變更意圖。
5. **文件同步閉環（Documentation Sync Guardrail）**：當變更涉及公開介面、CLI 指令、設定檔或目錄架構時，依循 `sync-docs` 規範先確認專案技術文件同步狀態，確保程式碼與文件一同納入原子提交閉環。

---

## 執行流程步驟（Step-by-step Protocol）

### 步驟 0：清理 Jupyter Notebook 輸出（動態執行）

在分析變更前，檢查 `git status --short` 中是否有受影響的 `.ipynb` 檔案。若存在，優先執行清理以移除 cell outputs 與 `execution_count`，避免巨量輸出污染 Git Diff：

```bash
# 針對有變更的 notebook 檔案進行清理
uv run jupyter nbconvert --clear-output <path/to/notebook.ipynb>
# 或若未安裝 uv，嘗試使用原生 jupyter
jupyter nbconvert --clear-output <path/to/notebook.ipynb>
```

- **判斷條件**：僅在 `git status` 包含 `.ipynb` 檔案且環境支援 `nbconvert` 時執行；若無 notebook 變更則自動略過。
- **目的**：縮小 diff 體積、利於 code review，不影響本地重新執行產生結果。

---

### 步驟 1：掃描工作區變更

執行以下唯讀指令收集工作區狀態：

```bash
git branch --show-current
git status --short
git diff --stat
git diff --cached --stat
git log --oneline -5
git branch -a
```

- 若工作區**無任何變更**（`working tree clean`），直接輸出狀態並結束。
- 若有變更，分別標記 Staged（已暫存）與 Unstaged（未暫存）檔案清單。

---

### 步驟 2：分析變更範圍與影響模組

讀取變更檔案的具體 Diff（`git diff <file>` 或 `git diff --cached <file>`），歸納：

- **變更類型**：新功能（feat）、缺陷修復（fix）、重構（refactor）、文件（docs）、測試（test）、依賴/建置（chore）、效能（perf）。
- **影響模組 / Scope**：依專案架構分組（例如 `src/`、`packages/`、`configs/`、`tests/`、`shared/`）。
- **內聚關聯**：哪些檔案屬於同一功能閉環，哪些為獨立修改。
- **文件同步檢核（Docs Sync Check）**：若變更涉及對外 API 簽名、CLI 指令、設定欄位或目錄架構調整，且尚未同步更新相關文件（如 `README.md`、`docs/`），提醒使用者優先執行 `/sync-docs` 進行文件同步，避免產生落後或失效文件。

---

### 步驟 3：規劃 Branch 命名與主線檢查

根據變更內容與當前分支狀態，產出 Branch 建議：

#### 命名規範（整合 GitFlow、DeepSource 與 Git Good 標準）

- **格式**：`<category>/[<issue-id>-]<kebab-description>`
- **命名要求**：全小寫、kebab-case、2~4 個語意段、避免模糊命名（禁止 `dev/update`、`fix/misc`）。

| 類別前綴 | 適用情境 | 範例 |
| :--- | :--- | :--- |
| `feat/`（或 `feature/`, `dev/`） | 新功能開發、新實驗或跨模組特性 | `feat/123-oauth-login`、`dev/optuna-hpo` |
| `fix/`（或 `bugfix/`） | 一般功能缺陷或 Bug 修復 | `fix/gh-45-null-pointer`、`fix/jwt-expiry` |
| `hotfix/` | 線上緊急修復（直接從主線切出） | `hotfix/auth-crash-patch` |
| `docs/` | 純文件、架構規範、ADR 或計畫更新 | `docs/adr-0004-logging` |
| `refactor/` | 程式碼重構（不改變對外公開行為） | `refactor/build-pipeline` |
| `test/` | 單元測試、整合測試新增或防護網補齊 | `test/auth-coverage` |
| `chore/` | 工具配置、依賴升級或建置腳本修改 | `chore/update-uv-lock` |
| `perf/` | 效能改善與最佳化 | `perf/cache-query-results` |

#### 分支決策原則

1. **主線保護**：若目前位於 `main`、`master` 或 `release/*`，且有實質功能/修復變更，**強制建議開立新分支**。
2. **沿用現有**：若已在語意相符的 topic branch，且變更屬於同一 PR/任務範圍，**留在現有分支**。
3. **主題偏離**：若變更與目前分支主題無關，建議另開新分支，並提示先 stash 或分次提交。

---

### 步驟 4：評估 Commit 拆分策略（Atomic Commits）

檢查變更是否需要拆分為多個獨立 Commit：

#### 必須拆分的情境

- 同時包含**功能變更**與**無關的程式碼重構／格式排版調整**。
- 跨越**多個獨立模組**且各自具備獨立執行與測試能力。
- 同時包含**核心程式碼變更**與**獨立的文件／設定調整**且無強耦合。
- **測試框架修復**與**新功能實作**混雜。

#### 應合併為單一 Commit 的情境

- **高內聚閉環**：單一功能實作 + 該功能的單元測試 + 該功能的介面文件說明。

若建議拆分，為每個 Commit 明確劃分檔案範圍與暫存指令（`git add <files>`）。

---

### 步驟 5：撰寫 CHANGELOG 條目與 Commit Message

為每個規劃的 Commit 產出對應的 CHANGELOG 條目與 Conventional Commit 訊息：

#### A. CHANGELOG 條目

遵循 [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) 與 `changelog` 技能規範：

- **分流寫入**：優先探測根目錄 `CHANGELOG.md`；若為 Monorepo 且子模組目錄包含專屬 `CHANGELOG.md`，自動分流寫入該模組。
- **分類標頭**：`### Added`、`### Changed`、`### Deprecated`、`### Removed`、`### Fixed`、`### Security`。
- **條目格式**：`- <動詞起頭之繁體中文說明>（\`影響之關鍵模組/檔案\`）。`
- **位置**：寫入對應檔案的 `## [Unreleased]` 區塊頂端。

#### B. Commit Message

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

- **格式**：`<type>(<scope>): <簡述>`
- **規則**：
  - `type`：feat, fix, refactor, docs, test, chore, perf
  - `scope`：模組或目錄名稱（可選，如 `auth`、`agent`、`build`）
  - `簡述`：**正體中文**，50 字元以內，動詞開頭，不以句號結尾
  - `Body`（若有 Breaking Change 或重大背景取捨）：空一行後詳細說明

---

### 步驟 6：產出建議與可執行指令摘要

輸出格式分為三大區塊，所有待執行指令以**純文字搭配 inline code**呈現（避免 Markdown fenced block 折疊造成複製不便）：

---

## 輸出結構模板

### 區塊一：變更掃描、Branch 與拆分建議

- **目前狀態**：目前分支名稱，Staged 與 Unstaged 檔案分類摘要。
- **Branch 建議**：建議目標分支名稱（如 `feat/auth-jwt-refresh`）與推薦理由；若需切換輸出切換指令。
- **拆分規劃**：說明預計拆分為 N 個 Commit 及其原因（或說明為何維持單一 Commit）。

### 區塊二：各 Commit 之 CHANGELOG 與 Message

- **Commit 1：`<type>(<scope>): <簡述>`**
  - **CHANGELOG 分類**：`### Added` / `### Fixed` ...
  - **CHANGELOG 內容**：`- 說明文字`（標註寫入之 CHANGELOG 路徑）
  - **Commit Message**：`type(scope): 簡述`
  - **Commit Body**：（若有）
- *(若有 Commit 2, 3... 依序展開)*

### 區塊三：可執行指令摘要（純文字 + Inline Code）

按順序提供使用者可複製執行的指令清單：

- 切換分支：`git checkout -b <branch>`（若需要）
- Commit 1 暫存：`git add <file1> <file2>`
- Commit 1 提交：`git commit -m "<type>(<scope>): <簡述>"`
- *(若有其他 Commit 依序提供暫存與提交指令)*
- 可選推送：`git push -u origin <branch>`
