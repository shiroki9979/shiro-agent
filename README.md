# shiro-agent

> 建立日期：2026-08-22
> 最後更新：2026-10-25

個人多 Agent（Antigravity, Codex, Cursor, Claude 等）設定與 Skills 管理庫。

透過 `shared/` 規範層維護單一真實來源（Single Source of Truth），並利用編譯/同步腳本自動展開並部署至各 Agent 全域設定或專案目錄。

---

## 目錄架構

```text
shiro-agent/
├── custom-skills/            # 自有自建 Agent Skills (原始碼目錄，支援 include 模板展開)
├── .agents/skills/           # 第三方外部 Agent Skills (由 npx skills 管理)
├── skill-addenda/            # 第三方 Skills 的本地補充段落 (編譯時附加至 SKILL.md)
├── configs/                  # 各 Agent 專屬設定與模板
│   ├── antigravity/          # Antigravity 設定 (rules, mcp, hooks)
│   ├── codex/                # Codex 全域指示 (AGENTS.md)
│   ├── cursor/               # Cursor 設定 (rules/mdc, settings)
│   └── claude/               # Claude Code / Desktop 設定 (CLAUDE.md, mcp)
├── docs/                     # 專案架構文件與決策記錄
│   ├── adr/                  # 架構決策記錄 (Architecture Decision Records)
│   ├── agents/               # Agent 工作流與儲存庫規範 (Issue Tracker, Triage, Domain)
│   ├── agent-skill-paths-research.md # 各平台 Skills 探索路徑研究
│   └── third-party-skills.md # 第三方 Agent Skills 功能與架構參考手冊
├── shared/                   # 跨 Agent 共用規範 (Single Source of Truth)
│   ├── identity.md           # 個人身分、角色與語言回覆偏好
│   └── coding-style.md       # Clean Code, DRY, SOLID, 測試規範
├── scripts/                  # 編譯與部署工具
│   └── build.py              # 模板展開、技能聚合與部署腳本
├── tests/                    # 單元測試
├── AGENTS.md                 # 專案 Agent 開發與行為指引
├── CHANGELOG.md              # 專案更新與版本日誌
├── CONTEXT.md                # 領域術語表 (Domain Language & Glossary)
├── skills-lock.json          # 第三方 Skills 來源、雜湊與鎖定檔
├── pyproject.toml            # uv / Python 專案定義
└── Makefile                  # 快捷開發與部署指令
```

---

## 快速開始

本專案使用 [`uv`](https://github.com/astral-sh/uv) 進行環境與執行管理，並提供 [`Makefile`](Makefile) 作為便捷指令入口。

### 快捷指令 (Makefile)

```bash
make build         # 重建 dist/ 的目標產物 (聚合 custom-skills 與 .agents/skills)
make deploy        # 部署至全域系統路徑，並清理已失去來源的受管檔案
make dry-run       # 預覽編譯與部署
make test          # 執行單元測試
make skills-list   # 列出已安裝之第三方 Agent Skills
make skills-add PKG=<source>  # 新增第三方 Agent Skill
make skills-update # 更新第三方 Agent Skills
make release TAG=vX.Y.Z  # 執行測試後建立註解 Git Tag（需另行推送）
make help          # 檢視所有可用指令
```

---

### 1. 編譯與預覽 (Dry-run)

預設將 `shared/` 中的規範展開，並聚合 `custom-skills/` 與 `.agents/skills/` 注入至 `dist/` 目錄：

每次編譯會先清空所選目標的輸出子目錄，再產生目前來源的檔案；來源已刪除的技能與輔助檔案不會留在舊產物中。指定 `--target skills` 時僅重建 `dist/.agents/`，其餘目標的產物保留。輸出目錄不得與專案根目錄或來源目錄重疊。

```bash
# 模擬編譯所有 Agent 設定與 Skills
uv run python scripts/build.py --dry-run
# 或使用 Makefile
make dry-run

# 指定單一目標 (如 antigravity, codex, cursor, claude, skills)
uv run python scripts/build.py --target skills --dry-run
```

`--dry-run` 仍會重新編譯 `dist/`，但只列出全域目錄的複製、備份與刪除計畫，不修改全域檔案或部署清單。

### 2. 部署至系統設定路徑

執行部署會將檔案同步至全域路徑。覆寫或刪除檔案前，預設將原內容備份至 `~/.agents/.shiro-agent-backups/<agent>/<原相對路徑>.bak`；每個檔案保留最近一次備份，可用 `--no-backup` 停用。備份集中存放，避免 `.bak` 混入技能目錄；內容與權限相同的檔案會跳過覆寫與備份。

- **Skills（全域同步分發）**：聚合自有與第三方技能並派發至：
  - `~/.agents/skills/` 與 `~/.agents/skills-lock.json`（Agent Skills CLI）
  - `~/.gemini/config/skills/`（Antigravity）
  - `~/.claude/skills/`（Claude Code）
  - Cursor 從既有的 `~/.agents/skills/` 探索，不建立 `~/.cursor/skills/` 重複副本；如需 Cloud Agents 同步，另由 Cursor 設定管理。
- **Antigravity Rules / Config**：`~/.gemini/config/rules/`、`mcp_config.json`、`hooks.json`
- **Cursor Rules / Config**：`~/.cursor/rules/`、`settings.json`
- **Claude Config**：`~/.claude/CLAUDE.md`（MCP 存於 `~/.claude.json`，須以 `claude mcp add-json --scope user` 設定，不由部署管理；詳見 [Claude Code 設定研究](docs/claude-settings-research.md)）
- **Codex Instruction**：`~/.codex/AGENTS.md`（僅編譯 `shared/identity.md` 與 `shared/coding-style.md`；不管理 Codex command rules）

Codex 使用既有的 `~/.agents/skills/` 作為全域 Skills 探索路徑，因此不會建立或同步 `~/.codex/skills/` 的重複副本。

```bash
# 部署全部 Agent 設定與 Skills
uv run python scripts/build.py --deploy
# 或使用 Makefile
make deploy

# 部署指定 Agent 或 Skills
uv run python scripts/build.py --target skills --deploy
uv run python scripts/build.py --target codex --deploy
uv run python scripts/build.py --target cursor --deploy
```

部署清單存放於 `~/.agents/.shiro-agent-deploy.json`，依 `--target` 記錄本專案部署過的檔案。後續部署會先備份、再移除該目標清單中已失去來源的檔案，並清除空的技能／規則子目錄。即使目標已沒有任何來源檔案，仍會執行清理；其他目標的紀錄與檔案保留。

清單之外的技能與檔案保留，包括另外安裝的技能、受管技能目錄中自行加入的檔案，以及舊版部署留下、尚未列入清單的技能與 `.bak`。首次使用新版會建立清單，無法自動辨認既有殘留項目的來源；刪除部署清單也會失去自動清理依據。

部署清單損壞、包含越界路徑，或待寫入／清理的路徑含符號連結時，部署會在變更全域檔案前報錯，避免影響受管範圍之外的檔案。

### 3. Agent Skills 管理

#### 自建技能（Custom Skills）

- 撰寫與驗證方法見 [技能撰寫指南](docs/skill-authoring-guide.md)；工作流來源與版本差異見 [Skills 工作流研究](docs/skills-workflow-research.md)。
- 建立於 `custom-skills/<skill-name>/SKILL.md`。
- 支援在 Markdown 檔案內使用 `<!-- INCLUDE:shared/coding-style.md -->` 等標籤引用共用規範。
- 執行 `make build` 或 `make deploy` 時會自動進行同名衝突檢查與模板展開，並聚合至 `dist/.agents/skills/` 與全域環境。

#### 第三方技能（Third-party Skills）

全面相容社群標準 Agent Skills CLI（`npx skills`）生態：

```bash
# 使用 Makefile 新增
make skills-add PKG=mattpocock/skills
make skills-add PKG=anthropics/skills
make skills-add PKG="https://github.com/vercel-labs/skills --skill find-skills"

# 或直接使用原生 CLI
npx skills add mattpocock/skills

# 列出與更新
make skills-list
make skills-update
```

---

## 執行測試

```bash
make test
# 或直接使用 uv
uv run python -m unittest discover -s tests -p "test_*.py" -v
```
