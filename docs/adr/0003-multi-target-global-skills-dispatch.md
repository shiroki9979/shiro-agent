# 多目標全域 Skills 派發架構

我們決定將編譯後的自建與第三方技能同時派發至多個 Agent 的真實全域技能路徑（包含 `~/.gemini/config/skills/`、`~/.claude/skills/`、`~/.cursor/skills/` 與 `~/.agents/skills/`）。各平台對全域技能的探索路徑各自獨立，透過在 `build.py` 編譯時統一進行多目標實體複製，能確保所有 Agent 零配置、原生且穩定地載入全部技能，並避免跨環境軟連結（Symlink）失效的相容性問題。
