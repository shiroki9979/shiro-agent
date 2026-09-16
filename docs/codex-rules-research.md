# Codex 指示、組態、命令規則與 Skills 機制研究

建立日期：2026-09-16  
最後更新：2026-09-16  
查證範圍：僅採用 OpenAI 官方 Codex／ChatGPT Learn 文件；所有連結於 2026-09-16 存取。

## 結論摘要

Codex 有四種用途不同的機制，應分開管理：

| 需求 | 應使用的機制 | 使用者層位置 |
| :--- | :--- | :--- |
| 跨專案的工作偏好與行為指示 | `AGENTS.md` | `$CODEX_HOME/AGENTS.md`（預設 `~/.codex/AGENTS.md`） |
| 暫時取代使用者層指示 | `AGENTS.override.md` | `$CODEX_HOME/AGENTS.override.md` |
| 模型、沙箱、批准、探索路徑等設定 | `config.toml` | `$CODEX_HOME/config.toml`（預設 `~/.codex/config.toml`） |
| 控制沙箱外 shell 命令的允許、詢問或封鎖 | `*.rules` | `$CODEX_HOME/rules/*.rules`（預設 `~/.codex/rules/*.rules`） |
| 可重用工作流程 | Skills | `$HOME/.agents/skills/<skill-name>/SKILL.md` |

`AGENTS.md` 是文字指示，適合回覆語言、測試與 Git 工作習慣；`.rules` 僅控制「在沙箱外執行的命令」，不是一般行為指示的替代品，且目前仍屬實驗性功能。[官方 AGENTS.md 文件](https://learn.chatgpt.com/docs/agent-configuration/agents-md)（2026-09-16 存取）；[官方 Rules 文件](https://learn.chatgpt.com/docs/agent-configuration/rules)（2026-09-16 存取）

## AGENTS.md：指示探索與優先權

### 使用者層

Codex home 預設為 `~/.codex`，也可以用 `CODEX_HOME` 改變。在此目錄中，Codex 優先讀取 `AGENTS.override.md`；該檔不存在時才讀 `AGENTS.md`；同一層只會採用第一個非空檔案。因此，`AGENTS.override.md` 是暫時切換全域工作模式的覆寫檔，移除後才會恢復使用 `AGENTS.md`。[官方 AGENTS.md 文件](https://learn.chatgpt.com/docs/agent-configuration/agents-md)（2026-09-16 存取）

```text
$CODEX_HOME/AGENTS.override.md  # 存在且非空時使用
或
$CODEX_HOME/AGENTS.md           # 否則使用；預設為 ~/.codex/AGENTS.md
```

### 專案與巢狀目錄

Codex 從專案根目錄（通常是 Git root）一路走到當前工作目錄；若找不到專案根，僅檢查當前目錄。每一層最多載入一個檔案，搜尋順序如下：

```text
AGENTS.override.md → AGENTS.md → project_doc_fallback_filenames 所列檔名
```

每層選中的檔案依「專案根 → 當前目錄」順序串接，後面（更接近當前目錄）的指示會在合併提示中較晚出現，故可精化或覆寫前面的指示。同一目錄中有 `AGENTS.override.md` 時，該目錄的 `AGENTS.md` 不會載入；但不會移除其他目錄已載入的指示。空檔會略過；合併內容預設上限為 32 KiB，達到 `project_doc_max_bytes` 後停止加入。[官方 AGENTS.md 文件](https://learn.chatgpt.com/docs/agent-configuration/agents-md)（2026-09-16 存取）

```text
$CODEX_HOME/AGENTS.md
repo/AGENTS.md
repo/services/AGENTS.md
repo/services/payments/AGENTS.override.md  # 在此目錄取代 payments/AGENTS.md
```

上述例子在 `repo/services/payments` 執行時，載入順序是使用者層、repo、services、payments override。這是累加後由較近目錄優先的模型，而非只讀取單一「最高優先權」檔案。[官方 AGENTS.md 文件](https://learn.chatgpt.com/docs/agent-configuration/agents-md)（2026-09-16 存取）

### 替代檔名與驗證

可在 `config.toml` 設定 `project_doc_fallback_filenames`，讓既有的 `TEAM_GUIDE.md` 等檔案在每個目錄中於兩種預設 AGENTS 檔之後被探索。`project_doc_max_bytes` 可提高整體指示讀取上限。修改設定或指示後，應重新啟動 Codex 或執行新的命令；官方也建議以指令摘要目前指示，或在啟用日誌後檢查 session/TUI log 驗證實際載入結果。[官方 AGENTS.md 文件](https://learn.chatgpt.com/docs/agent-configuration/agents-md)（2026-09-16 存取）

```toml
# ~/.codex/config.toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 65536
```

```bash
codex --ask-for-approval never "Summarize the current instructions."
codex --cd services/payments --ask-for-approval never "Show which instruction files are active."
```

## config.toml：組態層級與相關選項

使用者設定預設位於 `~/.codex/config.toml`；專案可在任一路徑的 `.codex/config.toml` 加上覆寫。CLI 與 IDE extension 共用這些層。對同一鍵值，優先權由高至低是：CLI flags／`--config`、從專案根到當前目錄的可信任專案設定（最近者勝出）、以 `--profile` 選取的 `$CODEX_HOME/<profile>.config.toml`、使用者設定、雲端受管預設、Unix 的 `/etc/codex/config.toml`、內建預設值。[官方 Config basics](https://learn.chatgpt.com/docs/config-file/config-basic)（2026-09-16 存取）

未被標示為 trusted 的專案，Codex 會略過專案 `.codex/` 層，包含專案 `config.toml`、hooks 和 `.rules`；使用者及系統層仍會載入。因此，需要隨 repository 版本控制的組態或命令規則，必須在可信任專案中才有效。[官方 Advanced Configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)（2026-09-16 存取）

本議題直接相關的組態鍵如下：

| 設定鍵 | 用途 |
| :--- | :--- |
| `project_doc_fallback_filenames` | 在預設 `AGENTS.md` 缺席時，額外嘗試的指示檔名。 |
| `project_doc_max_bytes` | 組合專案指示時，最多讀取的位元組數。 |
| `project_root_markers` | 尋找專案根時採用的根目錄標記檔名。 |
| `projects.<path>.trust_level` | 指定專案／worktree 是 `trusted` 或 `untrusted`。 |
| `skills.config` | 依 `SKILL.md` 路徑啟用或停用個別 skill。 |
| `skills.max_context_tokens` | 可用 skills 清單的 context token 預算；顯式值上限為 10,000。 |

上述鍵的型別與行為可見[官方 Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)（2026-09-16 存取）。

`CODEX_HOME` 是 Codex 本機狀態根目錄，預設為 `~/.codex`，其中包含 `config.toml`、可能的 `auth.json`、`history.jsonl`、logs 與 caches。可為隔離設定檔或自動化帳號指定不同值，例如：

```bash
CODEX_HOME="$(pwd)/.codex" codex exec "List active instruction sources"
```

[官方 Advanced Configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)（2026-09-16 存取）

## .rules：沙箱外命令的政策

Rules 用於控制 Codex 要求「在 sandbox 外」執行的命令，並非用來約束所有模型回覆或所有沙箱內操作。每個啟用中的 config layer 旁的 `rules/` 都會在啟動時掃描；使用者層為 `~/.codex/rules/`，專案層為 `<repo>/.codex/rules/`，而後者僅在專案 `.codex/` 層受信任時載入。新增或變更 `.rules` 後要重新啟動 Codex。[官方 Rules 文件](https://learn.chatgpt.com/docs/agent-configuration/rules)（2026-09-16 存取）

`.rules` 使用無副作用的 Starlark 語法。其核心 `prefix_rule()` 接受命令 token 前綴，決策可為 `allow`、`prompt`、`forbidden`；同時符合多條規則時採最嚴格結果：`forbidden > prompt > allow`。`match` 和 `not_match` 可作為載入時檢驗的例子。[官方 Rules 文件](https://learn.chatgpt.com/docs/agent-configuration/rules)（2026-09-16 存取）

```python
# ~/.codex/rules/default.rules
prefix_rule(
    pattern = ["git", "reset", "--hard"],
    decision = "forbidden",
    justification = "Use a non-destructive Git workflow instead.",
    match = ["git reset --hard HEAD"],
)
```

可以在依賴前以 `codex execpolicy check` 驗證特定規則檔與命令的結果：

```bash
codex execpolicy check --pretty \
  --rules ~/.codex/rules/default.rules \
  -- git reset --hard HEAD
```

此指令會輸出最嚴格決策與符合的規則。複雜 shell script（例如含重導向、變數展開或 command substitution）不會被拆分，整段會作為單一 `bash -lc` 呼叫套用規則，因此規則應以實際命令形式測試。[官方 Rules 文件](https://learn.chatgpt.com/docs/agent-configuration/rules)（2026-09-16 存取）

## Skills：位置、啟用與指示的關係

一個 skill 是含有具名 `SKILL.md` 的目錄，並可包含 `scripts/`、`references/` 與 `assets/`。Codex 一開始僅取得 skill 的名稱、description 與路徑，決定使用後才讀完整 `SKILL.md`。使用者可透過 `$skill-name` 或 `/skills` 明確叫用，也可由 Codex 依 skill description 隱式匹配。[官方 Build skills](https://learn.chatgpt.com/docs/build-skills)（2026-09-16 存取）

官方列出的本機探索位置如下：

| Scope | 位置 | 說明 |
| :--- | :--- | :--- |
| Repository | `$CWD/.agents/skills` 至 `$REPO_ROOT/.agents/skills` | Codex 從目前目錄往 repository root 掃描。 |
| User | `$HOME/.agents/skills` | 使用者個人、跨 repository 的 skills。 |
| Admin | `/etc/codex/skills` | 同一機器／容器各使用者共用的管理者 skills。 |
| System | Codex 內建 | OpenAI 隨 Codex 提供的通用 skills。 |

同名 skills 不會合併，可能同時出現在選擇器。官方的使用者技能位置是 `$HOME/.agents/skills`；`CODEX_HOME` 的官方職責是本機狀態與設定根目錄，不能把 `$CODEX_HOME/skills` 視為文件保證的使用者 skill 探索位置。[官方 Build skills](https://learn.chatgpt.com/docs/build-skills)（2026-09-16 存取）；[官方 Advanced Configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)（2026-09-16 存取）

若要停用而不刪除某個 skill，可在使用者 `config.toml` 設定：

```toml
[[skills.config]]
path = "/absolute/path/to/skill/SKILL.md"
enabled = false
```

[官方 Build skills](https://learn.chatgpt.com/docs/build-skills)（2026-09-16 存取）

## 對本專案的建議配置策略

1. 將個人且跨專案的偏好放在 `~/.codex/AGENTS.md`，例如預設語言、回覆密度、通用測試與安全 Git 習慣；不要將本專案的 domain 術語或部署命令放在此處。
2. 專案共享規範維持於 repository root 的 `AGENTS.md`；模組專屬規範才放進該模組目錄。這符合 Codex 由根至當前目錄的累加模型，也讓本專案既有 `AGENTS.md` 成為可版本控制的單一入口。
3. 僅在短期、明確且需完全取代同層指示的情境建立 `AGENTS.override.md`，並在檔案寫明用途與移除條件；否則它容易遮蔽正常的 `AGENTS.md`。
4. 將「禁止或必須確認沙箱外危險命令」放進 `~/.codex/rules/*.rules`，例如封鎖 `git reset --hard`；將程式碼風格、流程與文件要求保留在 `AGENTS.md`。
5. 共用技能放在本專案 `.agents/skills/`，個人跨專案技能放在 `~/.agents/skills/`。對要被使用者層停用的技能，再以 `~/.codex/config.toml` 的 `[[skills.config]]` 管理。

## 官方來源

- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)（2026-09-16 存取）
- [Config basics](https://learn.chatgpt.com/docs/config-file/config-basic)（2026-09-16 存取）
- [Advanced Configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)（2026-09-16 存取）
- [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)（2026-09-16 存取）
- [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules)（2026-09-16 存取）
- [Build skills](https://learn.chatgpt.com/docs/build-skills)（2026-09-16 存取）
