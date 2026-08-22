# shiro-agent

個人多 Agent（Antigravity, Cursor, Claude 等）設定與 Skills 管理庫。

透過 `shared/` 規範層維護單一真實來源（Single Source of Truth），並利用編譯/同步腳本自動展開並部署至各 Agent 全域設定或專案目錄。

---

## 目錄架構

```text
shiro-agent/
├── configs/                  # 各 Agent 專屬設定與模板
│   ├── antigravity/          # Antigravity 設定 (rules, mcp, hooks)
│   ├── cursor/               # Cursor 設定 (rules/mdc, settings)
│   └── claude/               # Claude Code / Desktop 設定 (CLAUDE.md, mcp)
├── shared/                   # 跨 Agent 共用規範 (Single Source of Truth)
│   ├── identity.md           # 個人身分、角色與語言回覆偏好
│   ├── coding-style.md       # Clean Code, DRY, SOLID, 測試規範
│   └── workflows/            # 通用工作流程
│       ├── grill-me.md       # Grill Me 設計樹與邊界決策流程
│       └── grill-with-docs.md# Grill With Docs 與架構決策 (ADR) 規範
├── skills/                   # Skills 庫
│   ├── curated/              # 自建與精選 Skills
│   ├── third-party/          # 外部第三方 Skills (自動下載)
│   └── manifest.json         # 第三方 Skills 來源與清單
├── scripts/                  # 編譯、部署與同步工具
│   ├── build.py              # 模板展開與部署腳本
│   └── fetch_skills.py       # 第三方 Skills 下載器
├── tests/                    # 單元測試
└── pyproject.toml            # uv / Python 專案定義
```

---

## 快速開始

本專案使用 [`uv`](https://github.com/astral-sh/uv) 進行環境與執行管理，並提供 [`Makefile`](file:///home/shiro/repos/shiro-agent/Makefile) 作為便捷指令入口。

### 快捷指令 (Makefile)

```bash
make build         # 編譯所有設定至 dist/
make deploy        # 編譯並部署至全域系統路徑 (~/.gemini/config, ~/.cursor, ~/.claude)
make dry-run       # 預覽編譯與部署
make test          # 執行單元測試
make skills-fetch  # 下載所有啟用的第三方 Skills
make help          # 檢視所有可用指令
```

---

### 1. 編譯與預覽 (Dry-run)

預設將 `shared/` 中的規範展開注入至 `dist/` 目錄：

```bash
# 模擬編譯所有 Agent 設定
uv run python scripts/build.py --dry-run
# 或使用 Makefile
make dry-run

# 指定單一 Agent (如 antigravity, cursor, claude)
uv run python scripts/build.py --target antigravity --dry-run
```

### 2. 部署至系統設定路徑

執行部署會將檔案同步至全域路徑（預設會自動建立 `.bak` 備份）：

- **Antigravity**: `~/.gemini/config/`
- **Cursor**: `~/.cursor/`
- **Claude**: `~/.claude/`

```bash
# 部署全部 Agent 設定
uv run python scripts/build.py --deploy
# 或使用 Makefile
make deploy

# 部署指定 Agent
uv run python scripts/build.py --target cursor --deploy
```

### 3. 第三方 Skills 管理

#### 一鍵新增與部署（一步到位）

支援 skills.sh 簡寫語法（`owner/repo@skill`）、`--skill` 參數或 GitHub 連結，自動寫入清單、下載並部署至全域：

```bash
# 新增並自動部署至全域 Antigravity 設定
uv run python scripts/fetch_skills.py add vercel-labs/agent-skills@find-skills --deploy

# 僅下載並記錄至 manifest.json
uv run python scripts/fetch_skills.py add vercel-labs/agent-skills@find-skills
```

#### 手動設定 `skills/manifest.json`

亦可在 `skills/manifest.json` 中手動填寫（`destination` 預設為 `skills/third-party/<name>/SKILL.md`，`enabled` 預設為 `true`，皆可省略）：

```json
{
  "skills": [
    {
      "name": "find-skills",
      "source": "vercel-labs/agent-skills@find-skills"
    }
  ]
}
```

#### 批次操作指令

```bash
# 列出清單中所有 Skills
uv run python scripts/fetch_skills.py --list

# 下載所有已啟用的 Skills
uv run python scripts/fetch_skills.py --all

# 下載指定 Skill
uv run python scripts/fetch_skills.py --name <skill-name>
```

---

## 執行測試

```bash
uv run python -m unittest discover -s tests -p "test_*.py" -v
```
