# Agent 指南：shiro-agent

本專案為跨平台 AI 開發環境（Antigravity, Cursor, Claude 等）之設定檔、共用行為規範與 Agent Skills 集中管理庫。

---

## 核心架構與單一真實來源 (Single Source of Truth)

- **共用規範**：[shared/](file:///home/myuser/repos/shiro-agent/shared) 為規範唯一修改點，包含 [identity.md](file:///home/myuser/repos/shiro-agent/shared/identity.md)、[coding-style.md](file:///home/myuser/repos/shiro-agent/shared/coding-style.md) 與 [workflows/](file:///home/myuser/repos/shiro-agent/shared/workflows)。嚴禁直接在 `configs/` 或 `dist/` 硬編碼修改共用規則。
- **自建技能**：[custom-skills/](file:///home/myuser/repos/shiro-agent/custom-skills)，每個技能必須包含 `SKILL.md`。支援以 `<!-- INCLUDE:shared/... -->` 標籤動態注入共用規範。
- **第三方技能**：[.agents/skills/](file:///home/myuser/repos/shiro-agent/.agents/skills) 與 [skills-lock.json](file:///home/myuser/repos/shiro-agent/skills-lock.json)，遵循社群標準 CLI（`npx skills`）管理。
- **目標設定**：[configs/](file:///home/myuser/repos/shiro-agent/configs) 存放針對各 Agent 的入口設定與特定設定檔（`antigravity/`、`cursor/`、`claude/`）。
- **架構決策與術語**：術語遵循 [CONTEXT.md](file:///home/myuser/repos/shiro-agent/CONTEXT.md)，重大架構決策記錄於 [docs/adr/](file:///home/myuser/repos/shiro-agent/docs/adr)。

---

## 開發工作流程與常用指令

專案使用 `uv` 與 `make` 作為指令入口：

| 動作 | 指令 | 說明 |
| :--- | :--- | :--- |
| **執行測試** | `make test` | 執行單元測試套件（`uv run python -m unittest discover -s tests -p "test_*.py" -v`） |
| **編譯設定** | `make build` | 展開模板並聚合技能至 `dist/` |
| **預覽部署** | `make dry-run` | 模擬編譯與部署流程 |
| **部署發布** | `make deploy` | 編譯並同步至全域系統路徑（`~/.agents`, `~/.gemini/config`, `~/.cursor`, `~/.claude`），自動產生 `.bak` |
| **技能管理** | `make skills-list`<br>`make skills-add PKG=<source>`<br>`make skills-update` | 管理與更新第三方 Agent Skills |

---

## Agent 開發與協作規範

1. **技能撰寫原則**：
   - 技能描述（`description`）為觸發路徑之 Context Pointer，語句首字前置關鍵動詞或領域名詞，精確定義適用情境。
   - 遵守漸進式揭露（Progressive Disclosure）：高頻或共通指引留在本體，邊界與深入參考拆分至獨立文件。
   - 自建技能（`custom-skills/`）與第三方技能（`.agents/skills/`）目錄名稱不得衝突。
2. **測試與品質把關**：
   - 修改 [scripts/build.py](file:///home/myuser/repos/shiro-agent/scripts/build.py) 或核心編譯邏輯時，須遵循 TDD 流程並同步於 [tests/test_build.py](file:///home/myuser/repos/shiro-agent/tests/test_build.py) 新增/維護測試案例。
   - 提交任何變更前，一律執行 `make test` 確保測試通過。
3. **溝通與行為原則**（詳見 [shared/identity.md](file:///home/myuser/repos/shiro-agent/shared/identity.md)）：
   - 預設使用正體中文回覆。
   - 保持客觀、簡潔、直接切入重點；不使用表情符號。
   - 遇架構決策或技術選型時，主動列出各方案的取捨（優點、成本、風險、適用情境）。
