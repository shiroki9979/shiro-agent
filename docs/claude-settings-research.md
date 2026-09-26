# Claude Code 設定機制研究

> 建立日期：2026-09-26
> 最後更新：2026-09-26
> 查證範圍：僅採用 Anthropic 官方 Claude Code 文件（`code.claude.com/docs`）與官方 JSON Schema（SchemaStore 上由文件指向之 `claude-code-settings.json`）；所有連結於 2026-09-26 存取。本機 `~/.claude/` 僅觀察目錄結構，未讀取憑證或私人內容。

## 結論摘要

Claude Code 將「行為指示」、「設定」、「MCP」、「Skills／Subagents」與「應用程式狀態」分放於不同檔案，且其中兩個檔案（`~/.claude/settings.json`、`~/.claude.json`）會被 Claude Code 自行回寫，不宜由 build/deploy 整檔覆寫。[官方 .claude directory 文件](https://code.claude.com/docs/en/claude-directory)

| 需求 | 使用者層位置 | 專案層位置 | 本專案現況 |
| :--- | :--- | :--- | :--- |
| 跨專案行為指示 | `~/.claude/CLAUDE.md` | `./CLAUDE.md`、`./.claude/CLAUDE.md`、`AGENTS.md`（條件式） | 已部署 `~/.claude/CLAUDE.md` |
| 主題式／路徑條件規則 | `~/.claude/rules/*.md` | `.claude/rules/*.md` | 未使用 |
| 權限、hooks、env、model 等設定 | `~/.claude/settings.json` | `.claude/settings.json`、`.claude/settings.local.json` | 未管理 |
| MCP servers | `~/.claude.json`（user／local scope） | `.mcp.json`（專案根） | 不由部署管理（原 `~/.claude/mcp_config.json` 部署已移除） |
| Skills | `~/.claude/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | 已部署（實體複製） |
| Slash commands（舊格式） | `~/.claude/commands/*.md` | `.claude/commands/*.md` | 未使用 |
| Subagents | `~/.claude/agents/*.md` | `.claude/agents/*.md` | 未使用 |
| 應用程式狀態、OAuth、信任紀錄 | `~/.claude.json` | — | 不應觸碰 |

## 記憶／規則檔（CLAUDE.md）

### 層級與載入順序

官方依「最廣 → 最具體」列出四層，後載入者在 context 中出現較晚。[官方 Memory 文件](https://code.claude.com/docs/en/memory)

| Scope | 位置 | 用途 |
| :--- | :--- | :--- |
| Managed policy | Linux／WSL：`/etc/claude-code/CLAUDE.md`；macOS：`/Library/Application Support/ClaudeCode/CLAUDE.md`；Windows：`C:\Program Files\ClaudeCode\CLAUDE.md` | 組織層，無法被個人設定排除 |
| User | `~/.claude/CLAUDE.md` | 個人跨專案偏好 |
| Project | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 團隊共享、版本控制 |
| Local | `./CLAUDE.local.md` | 個人專案偏好，應加入 `.gitignore` |

- Claude Code 從工作目錄往上每層讀取 `CLAUDE.md` 與 `CLAUDE.local.md`，全部**串接**而非互相覆寫；順序由檔案系統根目錄往工作目錄，同目錄內 `CLAUDE.local.md` 接在 `CLAUDE.md` 之後。子目錄中的 `CLAUDE.md` 則在 Claude 讀取該子目錄檔案時才按需載入。[官方 Memory 文件](https://code.claude.com/docs/en/memory)
- Block-level HTML 註解（`<!-- ... -->`）在注入 context 前會被移除，code block 內的註解保留。[官方 Memory 文件](https://code.claude.com/docs/en/memory)
- 建議每個 CLAUDE.md 低於 200 行；超過 4 MiB 的檔案會被略過。CLAUDE.md 以 user message 形式在 system prompt 之後提供，非強制設定；需強制時應改用 hook 或 `permissions`。[官方 Memory 文件](https://code.claude.com/docs/en/memory)
- 以 `/memory` 或 `/context`（**Memory files** 區）確認實際載入的檔案。[官方 Memory 文件](https://code.claude.com/docs/en/memory)

### `@path` import 語法

- 可在 CLAUDE.md 任意位置以 `@path/to/file` 引入其他檔案，於啟動時展開載入。
- 支援相對與絕對路徑（含 `@~/...`）；**相對路徑以「含 import 的檔案」為基準**，而非工作目錄。
- 可遞迴引入，**最大深度四層（four hops）**。
- Markdown code span 與 fenced code block 內不解析 import；以反引號包住可保留字面。
- 專案層檔案引入工作目錄外的路徑視為 external import，首次會跳出核准對話框；使用者層檔案（`~/.claude/CLAUDE.md`、`~/.claude/rules/`）的 import 不需核准（Cowork 桌面 session 例外）。
- Import 只協助組織內容，不降低 context 消耗。

[官方 Memory 文件](https://code.claude.com/docs/en/memory)

### `.claude/rules/` 與 `~/.claude/rules/`

- 專案 `.claude/rules/` 下所有 `.md` 會遞迴探索；無 `paths` frontmatter 的規則於啟動時載入，優先權同 `.claude/CLAUDE.md`。
- `paths` 是規則唯一會被讀取的 frontmatter 欄位（接受 YAML list 或逗號分隔字串，支援 glob 與 brace expansion）；有 `paths` 的規則在 Claude **讀取**符合檔案時才載入。YAML 解析失敗時視為無 `paths`。
- 支援 symlink；指向工作目錄外的 symlink 視同 external import，需核准後才載入，且核准後只載入無 `paths` 的規則。
- 使用者層規則放在 `~/.claude/rules/`，套用至所有專案，且在專案規則**之前**載入；兩者衝突時不保證採用哪一條。

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Development Rules
- All API endpoints must include input validation
```

[官方 Memory 文件](https://code.claude.com/docs/en/memory)

### 是否讀取 AGENTS.md

Claude Code v2.1.277 起可直接讀取 `AGENTS.md`，行為由內建 `agents-md` plugin 的 **Project instructions** 設定決定。[官方 Memory 文件](https://code.claude.com/docs/en/memory)

| 值 | 行為 |
| :--- | :--- |
| `claude-md-or-agents-md`（預設） | 工作目錄或其上層**沒有** `CLAUDE.md`／`.claude/CLAUDE.md`／`CLAUDE.local.md` 時才讀 `AGENTS.md` |
| `claude-md-and-agents-md` | 兩者都讀，同目錄先 `CLAUDE.md` 後 `AGENTS.md`，已載入者不重複 |
| `claude-md` | 只讀 `CLAUDE.md` |
| `managed-only` | 只讀 managed CLAUDE.md 與 auto memory |

- 判斷「是否已有 CLAUDE.md」時，`~/.claude/CLAUDE.md`、managed CLAUDE.md 與 `.claude/rules/` **不計入**，因此使用者層 CLAUDE.md 不會阻擋專案 `AGENTS.md` 載入。
- 不讀 `AGENTS.local.md`、`AGENTS.override.md`，也不讀 `.agents/` 目錄下任何內容。
- 設定可寫在 `~/.claude/settings.json` 的 `pluginConfigs["agents-md@builtin"].options.instructionFiles`；專案與 local settings 中此鍵會被忽略。
- 版本較舊或停用 `agents-md` plugin 的 session 只讀 CLAUDE.md；此時官方建議在 `CLAUDE.md` 中寫 `@AGENTS.md`（import 不會造成重複讀取）。

```json
{
  "pluginConfigs": {
    "agents-md@builtin": {
      "options": { "instructionFiles": "claude-md-and-agents-md" }
    }
  }
}
```

[官方 Memory 文件](https://code.claude.com/docs/en/memory)；[官方 Settings reference：pluginConfigs](https://code.claude.com/docs/en/settings-reference)

### Auto memory（與本專案管理範圍的界線）

Auto memory 由 Claude 自行寫入 `~/.claude/projects/<project>/memory/`（`MEMORY.md` 前 200 行或 25KB 於每次 session 載入），開關 `autoMemoryEnabled` 由 `/memory` 寫入 `~/.claude/settings.json`。此目錄屬執行期資料，不應由 build/deploy 管理。[官方 Memory 文件](https://code.claude.com/docs/en/memory)

## settings.json

### 位置與優先序

| 優先序（高 → 低） | 來源 |
| :--- | :--- |
| 1 | Managed settings（`managed-settings.json`、MDM、claude.ai console） |
| 2 | 命令列參數（含 `--settings <file-or-json>`） |
| 3 | `.claude/settings.local.json`（Project local） |
| 4 | `.claude/settings.json`（Shared project） |
| 5 | `~/.claude/settings.json`（User） |

- 陣列型鍵（如 `permissions.allow`）跨層**合併**而非覆寫；`hooks` 也跨檔合併。少數模型相關鍵（`fallbackModel`、`modelPicker`、`availableModels` 等）有個別規則。
- 環境變數不屬於此堆疊，與設定鍵的關係逐對定義（例如 shell 中的 `ANTHROPIC_MODEL` 優先於任何檔案的 `model`）。
- Claude Code 監看設定檔並熱重載大多數變更（含 `permissions`、`hooks`）；`model`、`effortLevel` 等少數鍵僅於啟動時讀取。
- 以 `/status` 的 `Setting sources` 行確認載入哪些檔案；`claude doctor` 列出被拒絕的項目。
- 設定檔為嚴格 JSON，註解或尾逗號會造成 Settings Error。

[官方 Settings 文件](https://code.claude.com/docs/en/settings)

**重要**：`/config`、`/model`、`/memory` 的 auto memory 開關、plugin `userConfig` 對話框等會**回寫** `~/.claude/settings.json`；若該檔由其他工具產生或為唯讀連結，變更只在當前 session 生效。[官方 Settings 文件](https://code.claude.com/docs/en/settings)；[官方 Settings reference：pluginConfigs](https://code.claude.com/docs/en/settings-reference)

### 主要欄位

| 鍵 | 說明 | Scope |
| :--- | :--- | :--- |
| `$schema` | 指向 `https://json.schemastore.org/claude-code-settings.json`，提供編輯器自動完成與驗證 | — |
| `permissions.allow` / `ask` / `deny` | 規則格式 `Tool` 或 `Tool(specifier)`；評估順序 deny → ask → allow，第一個符合者決定 | Any file |
| `permissions.defaultMode` | `default`、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions`、`manual`；`auto` 與 `bypassPermissions` 只在使用者層等生效 | Any file |
| `permissions.additionalDirectories` | 授予額外目錄的檔案存取（不載入其設定） | Any file |
| `env` | 每個 session 與子程序的環境變數；專案／local 層無法設定部分敏感變數 | Any file |
| `hooks` | 以事件為鍵、`{matcher, hooks}` 陣列為值；handler 類型 `command`、`prompt`、`agent`、`http`、`mcp_tool` | Any file |
| `model` | 新 session 預設模型 | Any file |
| `language` | 預設回覆語言，原樣傳給 Claude | Any file |
| `statusLine` | `{"type":"command","command":...}`，可選 `padding`、`refreshInterval` | Any file |
| `claudeMdExcludes` | 以 glob 排除特定 CLAUDE.md／rules | Any file |
| `skillOverrides` | 以 skill 名稱設 `on`／`name-only`／`user-invocable-only`／`off` | Any file |
| `autoMemoryEnabled` / `autoMemoryDirectory` | auto memory 開關與位置 | Any file |
| `attribution` | commit／PR 署名 | Any file |
| `pluginConfigs` / `enabledPlugins` | plugin 設定與啟用 | `pluginConfigs` 僅 User 或 managed |

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

[官方 Settings reference](https://code.claude.com/docs/en/settings-reference)；[官方 Settings 文件](https://code.claude.com/docs/en/settings)

官方 JSON Schema 為 draft-07、標題 `Claude Code Settings`，2026-09-26 取得版本含 142 個頂層屬性，包含上表各鍵，但**不含** `mcpServers`。[SchemaStore：claude-code-settings.json](https://json.schemastore.org/claude-code-settings.json)

### `~/.claude.json`（全域設定檔，非 settings.json）

`~/.claude.json` 由 Claude Code 自行維護，保存登入 session、MCP server、各專案狀態（如信任決定）與 `/config` 寫入的 global config 鍵（如 `autoConnectIde`、`diffTool`）；這些鍵放在 `settings.json` 會被忽略。Claude Code 改寫時會在 `~/.claude/backups/` 保留最近五份備份，解析失敗時會另存 `.corrupted` 副本。官方明示不要刪除此檔。[官方 Settings 文件](https://code.claude.com/docs/en/settings)；[官方 Settings reference：Global config settings](https://code.claude.com/docs/en/settings-reference)；[官方 .claude directory 文件](https://code.claude.com/docs/en/claude-directory)

本機觀察：`~/.claude.json` 頂層含 `oauthAccount`、`userID`、多種快取與遷移旗標等狀態鍵，符合上述描述。

## MCP

### 安裝 scope 與儲存位置

| Scope | 載入範圍 | 儲存位置 |
| :--- | :--- | :--- |
| Local（預設） | 僅當前專案 | `~/.claude.json` 的 `projects["<path>"].mcpServers` |
| Project | 僅當前專案、隨版本控制共享 | 專案根 `.mcp.json` |
| User | 所有專案 | `~/.claude.json` 頂層 `mcpServers` |

- 同名 server 定義於多處時，只取最高優先來源的**整筆**定義，欄位不跨層合併；順序為 Local → Project → User → Plugin 提供 → claude.ai connectors（managed `managedMcpServers` 更高）。
- `claude mcp add --scope user ...` 與 `claude mcp add-json <name> '<json>' --scope user` 會寫入 `~/.claude.json`；`add-json` 接受的是 `mcpServers` 內部的單筆物件，不含外層 wrapper。
- `.mcp.json` 支援 `${VAR}` 與 `${VAR:-default}` 展開（`command`、`args`、`env`、`url`、`headers`）；專案 server 在互動 session 首次使用前需核准。
- `--mcp-config <file...>` 可在單次 session 從 JSON 檔載入 MCP server；`--strict-mcp-config` 只使用該旗標指定的 server。

[官方 MCP 文件](https://code.claude.com/docs/en/mcp)；[官方 CLI reference](https://code.claude.com/docs/en/cli-reference)

### `configs/claude/mcp_config.json` 評估

- 目前 `compile_claude()` 將 `configs/claude/mcp_config.json` 部署為 `~/.claude/mcp_config.json`。
- 官方 MCP、Settings、Settings reference、`.claude` directory、CLI reference 等文件中**均未出現** `mcp_config.json` 或 `~/.claude/` 下任何 MCP 設定檔；官方列出的使用者層 MCP 位置只有 `~/.claude.json`。[官方 MCP 文件](https://code.claude.com/docs/en/mcp)；[官方 .claude directory 文件](https://code.claude.com/docs/en/claude-directory)
- Settings schema 不含 `mcpServers`，因此改放入 `~/.claude/settings.json` 亦非官方支援的做法。[SchemaStore：claude-code-settings.json](https://json.schemastore.org/claude-code-settings.json)
- 結論：`~/.claude/mcp_config.json` **不會**被 Claude Code 自動讀取；除非每次以 `claude --mcp-config ~/.claude/mcp_config.json` 啟動。現況檔案內容為空 `{"mcpServers": {}}`，故尚無實際影響。
- `mcp_config.json` 是 Antigravity 的檔名慣例（見 [gemini-settings-research.md](gemini-settings-research.md)），Claude 端沿用屬誤植。

## Skills、Commands、Subagents 與 Plugins

### Skills 位置與結構

| Location | 路徑 | 載入範圍 |
| :--- | :--- | :--- |
| Enterprise | managed settings 目錄下 `.claude/skills/<name>/SKILL.md` | 組織部署之機器 |
| Personal | `~/.claude/skills/<name>/SKILL.md` | 本機所有專案（不含 Cowork／cloud session） |
| Project | `.claude/skills/<name>/SKILL.md` | 本 repository；從啟動目錄往上至 repo root |
| Nested | `<subdir>/.claude/skills/<name>/SKILL.md` | Claude 處理該子目錄檔案時載入 |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | 以 `/plugin-name:skill-name` 命名空間 |
| claude.ai 帳號 | 同步下載至 `~/.claude/skills/synced/` | Cowork、cloud、登入之終端 session |

- 同名時：Enterprise > Personal > Project；skill 與 `.claude/commands/` 同名時取 skill；plugin skill 因命名空間可並存。
- `<name>` 目錄**可為 symlink**，Claude Code 從目標讀取 `SKILL.md`，多處指向同一目標時只載入一次。
- 保留名稱：`synced`（任何大小寫）與 `anthropic-skills` 開頭者不得作為 skill 目錄名。
- `SKILL.md` 文字變更有 live change detection，session 中即時生效。
- 官方列出的探索路徑**不含** `~/.agents/skills/`；Memory 文件亦明示不讀 `.agents/` 目錄下內容。因此 Claude Code 需要 `~/.claude/skills/` 的副本或 symlink。

[官方 Skills 文件](https://code.claude.com/docs/en/skills)；[官方 Memory 文件](https://code.claude.com/docs/en/memory)

### SKILL.md frontmatter

全部欄位皆選填，僅建議提供 `description`；未知欄位會被靜默忽略，YAML 解析失敗時 skill 仍載入但無欄位。

| 欄位 | 用途 |
| :--- | :--- |
| `name` | `/` 選單名稱，預設為目錄名 |
| `description` | 觸發判斷依據；與 `when_to_use` 合計於清單中截斷至 1,536 字元 |
| `when_to_use` | 額外觸發情境，附加於 description |
| `argument-hint`、`arguments` | 參數提示與具名參數替換 |
| `disable-model-invocation` | `true` 時僅能手動 `/name` 觸發 |
| `user-invocable` | `false` 時自 `/` 選單隱藏 |
| `allowed-tools`、`disallowed-tools` | 本輪預先核准／移除的工具 |
| `model`、`effort` | 本輪模型與 effort 覆寫 |
| `context`、`agent`、`background` | `context: fork` 時於 subagent 執行 |
| `hooks`、`paths`、`shell` | skill 級 hooks、路徑條件啟用、inline shell 類型 |
| `metadata`、`license`、`compatibility` | Agent Skills 規格欄位，Claude Code 接受但不作用 |

若 skill 同時要上傳 claude.ai 或經 Skills API 使用，只能用 `name`、`description`、`license`、`compatibility`、`metadata`、`allowed-tools` 六個欄位，其他欄位會造成上傳硬錯誤。[官方 Skills 文件](https://code.claude.com/docs/en/skills)

### 與 commands、subagents、plugins 的關係

- **Commands**：自訂 commands 已併入 skills。`~/.claude/commands/<name>.md` 與 `~/.claude/skills/<name>/SKILL.md` 都建立 `/name`，commands 支援 skill frontmatter（`name`、`paths` 除外）但無 supporting files；新工作建議用 skill。[官方 Skills 文件](https://code.claude.com/docs/en/skills)
- **Subagents**：`~/.claude/agents/*.md`（使用者層，優先序 4）與 `.claude/agents/*.md`（專案層，優先序 3），遞迴掃描、以 frontmatter `name` 識別；frontmatter 含 `name`、`description`、`tools`、`model`、`skills`、`mcpServers`、`hooks`、`memory` 等。若 session 啟動時 `~/.claude/agents/` 不存在，新建後需重啟。[官方 Subagents 文件](https://code.claude.com/docs/en/sub-agents)；[官方 .claude directory 文件](https://code.claude.com/docs/en/claude-directory)
- **Plugins**：以 `.claude-plugin/plugin.json` 為 manifest，將 skills、agents、hooks、MCP servers 打包成單位，透過 marketplace 或本機資料夾安裝，安裝內容存於 `~/.claude/plugins/`（由 `claude plugin` 指令管理）。單純的 skill、subagent、hook、MCP 不需 plugin 即可運作。[官方 Plugins 文件](https://code.claude.com/docs/en/plugins)；[官方 .claude directory 文件](https://code.claude.com/docs/en/claude-directory)

## 對本專案的建議

### build/deploy 產出對照

| 產出 | 部署路徑 | 建議做法 | 理由 |
| :--- | :--- | :--- | :--- |
| `configs/claude/CLAUDE.md`（展開 include） | `~/.claude/CLAUDE.md` | **維持**整檔覆寫 | 使用者手寫檔，Claude Code 不回寫；與 Codex `~/.codex/AGENTS.md` 對稱 |
| Skills | `~/.claude/skills/<name>/` | **維持**（ADR-0003） | Claude Code 不探索 `~/.agents/skills/` |
| `configs/claude/mcp_config.json` | `~/.claude/mcp_config.json` | **已移除**此部署與來源檔 | 官方不讀取此檔 |
| MCP servers（若日後需要） | `~/.claude.json` 頂層 `mcpServers` | 以 `claude mcp add-json --scope user` 寫入，不直接改檔 | `~/.claude.json` 含 OAuth 與狀態，由 Claude Code 維護 |
| `configs/claude/settings.json`（選用） | `~/.claude/settings.json` | 若要管理，採**鍵層級合併**而非整檔覆寫 | Claude Code 會回寫此檔 |
| `configs/claude/rules/*.md`（選用） | `~/.claude/rules/` | 可選 | 見下方取捨 |

### 不應覆寫或管理的路徑

- `~/.claude.json`：OAuth、userID、專案信任、MCP、global config。
- `~/.claude/.credentials.json`：登入憑證。
- `~/.claude/projects/`（含 auto memory）、`~/.claude/plugins/`、`~/.claude/backups/`、`~/.claude/sessions/`、`history.jsonl` 等執行期資料。
- `~/.claude/skills/synced/`：claude.ai 同步 skills 的保留目錄。

[官方 .claude directory 文件](https://code.claude.com/docs/en/claude-directory)；[官方 Skills 文件](https://code.claude.com/docs/en/skills)

### 需決策事項與取捨

**1. settings.json 部署策略**

| 方案 | 優點 | 成本／風險 | 適用情境 |
| :--- | :--- | :--- | :--- |
| A. 不管理 | 零風險 | 權限、hooks、`language` 等無法版本控制 | 目前無共用設定需求 |
| B. 整檔覆寫 + `.bak` | 實作最簡，與 Cursor `settings.json` 一致 | 每次 deploy 抹除 `/config`、`/model`、`pluginConfigs`、`autoMemoryEnabled` 等回寫值 | 不使用 `/config` 的使用者 |
| C. 鍵層級合併（repo 鍵覆蓋，其餘保留） | 保留執行期回寫值 | 需新增 JSON merge 邏輯與測試；陣列語意（取代或聯集）需定義 | 需要版本控制部分設定 |

建議：短期 A；若要管理 `permissions.deny`、`hooks` 等，採 C，並在 `tests/test_build.py` 先寫合併行為測試。

**2. 共用規範的組裝方式**

| 方案 | 優點 | 成本／風險 |
| :--- | :--- | :--- |
| 維持 build 期 `<!-- INCLUDE -->` 展開成單一 `~/.claude/CLAUDE.md` | 與 Antigravity／Codex／Cursor 流程一致；部署結果自足 | 無 |
| 改用 `@~/...` runtime import | 可少一份副本 | 依賴另一部署路徑存在；僅 Claude 支援，破壞跨平台對稱 |
| 拆為 `~/.claude/rules/identity.md`、`coding-style.md` | 可用 `paths` 條件載入 | 需新增 compile 邏輯；對無條件規則無 context 節省 |

建議維持現行 build 期展開。註：若 INCLUDE 未展開，HTML 註解會被 Claude Code 剝除，因此漏展開時不會出錯而是**靜默缺少內容**，現行 `FileNotFoundError` 檢查可避免此情況。

**3. 專案層 AGENTS.md**

本 repo 根目錄只有 `AGENTS.md`、沒有 `CLAUDE.md`，在 v2.1.277 以上的預設設定下 Claude Code 會直接讀取 `AGENTS.md`，且 `~/.claude/CLAUDE.md` 不影響此判斷。無需新增專案 `CLAUDE.md`；若需支援較舊版本或停用 `agents-md` plugin 的環境，再加入僅含 `@AGENTS.md` 的 `CLAUDE.md`。[官方 Memory 文件](https://code.claude.com/docs/en/memory)

### 與現有 build.py 的差距清單

1. ~~`compile_claude()` 部署 `mcp_config.json` 至 `~/.claude/`~~：已移除此段與 `configs/claude/mcp_config.json`（2026-09-26）。
2. ~~`compile_skills()` 未排除保留名稱~~：已新增 `validate_skill_name()`，名稱為 `synced`（不分大小寫）或以 `anthropic-skills` 開頭時編譯失敗（2026-09-26）。
3. `deploy()` 對每個 skill 檔案產生 `.bak`，本機觀察 `~/.claude/skills/` 下已累積 676 個 `.bak` 檔；雖 Claude Code 只讀 `SKILL.md`，但這些檔案會混入 skill 目錄，可能被當作 supporting files 瀏覽。建議 skill 目錄改以整目錄備份或不備份。
4. 部署僅新增／覆蓋，不刪除 repo 中已移除的 skill；`~/.claude/skills/` 可能殘留舊 skill。
5. 尚無 `settings.json`、`rules/`、`agents/` 的編譯路徑；若日後需要，依上方取捨新增並補測試。

### 與 repo 既有文件的衝突

- （已於 2026-09-26 修正）[agent-skill-paths-research.md](agent-skill-paths-research.md) 原將 Claude Code 全域 MCP 設定寫為 `~/.claude/mcp_config.json` 或 `~/.claude/config.json`，與官方文件不符；官方使用者層 MCP 位置為 `~/.claude.json`。
- 同文件寫專案 Rules 僅 `CLAUDE.md`（專案根）；官方另有 `./.claude/CLAUDE.md`、`CLAUDE.local.md`、`.claude/rules/` 與條件式 `AGENTS.md`。

## 未確認事項

- Claude Code 是否能透過 symlink 或其他設定探索 `~/.agents/skills/`：官方文件僅允許個別 `<name>` 目錄為 symlink，未列出 `~/.agents/skills/` 為探索位置；是否可將整個 `~/.claude/skills` 設為 symlink 未確認。
- `~/.claude/rules/` 下的 `paths` 條件規則，其 glob 是相對哪個根目錄比對（使用者層規則無固定專案根）：官方文件未說明，未確認。
- `claude mcp add --scope user` 對已存在同名 server 的覆寫或報錯行為：本次未查得官方說明，未確認。
- 本機未安裝 `claude` 指令於 PATH，無法以 `claude --version` 確認版本是否 ≥ v2.1.277（AGENTS.md 直接讀取之門檻）。

## 官方來源

- [How Claude remembers your project（Memory）](https://code.claude.com/docs/en/memory)（2026-09-26 存取）
- [Settings files and precedence](https://code.claude.com/docs/en/settings)（2026-09-26 存取）
- [Settings reference](https://code.claude.com/docs/en/settings-reference)（2026-09-26 存取）
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)（2026-09-26 存取）
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)（2026-09-26 存取）
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents)（2026-09-26 存取）
- [Plugins overview](https://code.claude.com/docs/en/plugins)（2026-09-26 存取）
- [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory)（2026-09-26 存取）
- [CLI reference](https://code.claude.com/docs/en/cli-reference)（2026-09-26 存取）
- [Claude Code settings JSON Schema](https://json.schemastore.org/claude-code-settings.json)（2026-09-26 存取）
