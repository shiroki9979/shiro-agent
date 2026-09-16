# Shiro Agent

跨開發環境之多 Agent 設定檔、共用行為規範與標準化 Agent Skills 的集中管理系統。

## 語言（Language）

**Skill**:
包含 `SKILL.md` 檔案與選用之輔助腳本或參考資源的模組化目錄，用於擴充 Agent 的特定領域能力。
_Avoid_: 插件（Plugin）、工具（Tool）、擴充（Extension）、動作（Action）

**Custom Skill**:
由本專案自主撰寫與維護、存放於 `custom-skills/` 並支援動態引入共用規範的自有技能。
_Avoid_: 內部插件（Internal plugin）、本機技能（Local skill）、私有工具（Private tool）

**Third-party Skill**:
透過 Agent Skills CLI 安裝並記錄於 `skills-lock.json`、存放於 `.agents/skills/` 的外部社群技能。
_Avoid_: 外部依賴（External dependency）、第三方套件（Third-party package）

**Agent Config**:
自共用規範編譯而成、針對特定目標 AI Agent 所建立的專屬規則與環境設定檔。
_Avoid_: 設定（Setting）、偏好（Preference）、Dotfile

**Shared Rule**:
定義跨 Agent 共用之角色人設、程式風格或工作流程約束的單一真實來源 Markdown 文件。
_Avoid_: 基礎設定（Base config）、系統提示詞（System prompt）、全域指引（Global guideline）

**Target Agent**:
接收編譯後設定檔與 Skills 部署的目標 AI 開發平台（例如 Antigravity、Codex、Cursor 或 Claude）。
_Avoid_: 客戶端（Client）、工具（Tool）、環境（Environment）

**Codex Instruction**:
Codex 的持久行為規範文件，以 `AGENTS.md` 表示並部署至 Codex home。
_Avoid_: Command Rule、Sandbox Policy

**Skill Lock**:
記錄已安裝 Skills 之確切來源、路徑與校驗雜湊值的依賴鎖定檔。
_Avoid_: 清單（Manifest）、依賴樹（Dependency tree）、版本鎖（Version lock）
