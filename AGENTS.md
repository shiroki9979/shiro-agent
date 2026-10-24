# Agent 指南：shiro-agent

> 建立日期：2026-08-24
> 最後更新：2026-10-25

本專案為跨平台 AI 開發環境（Antigravity, Cursor, Claude 等）之設定檔、共用行為規範與 Agent Skills 集中管理庫。

---

## 核心架構與單一真實來源 (Single Source of Truth)

- **共用規範**：[shared/](shared) 為規範唯一修改點，包含 [identity.md](shared/identity.md) 與 [coding-style.md](shared/coding-style.md)。主標題採用 `##`（H2）以適配入口模板 `# Rules` 的單一 H1 結構。嚴禁直接在 `configs/` 或 `dist/` 硬編碼修改共用規則。
- **自建技能**：[custom-skills/](custom-skills)，每個技能必須包含 `SKILL.md`。支援以 `<!-- INCLUDE:shared/... -->` 標籤動態注入共用規範。
- **第三方技能**：[.agents/skills/](.agents/skills) 與 [skills-lock.json](skills-lock.json)，遵循社群標準 CLI（`npx skills`）管理；完整技能功能與架構請參閱 [docs/third-party-skills.md](docs/third-party-skills.md)。
- **第三方技能補充**：需調整第三方技能時，於 [skill-addenda/](skill-addenda) 新增 `<技能名稱>.md`，編譯時附加至輸出的 `SKILL.md`，不修改 `.agents/skills/` 原檔；依據見 [ADR-0004](docs/adr/0004-append-local-addenda-to-third-party-skills.md)。
- **目標設定**：[configs/](configs) 存放針對各 Agent 的入口設定與特定設定檔（`antigravity/`、`codex/`、`cursor/`、`claude/`）。
- **架構決策與術語**：術語遵循 [CONTEXT.md](CONTEXT.md)，重大架構決策依循 [adr-writing](custom-skills/adr-writing/SKILL.md) 規範記錄於 [docs/adr/](docs/adr)。

---

## 開發工作流程與常用指令

專案使用 `uv` 與 `make` 作為指令入口：

| 動作 | 指令 | 說明 |
| :--- | :--- | :--- |
| **執行測試** | `make test` | 執行單元測試套件（`uv run python -m unittest discover -s tests -p "test_*.py" -v`） |
| **編譯設定** | `make build` | 展開模板並聚合技能至 `dist/` |
| **預覽部署** | `make dry-run` | 模擬編譯與部署流程 |
| **部署發布** | `make deploy` | 編譯並同步至全域系統路徑（`~/.agents`, `~/.gemini/config`, `~/.cursor`, `~/.claude`, `~/.codex`），自動產生 `.bak` |
| **技能管理** | `make skills-list`, `make skills-add PKG=<source>`, `make skills-update` | 管理與更新第三方 Agent Skills |
| **版本發布** | `make release TAG=vX.Y.Z` | 執行測試後建立註解 Git Tag；需另行 `git push origin <tag>` |

---

## Agent 開發與協作規範

1. **技能撰寫原則**：
   - 新增自建技能、調整觸發範圍或驗證技能行為時，參閱 [技能撰寫與驗證指南](docs/skill-authoring-guide.md)。
   - 技能描述（`description`）為觸發路徑之 Context Pointer，語句首字前置關鍵動詞或領域名詞，精確定義適用情境。
   - 遵守漸進式揭露（Progressive Disclosure）：高頻或共通指引留在本體，邊界與深入參考拆分至獨立文件。
   - 自建技能（`custom-skills/`）與第三方技能（`.agents/skills/`）目錄名稱不得衝突。
2. **架構決策紀錄 (ADR)**：
   - 提議或新增 ADR 須依循 [adr-writing](custom-skills/adr-writing/SKILL.md) 滿足「難以逆轉、無脈絡下令人意外、源自真實取捨」三大門檻，並落實 5 態生命週期與雙向關聯。
3. **測試與品質把關**：
   - 修改 [scripts/build.py](scripts/build.py) 或核心編譯邏輯時，須遵循 TDD 流程並同步於 [tests/test_build.py](tests/test_build.py) 新增/維護測試案例。
   - 提交任何變更前，一律執行 `make test` 確保測試通過。
4. **溝通與行為原則**（詳見 [shared/identity.md](shared/identity.md)）：
   - 預設使用正體中文回覆。
   - 保持客觀、簡潔、直接切入重點；不使用表情符號。
   - 遇架構決策或技術選型時，主動列出各方案的取捨（優點、成本、風險、適用情境）。

---

## Agent skills

### Issue tracker

Issues and specs for this repo live as GitHub issues (`shiroki9979/shiro-agent`). See `docs/agents/issue-tracker.md`.

### Triage labels

The default 5 canonical triage roles mapped 1:1 (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`CONTEXT.md` + `docs/adr/` at repo root). See `docs/agents/domain.md`.
