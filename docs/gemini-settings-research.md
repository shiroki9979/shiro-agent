# Gemini CLI 與 Antigravity CLI 設定機制研究

> 建立日期：2026-09-16
> 最後更新：2026-09-17
> 查證範圍：僅採用 Google 官方文件；所有連結於 2026-09-16 存取。

## 範圍與版本註記

本文件中的 Gemini 指 **Gemini CLI**，不是 Gemini 網頁版或 Cursor 可選模型。Google 已宣布 Gemini CLI 的一般消費者服務於 2026-06-18 停止，主要遷移目標為 **Antigravity CLI**；企業授權與特定付費 API key 的 Gemini CLI 存取仍受支援。[Google 官方遷移公告](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)

Gemini CLI 是既有安裝的維護參考；新的一般使用者部署應採 Antigravity CLI。兩者有指示檔相容層，但 settings、Skills 與 MCP 路徑不能直接互換。[Antigravity CLI 概覽](https://antigravity.google/docs/cli/overview)

| 需求 | Gemini CLI（既有） | Antigravity CLI（遷移目標） |
| :--- | :--- | :--- |
| 跨專案行為指示 | `~/.gemini/GEMINI.md` | `~/.gemini/GEMINI.md` |
| 專案行為指示 | `GEMINI.md` | `GEMINI.md`、`AGENTS.md` |
| 跨專案 Skills | `~/.gemini/skills/`、`~/.agents/skills/` alias | `~/.gemini/antigravity-cli/skills/` |
| 專案 Skills | `.gemini/skills/`、`.agents/skills/` alias | `.agents/skills/` |
| 使用者 settings | `~/.gemini/settings.json` | `~/.gemini/antigravity-cli/settings.json` |
| MCP | `settings.json` 的 `mcpServers` | `~/.gemini/config/mcp_config.json`、`.agents/mcp_config.json` |

## Gemini CLI

### GEMINI.md

Gemini CLI 預設以 `GEMINI.md` 提供模型指示；`context.fileName` 可設為單一名稱或陣列，例如同時採用 `AGENTS.md`、`CONTEXT.md` 與 `GEMINI.md`。指示內容會串接後隨 prompt 提供模型。[官方 GEMINI.md 文件](https://geminicli.com/docs/cli/gemini-md/)

```json
{
  "context": {
    "fileName": ["AGENTS.md", "CONTEXT.md", "GEMINI.md"]
  }
}
```

載入順序是全域 `~/.gemini/GEMINI.md`、workspace 與其父目錄的 context 檔、以及工具存取路徑向上至 trusted root 的 JIT context 檔。CLI footer 顯示載入檔案數，`/memory show` 顯示合併指示，`/memory reload` 重新掃描。[官方 GEMINI.md 文件](https://geminicli.com/docs/cli/gemini-md/)、[官方 CLI reference](https://geminicli.com/docs/cli/cli-reference/)

```text
/memory show
/memory reload
```

### Settings

Gemini CLI settings 為 JSON。由低至高優先權：內建預設 → system defaults → user → project → system settings → environment variables → CLI arguments。[官方 Configuration Reference](https://geminicli.com/docs/reference/configuration/)

| 層級 | Linux 位置 | 用途 |
| :--- | :--- | :--- |
| System defaults | `/etc/gemini-cli/system-defaults.json` | 可被其他層覆寫的系統預設。 |
| User | `~/.gemini/settings.json` | 使用者跨專案設定。 |
| Project | `<project>/.gemini/settings.json` | 當前專案設定，覆寫 user。 |
| System settings | `/etc/gemini-cli/settings.json` | 管理者強制設定。 |

字串設定可引用 `$VAR`、`${VAR}` 或 `${VAR:-default}`；秘密值不得提交到 repository。[官方 Configuration Reference](https://geminicli.com/docs/reference/configuration/)

### Skills、Extensions、MCP、Hooks 與 Policy

Skills 優先權由低至高為 Built-in → Extension → User → Workspace；同名時較高層版本勝出。User Skills 位於 `~/.gemini/skills/` 或 `~/.agents/skills/` alias；workspace Skills 位於 `.gemini/skills/` 或 `.agents/skills/` alias。[官方 Managing Agent Skills 文件](https://geminicli.com/docs/cli/using-agent-skills/)

```bash
gemini skills list
gemini skills link /absolute/path/to/skill
gemini skills install https://github.com/example/skill
```

Extension 可打包 prompts、MCP、commands、themes、hooks、subagents 與 Skills。安裝後為副本，以 `gemini extensions update` 更新，並在重啟 CLI session 後生效。[官方 Extension reference](https://geminicli.com/docs/extensions/reference/)

```bash
gemini extensions install https://github.com/example/extension --ref v1.2.3
gemini extensions list
gemini extensions update --all
```

MCP server 在 `settings.json` 的 `mcpServers`；可用 `gemini mcp add ... --scope user` 建立並用 `gemini mcp list` 查核，互動模式以 `/mcp reload` 重載。[官方 CLI reference](https://geminicli.com/docs/cli/cli-reference/)

Hooks 定義在 `settings.json` 的 `hooks`，總開關為 `hooksConfig.enabled`。安全封鎖需測試 exit code `2` 的行為，因其餘非零值只產生警告。[官方 Hooks reference](https://geminicli.com/docs/hooks/reference/)

命令 allow／deny／ask 不應寫在 `GEMINI.md`，而應使用 TOML Policy Engine。User policy 為 `~/.gemini/policies/*.toml`；workspace policy 目前標註為 non-functional，需使用 user 或 admin tier 才能保證行為。[官方 Policy Engine](https://geminicli.com/docs/reference/policy-engine/)

```toml
[[rule]]
toolName = "run_shell_command"
commandPrefix = "git reset --hard"
decision = "deny"
priority = 100
```

## Antigravity CLI

首次以 `agy` 啟動時可偵測 Gemini 設定並引導轉換，也可用 `agy plugin import gemini` 將 legacy extension 轉成 plugin。並非所有 Gemini CLI 實驗性 theme／視覺覆蓋都有等價支援。[官方 Gemini CLI migration 文件](https://antigravity.google/docs/cli/gcli-migration/)

```bash
agy plugin import gemini
```

Antigravity CLI 解析 workspace `GEMINI.md` 與 `AGENTS.md`，也讀取 `~/.gemini/GEMINI.md` 全域約束。因此現有共用行為規範可維持為 Markdown source。[官方 Gemini CLI migration 文件](https://antigravity.google/docs/cli/gcli-migration/)

使用者 settings 位於 `~/.gemini/antigravity-cli/settings.json`，TUI 可透過 `/config` 或 `/settings` 修改；CLI flags 只覆寫當次 session。[官方 Settings 文件](https://antigravity.google/docs/cli/settings/)

```text
/config
/settings
```

workspace Skill 位於 `.agents/skills/`，使用者全域 Skill 位於 `~/.gemini/antigravity-cli/skills/`。官方描述其 Skills 為 Markdown slash commands，不能假設與 Gemini CLI 的 `SKILL.md` 目錄格式完全等價，應以 `/` 指令清單驗證。[官方 Plugins & Skills 文件](https://antigravity.google/docs/cli/plugins/)

Plugin 位於 `~/.gemini/antigravity-cli/plugins/<plugin-name>/`，可包含 `plugin.json`、`mcp_config.json`、`hooks.json`、`skills/`、`agents/` 與 `rules/`；以 `agy plugin` 命令管理。[官方 Plugins & Skills 文件](https://antigravity.google/docs/cli/plugins/)

```bash
agy plugin list
agy plugin install /path/to/plugin
agy plugin disable example-plugin
```

MCP 採獨立設定檔：`~/.gemini/config/mcp_config.json` 為全域，`.agents/mcp_config.json` 為 workspace。使用 `/mcp` 管理與重載。[官方 Antigravity MCP 文件](https://antigravity.google/docs/cli/mcp/)

Hooks 可由 plugin `hooks.json` 或主要 settings 設定，`/hooks` 是檢視 active hooks 的入口。部署前應以 `/hooks` 與無副作用 hook 驗證，不直接搬用 Gemini CLI hooks schema。[官方 Plugins & Skills 文件](https://antigravity.google/docs/cli/plugins/)

## 對本專案的配置策略

1. 本專案目前以已安裝的 legacy `agy` 相容路徑為部署基線：Rules、MCP、Hooks 與 Skills 分別部署至 `~/.gemini/config/rules/`、`~/.gemini/config/mcp_config.json`、`~/.gemini/config/hooks.json` 與 `~/.gemini/config/skills/`。
2. 不在此階段遷移至目前 Antigravity CLI 的 `~/.gemini/antigravity-cli/`。升級 CLI 時，先以 `/settings`、`/mcp`、`/hooks` 與 Skills 指令驗證，再另行調整 build/deploy 目標。
3. `AGENTS.md` 可同時服務 Antigravity CLI；Gemini CLI 需以 `context.fileName` 明確加入才會讀取。
4. 行為與程式風格放在 context Markdown；副作用命令封鎖使用 Gemini CLI Policy Engine。Antigravity 的 hook 與 permission 規格應逐版以 `/hooks`、`/mcp` 驗證。

## 官方來源

- [Google：Gemini CLI 轉移至 Antigravity CLI](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)（2026-09-16 存取）
- [Gemini CLI Configuration Reference](https://geminicli.com/docs/reference/configuration/)（2026-09-16 存取）
- [Gemini CLI GEMINI.md](https://geminicli.com/docs/cli/gemini-md/)（2026-09-16 存取）
- [Gemini CLI Managing Agent Skills](https://geminicli.com/docs/cli/using-agent-skills/)（2026-09-16 存取）
- [Gemini CLI Extension reference](https://geminicli.com/docs/extensions/reference/)（2026-09-16 存取）
- [Gemini CLI Hooks reference](https://geminicli.com/docs/hooks/reference/)（2026-09-16 存取）
- [Gemini CLI Policy Engine](https://geminicli.com/docs/reference/policy-engine/)（2026-09-16 存取）
- [Antigravity CLI Overview](https://antigravity.google/docs/cli/overview)（2026-09-16 存取）
- [Antigravity CLI Settings](https://antigravity.google/docs/cli/settings/)（2026-09-16 存取）
- [Antigravity CLI Plugins & Skills](https://antigravity.google/docs/cli/plugins/)（2026-09-16 存取）
- [Antigravity CLI MCP](https://antigravity.google/docs/cli/mcp/)（2026-09-16 存取）
- [Antigravity CLI migration from Gemini CLI](https://antigravity.google/docs/cli/gcli-migration/)（2026-09-16 存取）
