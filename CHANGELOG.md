<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 新增 `after-code-review` 自建技能：將 `/code-review` 雙軸報告分流為下一 commit／開票草稿（`custom-skills/after-code-review/`）。
- 引入 `diagram-design`（源自 `cathrynlavery/diagram-design`）第三方技能，鎖定檔技能數由 53 增至 54（`skills-lock.json`、`.agents/skills/diagram-design/`）。
- 新增 `eli5` 自建技能，暫存 Anthropic `claude-plugins-community` 的 HTML 圖解解釋技能副本（正式發布前）。
- 引入 15 個源自 `anthropics/skills` 的第三方技能（文件處理、設計、MCP、內部溝通等），鎖定檔技能數由 38 增至 53（`skills-lock.json`、`.agents/skills/`）。

### Changed

- 同步上游第三方技能：`diagram-design` 新增瀑布圖、Excalidraw 匯入與 CJK 字型支援；`frontend-design` 更新設計原則與反模板化指引，並將技能手冊圖表數由 39 改為 40（`skills-lock.json`、`.agents/skills/`、`docs/third-party-skills.md`）。
- 精簡 `shared/identity.md`（移除 Profile 與程式碼輸出條目）與 `shared/coding-style.md`（移除原則口號與註解語言強制）。
- 精簡 `diataxis` 自建技能工作流程，移除強制輸出宣告區塊之要求（`custom-skills/diataxis/SKILL.md`）。
- 同步更新 `docs/third-party-skills.md` 技能清單與分類（53 → 54；新增 `cathrynlavery/diagram-design` 條目）。
- 於 `README.md` 與 `AGENTS.md` 補上 `make release` 發布指令說明。
- 校正 `docs/agent-skill-paths-research.md` 之 Skills 派發結論，使其與現行多目標全域部署一致。

### Removed

- 移除全域 always-on 的 Grill 工作流程摘要（`shared/workflows/grill-me.md`、`shared/workflows/grill-with-docs.md`）；質詢改由第三方技能 `grill-me` / `grill-with-docs` 觸發。

## [0.1.0] - 2026-08-25

### Added

- 新增第三方 Agent Skills 功能與架構參考手冊（`docs/third-party-skills.md`）。
- 新增 `sync-docs`、`prepare-commit`、`changelog`、`adr-writing`、`diataxis`、`extract-till-you-drop` 等自建 Agent 技能與規範。
- 新增 Agent 儲存庫工作流規範文件（`docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/agents/domain.md`）。
- 引入 `frontend-design`（源自 `anthropics/skills`）第三方 Agent 技能。

### Changed

- 將根目錄 `AGENT.md` 重命名為標準 `AGENTS.md` 並補全 `## Agent skills` 指標設定。
- 同步更新 `README.md` 目錄結構與 `docs/third-party-skills.md` 技能清單（共 38 個）。
- 於 `prepare-commit` 自建技能中新增文件同步閉環（`sync-docs`）檢核規範與前置建議。

### Fixed

- 校正專案技術文件（`AGENTS.md`、`README.md`）與架構決策紀錄（`docs/adr/`）內部之相對路徑連結。
- 修復 Markdownlint 格式、內嵌 HTML 與標題間距問題（`MD022`、`MD032`、`MD033`）。

[Unreleased]: https://github.com/ShirokiXue/shiro-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ShirokiXue/shiro-agent/releases/tag/v0.1.0
