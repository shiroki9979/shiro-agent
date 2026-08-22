# shiro-agent

個人多 Agent（Antigravity, Cursor, Claude 等）設定與 Skills 管理庫。

透過 `shared/` 規範層維護單一真實來源（Single Source of Truth），並利用編譯/同步腳本自動展開並部署至各 Agent 全域設定或專案目錄。

---

## 目錄架構

```text
shiro-agent/
├── custom-skills/            # 自有自建 Agent Skills (原始碼目錄，支援 include 模板展開)
├── .agents/skills/           # 第三方外部 Agent Skills (由 npx skills 管理)
├── configs/                  # 各 Agent 專屬設定與模板
│   ├── antigravity/          # Antigravity 設定 (rules, mcp, hooks)
│   ├── cursor/               # Cursor 設定 (rules/mdc, settings)
│   └── claude/               # Claude Code / Desktop 設定 (CLAUDE.md, mcp)
├── docs/                     # 專案架構文件與決策記錄
│   └── adr/                  # 架構決策記錄 (Architecture Decision Records)
├── shared/                   # 跨 Agent 共用規範 (Single Source of Truth)
│   ├── identity.md           # 個人身分、角色與語言回覆偏好
│   ├── coding-style.md       # Clean Code, DRY, SOLID, 測試規範
│   └── workflows/            # 通用工作流程
│       ├── grill-me.md       # Grill Me 設計樹與邊界決策流程
│       └── grill-with-docs.md# Grill With Docs 與架構決策 (ADR) 規範
├── scripts/                  # 編譯與部署工具
│   └── build.py              # 模板展開、技能聚合與部署腳本
├── tests/                    # 單元測試
├── CONTEXT.md                # 領域術語表 (Domain Language & Glossary)
├── skills-lock.json          # 第三方 Skills 來源、雜湊與鎖定檔
├── pyproject.toml            # uv / Python 專案定義
└── Makefile                  # 快捷開發與部署指令
```

---

## 快速開始

本專案使用 [`uv`](https://github.com/astral-sh/uv) 進行環境與執行管理，並提供 [`Makefile`](file:///home/shiro/repos/shiro-agent/Makefile) 作為便捷指令入口。

### 快捷指令 (Makefile)

```bash
make build         # 編譯所有設定至 dist/ (聚合 custom-skills 與 .agents/skills)
make deploy        # 編譯並部署至全域系統路徑 (~/.agents, ~/.gemini/config, ~/.cursor, ~/.claude)
make dry-run       # 預覽編譯與部署
make test          # 執行單元測試
make skills-list   # 列出已安裝之第三方 Agent Skills
make skills-add PKG=<source>  # 新增第三方 Agent Skill
make skills-update # 更新第三方 Agent Skills
make help          # 檢視所有可用指令
```

---

### 1. 編譯與預覽 (Dry-run)

預設將 `shared/` 中的規範展開，並聚合 `custom-skills/` 與 `.agents/skills/` 注入至 `dist/` 目錄：

```bash
# 模擬編譯所有 Agent 設定與 Skills
uv run python scripts/build.py --dry-run
# 或使用 Makefile
make dry-run

# 指定單一目標 (如 antigravity, cursor, claude, skills)
uv run python scripts/build.py --target skills --dry-run
```

### 2. 部署至系統設定路徑

執行部署會將檔案同步至全域路徑（預設會自動建立 `.bak` 備份）：

- **Skills 與 Lock 檔**: `~/.agents/skills/`（聚合自有與第三方技能）與 `~/.agents/skills-lock.json`
- **Antigravity**: `~/.gemini/config/`
- **Cursor**: `~/.cursor/`
- **Claude**: `~/.claude/`

```bash
# 部署全部 Agent 設定與 Skills
uv run python scripts/build.py --deploy
# 或使用 Makefile
make deploy

# 部署指定 Agent 或 Skills
uv run python scripts/build.py --target skills --deploy
uv run python scripts/build.py --target cursor --deploy
```

### 3. Agent Skills 管理

#### 自建技能（Custom Skills）
- 建立於 `custom-skills/<skill-name>/SKILL.md`。
- 支援在 Markdown 檔案內使用 `<!-- INCLUDE:shared/coding-style.md -->` 等標籤引用共用規範。
- 執行 `make build` 或 `make deploy` 時會自動進行同名衝突檢查與模板展開，並聚合至 `dist/.agents/skills/` 與全域環境。

#### 第三方技能（Third-party Skills）
全面相容社群標準 Agent Skills CLI（`npx skills`）生態：

```bash
# 使用 Makefile 新增
make skills-add PKG=mattpocock/skills
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
