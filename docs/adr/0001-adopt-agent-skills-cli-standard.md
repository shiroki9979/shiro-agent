# ADR-0001：採用 Agent Skills CLI 標準規範進行技能管理

> - Created: 2026-08-23
> - Last Updated: 2026-11-27
> - Author: Bo-Xue Huang
> - Status: Accepted
> - Related: [ADR-0002](0002-separate-custom-and-third-party-skills.md)

---

## Plain Language Summary

這個專案要管理外部作者寫的技能，也就是用來擴充 AI 開發助理能力的說明檔。早期用自製的腳本下載，但看不出上游有沒有更新，也無法確認下載的內容沒被改過。因此決定改用社群通用的技能管理工具來安裝與更新，並用一份鎖定檔記下每個技能的來源與內容指紋，自製的下載腳本全部移除。代價是開發環境必須裝有 Node.js，目錄結構也要照這個工具的規定。

## 1. Context

專案早期使用自研技能下載腳本（包含 `fetch_skills.py`、`manifest.json` 與自訂目錄結構），難以追蹤第三方技能上游更新、缺乏完整性雜湊驗證，且無法與社群快速發展的 Agent Skills 生態標準對齊。需要一套標準化、具備依賴鎖定與雜湊校驗的技能管理機制。

## 2. Decision

全面遷移至社群標準 Agent Skills CLI（`npx skills`），使用 `.agents/skills/` 作為第三方技能存放目錄，並以根目錄 `skills-lock.json` 作為版本與 SHA-256 雜湊鎖定檔；移除自研 `fetch_skills.py` 與 `manifest.json`。

### Rationale & Alternatives Considered

- **選定方案（Agent Skills CLI）**：具備內建依賴解析、版本鎖定與 SHA-256 完整性校驗；完全相容社群生態與 Agent 原生探索機制；免除自行維護下載解析器的額外成本。
- **候選方案 A（保留自研 `fetch_skills.py` + `manifest.json`）**：雖可任意客製目錄結構，但需自行實作依賴樹解析、雜湊檢查與版本控制，維護成本高且與開源生態割裂。
- **候選方案 B（Git Submodule）**：可鎖定 commit，但 submodule 操作繁瑣、缺乏 skill 等級的顆粒度管理與社群 CLI 的便捷安裝命令。

## 3. Consequences

- **正面效益（Positive）**：獲得標準化 `skills-lock.json` 鎖定機制；可直接使用 `npx skills add/update/list` 安裝開源技能；大幅降低維護成本。
- **代價與風險（Trade-offs & Risks）**：開發環境需要具備 Node.js / `npx` 執行環境；需適配 `.agents/skills/` 的固定結構。
- **不做／延後範圍（Out of Scope / Deferred）**：不自行建立或託管私有 Skills Registry。

## 4. Compliance

- 專案根目錄必須維持 `skills-lock.json` 與 `.agents/skills/` 一致性。
- 透過 [Makefile](../../Makefile) 提供快捷指令（`make skills-list`、`make skills-add`、`make skills-update`）統一操作介面。
- CI / Code Review 檢驗第三方技能是否皆由 `skills-lock.json` 記錄且無手動修改。

## 5. Notes

- **實作與遷移紀錄**：於 commit `6501cae` 清理舊有 `scripts/fetch_skills.py`，建立標準 `skills-lock.json`。
