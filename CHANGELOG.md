# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- 新增第三方 Agent Skills 功能與架構參考手冊（`docs/third-party-skills.md`）。
- 新增 `sync-docs`、`prepare-commit`、`changelog`、`adr-writing`、`diataxis`、`extract-till-you-drop` 等自建 Agent 技能與規範。
- 新增 Agent 儲存庫工作流規範文件（`docs/agents/issue-tracker.md`、`docs/agents/triage-labels.md`、`docs/agents/domain.md`）。
- 引入 `frontend-design`（源自 `anthropics/skills`）第三方 Agent 技能。

### Changed

- 將根目錄 `AGENT.md` 重命名為標準 `AGENTS.md` 並補全 `## Agent skills` 指標設定。
- 同步更新 `README.md` 目錄結構與 `docs/third-party-skills.md` 技能清單（共 38 個）。

### Fixed

- 校正專案技術文件（`AGENTS.md`、`README.md`）與架構決策紀錄（`docs/adr/`）內部之相對路徑連結。
- 修復 Markdownlint 格式、內嵌 HTML 與標題間距問題（`MD022`、`MD032`、`MD033`）。

[Unreleased]: https://github.com/ShirokiXue/shiro-agent/commits/main
