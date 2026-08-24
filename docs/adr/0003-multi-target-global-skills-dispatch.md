# ADR-0003：多目標全域 Skills 派發架構

> - Created: 2026-08-23
> - Last Updated: 2026-08-24
> - Author: White Huang
> - Status: 核准
> - Related: [ADR-0001](0001-adopt-agent-skills-cli-standard.md), [ADR-0002](0002-separate-custom-and-third-party-skills.md)

---

## 1. Context

不同 AI 開發平台（Antigravity、Cursor、Claude Code、Agent Skills CLI）各自擁有獨立的全域技能探索目錄（如 `~/.gemini/config/skills/`、`~/.claude/skills/`、`~/.cursor/skills/`、`~/.agents/skills/`）。若僅部署至單一平台目錄，其他 Agent 無法免設定直接載入技能；若使用符號連結（Symlink），在跨環境、容器或特定 IDE 檔案監聽機制下可能失效或引發相容性問題。

## 2. Decision

在 [scripts/build.py](../../scripts/build.py) 的部署邏輯中，將編譯聚合後的全部技能同時派發（實體複製）至所有支援的目標全域路徑（`~/.agents/skills/`、`~/.gemini/config/skills/`、`~/.claude/skills/`、`~/.cursor/skills/`），並在覆蓋現有檔案前自動產生 `.bak` 備份。

### Rationale & Alternatives Considered

- **選定方案（多目標實體部署 + 自動 .bak 備份）**：確保所有 Agent 零配置（Zero-config）即可原生探索並使用所有技能；無符號連結失效或跨檔案系統問題；備份機制防範誤覆寫。
- **候選方案 A（單一目錄 + 全域 Symlink 指向）**：部分工具或遠端開發環境（如 VS Code Server / DevContainer）對 Symlink 解析支援不一，可能導致探索失敗。
- **候選方案 B（僅部署至 `~/.agents/skills/`）**：Claude Code 與 Cursor 歷史版本或特定工作區無法直接自動向上探索 `~/.agents/skills/`，需使用者額外手動配置。

## 3. Consequences

- **正面效益（Positive）**：達成真正的一處編譯、全平台即時同步（Write once, available everywhere）；Agent 探索效能高且無相容性隱患。
- **代價與風險（Trade-offs & Risks）**：磁碟佔用略微增加（多份副本，但文字 Skills 體積極小）；部署步驟較多。
- **不做／延後範圍（Out of Scope / Deferred）**：暫不實作各目標平台技能的個別啟用/停用過濾開關（預設全量同步）。

## 4. Compliance

- [tests/test_build.py](../../tests/test_build.py) 包含 `test_compile_and_deploy_dry_run` 與 `test_compile_and_deploy_with_backup`，確保多目標派發與備份邏輯正確。
- 執行 `make deploy`（或 `make dry-run`）可檢驗部署操作皆正確指向各平台全域目錄。

## 5. Notes

- **調研依據**：詳見 [docs/agent-skill-paths-research.md](../agent-skill-paths-research.md) 各平台探索路徑研究。
- **實作與遷移紀錄**：於 commit `6178ed5` 納入多目標全域派發。
