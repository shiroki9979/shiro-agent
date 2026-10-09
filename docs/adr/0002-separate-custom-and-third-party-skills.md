# ADR-0002：分離自建技能與第三方依賴目錄並於編譯時聚合

> - Created: 2026-08-23
> - Last Updated: 2026-08-24
> - Author: Bo-Xue Huang
> - Status: 核准
> - Related: [ADR-0001](0001-adopt-agent-skills-cli-standard.md), [ADR-0003](0003-multi-target-global-skills-dispatch.md)

---

## 1. Context

在採用 Agent Skills CLI 後，外部技能由 CLI 管理於 `.agents/skills/` 中。若將團隊自行撰寫的技能也直接放入 `.agents/skills/`，在執行 `npx skills update` 或清理依賴時容易發生意外覆寫或誤刪；且自建技能需要支援 `<!-- INCLUDE:shared/... -->` 模板動態展開，而第三方技能為靜態檔案。

## 2. Decision

在原始碼層級實體隔離：自建技能存放於 `custom-skills/`，第三方技能維持於 `.agents/skills/`。由 `scripts/build.py` 在編譯階段聚合兩者至輸出目錄 `dist/`，並在偵測到同名衝突時強制中斷報錯。

### Rationale & Alternatives Considered

- **選定方案（目錄分離 + 編譯聚合 + 衝突檢查）**：原始碼層級實體隔離保護自有資產；自建技能可獨享模板展開（`<!-- INCLUDE:... -->`）；聚合時進行重名檢查保證確定性。
- **候選方案 A（全放在 `.agents/skills/`）**：維護單一目錄看似簡潔，但無法防止 `npx skills` 指令覆寫自有技能，且難以清晰區分何者為外部依賴、何者為自建資產。
- **候選方案 B（自建技能以獨立 npm/git package 發布再用 CLI 安裝）**：過度複雜化內部迭代流程，每次小改動皆須發布版本。

## 3. Consequences

- **正面效益（Positive）**：自建技能與外部依賴邊界清晰；防止 CLI 工具誤覆寫；支援模板動態展開；編譯器自動防範同名衝突。
- **代價與風險（Trade-offs & Risks）**：專案需要多一道 `make build` 編譯步驟將技能聚合至 `dist/`。
- **不做／延後範圍（Out of Scope / Deferred）**：暫不支援自建技能的跨 repo 自動發布流程。

## 4. Compliance

- [tests/test_build.py](../../tests/test_build.py) 包含 `test_compile_skills_aggregates_custom_and_third_party` 與 `test_compile_skills_collision_error` 單元測試，嚴格驗證聚合邏輯與重名防護。
- 執行 `make test` 與 `make build` 確保編譯與測試通過。

## 5. Notes

- **實作與遷移紀錄**：於 commit `332c98b` 實作 `custom-skills/` 與 [scripts/build.py](../../scripts/build.py) 聚合管線。
