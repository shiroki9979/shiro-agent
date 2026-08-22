# 採用 Agent Skills CLI 標準規範進行技能管理

我們決定從自製技能下載工具（包含 `fetch_skills.py`、`manifest.json` 與 `skills/` 子目錄）遷移至社群標準的 Agent Skills CLI（`npx skills`、`.agents/skills/` 與 `skills-lock.json`）。雖然自製腳本能提供局部的目錄分類隔離，但採用標準生態格式具備內建完整性雜湊驗證、自動依賴解析與 Agent 執行時期的原生探索相容性，並消除了維護自訂解析器的額外成本。
