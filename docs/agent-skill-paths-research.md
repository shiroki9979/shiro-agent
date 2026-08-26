# 各 Agent 平台之真實 User Skill 與 Rule 探索路徑研究報告

本文件調查並整理 Google Antigravity、Claude Code、Cursor 以及 Agent Skills 生態標準（`npx skills`）在全域（User-level / Global）與專案（Workspace-level / Project）層級之實體路徑與探索機制。

---

## 1. 探索路徑對照總表

| 平台 / 工具 | 全域 Skills 路徑 (Global User Skills) | 全域 Rules / Configs | 專案 Skills 路徑 (Workspace Skills) | 專案 Rules / Guidelines |
| :--- | :--- | :--- | :--- | :--- |
| **Antigravity (AGY)** | `~/.gemini/config/skills/<name>/SKILL.md` | `~/.gemini/config/rules/*.md`<br>`~/.gemini/config/mcp_config.json` | `.agents/skills/<name>/SKILL.md`<br>（或 `.agent/`, `_agents/`） | `AGENTS.md`<br>`GEMINI.md`<br>`.agents/rules/*.md` |
| **Claude Code** | `~/.claude/skills/<name>/SKILL.md` | `~/.claude/CLAUDE.md`<br>`~/.claude/mcp_config.json` | `.claude/skills/<name>/SKILL.md` | `CLAUDE.md` (專案根目錄) |
| **Cursor** | `~/.cursor/skills/<name>/SKILL.md`（選用） | Cursor Settings > Rules for AI<br>`~/.cursor/settings.json` | `.cursor/skills/<name>/SKILL.md` | `.cursor/rules/*.mdc`<br>`AGENTS.md` |
| **Agent Skills (CLI)** | `~/.agents/skills/<name>/SKILL.md` | `~/.agents/.skill-lock.json` | `.agents/skills/<name>/SKILL.md` | `skills-lock.json` |

---

## 2. 各平台詳細規範與實體路徑

### A. Google Antigravity (AGY / Antigravity IDE)

- **全域配置路徑 (Global Customizations Root)**：`~/.gemini/config/`
  - **Skills**：`~/.gemini/config/skills/<skill-name>/SKILL.md`
  - **Plugins**：`~/.gemini/config/plugins/<plugin-name>/`
  - **Rules**：`~/.gemini/config/rules/*.md` 或 `~/.gemini/config/GEMINI.md`
  - **MCP / Hooks**：`~/.gemini/config/mcp_config.json` 與 `~/.gemini/config/hooks.json`
- **專案配置路徑 (Workspace Customizations Root)**：
  - **Skills**：`.agents/skills/<skill-name>/SKILL.md`（支援 `.agent/`、`_agents/`、`_agent/`）
  - **Rules**：`GEMINI.md`、`AGENTS.md`、`.agents/rules/*.md`
- **優先級順序**：
  1. 專案根目錄 `.agents/`
  2. 專案明確宣告之 `skills.json` / `plugins.json`
  3. 全域目錄 `~/.gemini/config/`
  4. 應用程式內建（Built-in）技能

---

### B. Claude Code / Claude Desktop

- **全域配置路徑 (Global User Root)**：`~/.claude/`
  - **Skills**：`~/.claude/skills/<skill-name>/SKILL.md`（適用於該使用者的所有專案）
  - **全域指令**：`~/.claude/CLAUDE.md`
  - **MCP 設定**：`~/.claude/mcp_config.json` 或 `~/.claude/config.json`
- **專案配置路徑 (Project Root)**：
  - **Skills**：`.claude/skills/<skill-name>/SKILL.md`
  - **Always-on 規範**：`CLAUDE.md`（專案根目錄）

---

### C. Cursor (IDE & Agent Mode)

- **全域配置路徑**：
  - **Rules for AI**：Cursor 偏好儲存於內部組態資料庫，並透過帳號雲端同步（於 `Settings > General > Rules for AI` 中管理）。
  - **全域 Skills**：`~/.cursor/skills/<skill-name>/SKILL.md`（部分版本支援，但以專案層級最穩定）。
- **專案配置路徑 (Project Root)**：
  - **Rules**：`.cursor/rules/*.mdc`（Cursor 專屬 MDC 格式，內含 frontmatter 與 glob 匹配條件）以及相容 `AGENTS.md`、`.cursorrules`。
  - **Skills**：`.cursor/skills/<skill-name>/SKILL.md`。

---

### D. 社群標準 Agent Skills CLI (`npx skills`)

- **全域安裝 (`-g`)**：`~/.agents/skills/<skill-name>/SKILL.md`，並產生 `~/.agents/.skill-lock.json`。
- **專案本機安裝**：`./.agents/skills/<skill-name>/SKILL.md`，並產生 `./skills-lock.json`。

---

## 3. 對 `shiro-agent` 部署架構之結論與建議

1. **Skills 統一分發策略**：
   - `scripts/build.py` 將編譯聚合後的 Skills 實體複製至 `~/.agents/skills/`、`~/.gemini/config/skills/`、`~/.claude/skills/` 與 `~/.cursor/skills/`（見 [ADR-0003](adr/0003-multi-target-global-skills-dispatch.md)），各平台零配置即可探索。
2. **Rules 專屬分發策略**：
   - Antigravity 部署至 `~/.gemini/config/rules/`。
   - Cursor 部署至 `~/.cursor/rules/` 或專案 `.cursor/rules/`。
   - Claude 部署至 `~/.claude/CLAUDE.md`。
