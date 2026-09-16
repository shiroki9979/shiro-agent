# Cursor 設定機制研究

> 建立日期：2026-09-16
> 最後更新：2026-09-17
> 查證範圍：僅採用 Cursor 官方文件；所有連結於 2026-09-16 存取。

## 結論摘要

Cursor 應將行為規範、Skills、MCP 與 Hooks 分開管理：User Rules 由 Customize UI 管理，Project Rules 以 `.cursor/rules/*.mdc` 版本控制；Skills 可由 `.agents/skills/` 或 `.cursor/skills/` 探索；MCP 與 Hooks 分別使用 JSON 設定檔。這些機制有不同載入範圍與優先權，不宜互相替代。[官方 Rules 文件](https://cursor.com/docs/rules)

| 需求 | 使用者層 | 專案層 |
| :--- | :--- | :--- |
| 行為規範 | Customize → Rules 的 User Rules | `.cursor/rules/*.mdc`、`AGENTS.md` |
| Skills | `~/.agents/skills/`、`~/.cursor/skills/` | `.agents/skills/`、`.cursor/skills/` |
| MCP | `~/.cursor/mcp.json` | `.cursor/mcp.json` |
| Hooks | `~/.cursor/hooks.json` | `.cursor/hooks.json` |
| Plugin | Customize 的 user scope | Customize 的 workspace scope |

## Rules 與 AGENTS.md

Cursor 的 Agent 指示來源包括 Project Rules、User Rules、Team Rules 與 `AGENTS.md`。Rule 內容會加入 Agent context，不影響 Tab；User Rules 也不適用於 Inline Edit。官方未承諾 User Rules 的本機檔案格式，因此不應由本專案 build/deploy 覆寫。[官方 Rules 文件](https://cursor.com/docs/rules)

| 類型 | 位置或管理方式 | 載入與範圍 |
| :--- | :--- | :--- |
| User Rules | Customize → Rules | 全域偏好，只供 Agent Chat 使用。 |
| Project Rules | `.cursor/rules/*.mdc` | 版本控制的專案規則；必須含 frontmatter，`.md` 會被忽略。 |
| 巢狀 Project Rules | 子目錄 `.cursor/rules/` | 相關目錄的檔案進入 context 時套用。 |
| `AGENTS.md` | 專案根與子目錄 | 純 Markdown 替代方案；子目錄規範與父層合併，較具體路徑優先。 |
| Team Rules | Cursor Dashboard | Team／Enterprise 層規則可強制啟用；優先順序為 Team → Project → User。 |

Project Rule 的 frontmatter 控制觸發：`alwaysApply: true` 每個 Chat 載入；`globs` 對應檔案進入 context 時載入；只設定 `description` 時由 Agent 決定是否套用；兩者皆無時，以 `@rule-name` 手動載入。[Rule format 與觸發規則](https://cursor.com/docs/rules)

```md
---
description: Python tests and test fixtures
globs: tests/**/*.py
alwaysApply: false
---

- Keep tests focused on public behavior.
- Prefer existing fixtures before adding new ones.
```

可用 `/create-rule` 建立 Project Rule，並在 Customize → Rules 檢查已載入規則。官方建議每個 rule 聚焦且低於 500 行。[官方 Rules 文件](https://cursor.com/docs/rules)

## Skills 與 Plugins

Cursor 會遞迴掃描以下含 `SKILL.md` 的目錄；巢狀專案目錄的 Skill 僅會在處理該目錄的檔案時出現。官方未定義同名 Skill 的選擇優先權，應避免在多個根目錄部署同名項目。[官方 Agent Skills 文件](https://cursor.com/docs/skills)

```text
.agents/skills/      # 專案
.cursor/skills/      # 專案
~/.agents/skills/    # 使用者全域
~/.cursor/skills/    # 使用者全域
```

在 Customize → Skills 可檢視已探索的 Skills，或以 `/skill-name` 手動叫用。Cloud Agents 僅會同步 `~/.cursor/skills/` 中、且在 Settings → Agents 啟用 **Sync Skills for Cloud Agents** 的 Skills；`~/.agents/skills/` 不會自動同步到雲端或遠端 SSH Agent。[官方 Agent Skills 文件](https://cursor.com/docs/skills)

Cursor Plugin 可打包 Rules、Skills、subagents、commands、MCP 與 Hooks，安裝時可選 user 或 workspace scope。本機 plugin 可放在 `~/.cursor/plugins/local/<plugin-name>/`，重載視窗後從 Customize 核對元件；Marketplace plugin 同名時優先於 local copy。[官方 Plugins 文件](https://cursor.com/docs/plugins)

```bash
# 在 Cursor 執行 Developer: Reload Window 後，於 Customize → Skills／Plugins 查核。
ls ~/.cursor/plugins/local
```

## MCP

Cursor custom MCP server 使用 JSON；專案設定適合隨 repository 版本控制，使用者設定適合個人連線定義。[官方 MCP 文件](https://cursor.com/docs/mcp)

```text
.cursor/mcp.json     # project
~/.cursor/mcp.json   # user global
```

```json
{
  "mcpServers": {
    "example": {
      "command": "npx",
      "args": ["-y", "mcp-server"]
    }
  }
}
```

Cursor 支援 `stdio`、SSE 與 Streamable HTTP。可在 Customize 停用 MCP server；停用後不會提供 context 或工具。設定支援 `${env:NAME}`、`${userHome}`、`${workspaceFolder}` 等插值。[官方 MCP 文件](https://cursor.com/docs/mcp)

## Hooks

Cursor Hooks 可在 agent loop 事件執行 command 或 prompt hook。官方優先權為 Enterprise → Team → Project → User；project hooks 只在 trusted workspace 執行。[官方 Hooks 文件](https://cursor.com/docs/hooks)

```text
~/.cursor/hooks.json                 # user
~/.cursor/hooks/<script>             # user scripts
<project>/.cursor/hooks.json         # project
<project>/.cursor/hooks/<script>     # project scripts
```

Command hook 以 JSON stdin／stdout 通訊；exit code `2` 會封鎖動作，其餘非零預設 fail-open。安全控制應設定 `failClosed: true`，並在 Customize 的 Hooks tab 與 Hooks output channel 查核。Cursor 監看 `hooks.json` 變更並自動重載。[官方 Hooks 文件](https://cursor.com/docs/hooks)

## 對本專案的配置策略

1. 維持根目錄 `AGENTS.md` 作為可跨 Agent 讀取的專案文字規範；Cursor 專屬檔案範圍規則再寫入 `.cursor/rules/*.mdc`。
2. 不嘗試 build/deploy Cursor User Rules，因官方只提供 Customize UI，未承諾可寫入的本機格式。
3. 本專案僅部署使用者全域 Skills 至 `~/.agents/skills/`，Cursor 可直接探索；若 Cloud Agents 需要個人 Skill，再由 Cursor 個別同步至 `~/.cursor/skills/`，不以 build/deploy 建立重複副本。
4. 將副作用控制放在 Hooks，而非行為 Rule；將 secrets 留在環境變數，不放入版本控制的 MCP 設定。

## 官方來源

- [Cursor Rules](https://cursor.com/docs/rules)（2026-09-16 存取）
- [Cursor Agent Skills](https://cursor.com/docs/skills)（2026-09-16 存取）
- [Cursor Plugins](https://cursor.com/docs/plugins)（2026-09-16 存取）
- [Cursor MCP](https://cursor.com/docs/mcp)（2026-09-16 存取）
- [Cursor Hooks](https://cursor.com/docs/hooks)（2026-09-16 存取）
