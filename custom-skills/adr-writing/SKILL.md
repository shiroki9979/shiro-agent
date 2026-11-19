---
name: adr-writing
description: ADR（架構決策紀錄）的建立門檻、撰寫與維護。使用於判斷決策是否值得寫 ADR、新增 ADR，或修訂既有 ADR、變更其 Status（Proposed／Accepted／Superseded／Deprecated／Rejected）。
---

# ADR 撰寫與維護

**專案規範優先**：目標 repo 的規範（`AGENTS.md`、ADR 目錄的 README）另定目錄、編號、metadata key 或 Status 寫法時，一律從專案規範；本技能只補足專案未規定的部分。

## 1. 門檻

三項同時成立才寫 ADR：

1. **難以逆轉**：實施後變更或遷移的成本高，例如更換資料庫、核心框架、通訊協定。
2. **無脈絡下令人意外**：不是業界唯一標準解，沒參與討論的人讀程式碼會疑惑，例如自研簡化版工具而不引入成熟套件。
3. **源自真實取捨**：在多個可行方案之間，依具體約束（效能、時程、複雜度）做出選擇。

任一項不成立，說明寫在一般文件、程式碼註解或 PR 說明。

## 2. 路徑與編號

專案沒有規定時：

- 依序探測既有目錄：`docs/adr/` → `docs/adrs/` → `doc/adr/` → `docs/architecture/decisions/`；找到就沿用該目錄與其檔名風格。
- 沒有既有目錄：`docs/adr/NNNN-kebab-slug.md`。
- 編號為四位數流水號，取目錄中最大編號 + 1。
- Slug 全小寫 kebab-case，用具體動詞與關鍵技術詞，例如 `0001-adopt-agent-skills-cli.md`。
- H1 為 `# ADR-NNNN：<決策摘要>`，編號與檔名一致。

## 3. Status

| 值 | 意義 |
| --- | --- |
| `Proposed` | 方案已提出，討論或檢驗中，尚未定稿 |
| `Accepted` | 決策已定稿並實施 |
| `Superseded` | 整個決策被後續 ADR 推翻或取代 |
| `Deprecated` | 決策涉及的功能、模組或架構已退役，且沒有替代方案 |
| `Rejected` | 評估後不採納，保留紀錄避免重複論證 |

| 轉換 | 同步動作 |
| --- | --- |
| `Proposed` → `Accepted` | 確認決策已定稿 |
| `Proposed` → `Rejected` | Notes 寫一句不採納的原因 |
| `Accepted` → `Superseded` | 新 ADR 寫 `Supersedes`，舊 ADR 寫 `Superseded by`，兩份的 Notes 互相連結 |
| `Accepted` → `Deprecated` | Notes 寫退役原因 |

**部分取代**：新 ADR 只推翻舊 ADR 的一部分時，舊 ADR 的 Status 維持 `Accepted`，加上 `Superseded by` 連結，並在 Notes 寫明被取代的段落。

**正文凍結**：`Proposed` 的正文可以直接改。`Accepted` 之後正文保持原貌，修訂寫成 Notes 條目；決策本身改變時開新 ADR。

## 4. Metadata

H1 之後的第一個區塊，blockquote 清單、英文 key，依下列順序：

| Key | 規則 |
| --- | --- |
| `Created` | 必填，單一 `YYYY-MM-DD` |
| `Last Updated` | 必填，單一 `YYYY-MM-DD`；正文或 Notes 有變動時改成當天 |
| `Author` | 選填；向使用者確認，不臆造 |
| `Status` | 必填，§3 的一個值 |
| `Related` | 選填，只放連結 |
| `Supersedes`、`Superseded by` | 選填，只放連結 |
| `Revisions` | 選填，本身有修訂時放一個指向本檔 Notes 的錨點連結 |

連結以 `、` 分隔。Metadata 只放上述值；變更經過（改了什麼、審查輪次、票號、PR 號）寫在 commit message。

## 5. 模板

```markdown
# ADR-NNNN：<決策摘要>

> - Created: YYYY-MM-DD
> - Last Updated: YYYY-MM-DD
> - Status: Proposed
> - Related: [ADR-000N](000N-slug.md)

## 1. Context

<背景、技術約束或業務需求；一句話點出要解決的核心問題。>

## 2. Decision

<選定的方案與實施範圍。>

### Rationale & Alternatives Considered

- **選定方案**：<優勢與適用原因>
- **候選方案 A**：<未採納原因>
- **候選方案 B**：<未採納原因>

## 3. Consequences

- **Positive**：...
- **Trade-offs & Risks**：...
- **Out of Scope / Deferred**：...

## 4. Compliance

<可驗證的遵守手段：測試、Linter、CI 檢查、特定檔案檢查或 Code Review 清單。沒有自動化手段時寫「無自動化強制機制，依賴 PR Code Review 清單驗證」。>

## 5. Notes

- 取代關係：取代 [ADR-0001](0001-xxx.md)；或被 [ADR-0005](0005-yyy.md) 取代。
- 修訂條目、遷移注意事項、已知限制。
```

Notes 的修訂條目一次修訂一項，依日期往後追加，以日期開頭並寫出受影響的段落；來自另一份 ADR 或規格時附連結：

```markdown
- 2026-10-30：§2.4 的計分限制被 [ADR-0046](0046-recursive-segment-settlement.md) 取代，正文不動。
```

## 6. 流程

### A. 新增 ADR

1. 對照 §1 三項門檻，三項都成立才往下。
2. 依專案規範或 §2 決定目錄、編號與 slug。
3. 與使用者確認核心問題、候選方案、選定決策；寫 `Author` 時一併確認作者。
4. 依 §5 模板撰寫：`Rationale` 列出每個候選方案的取捨，`Compliance` 寫出可驗證的手段。
5. 涉及既有 ADR 時，在雙方建立連結（`Related`，或取代關係的 `Supersedes`／`Superseded by` 加 Notes）。

完成條件：§7 檢核表每項都符合。

### B. 修訂或變更 Status

1. 讀目標 ADR 全文與它連結的 ADR。
2. 依 §3 的轉換表做同步動作；`Accepted` 的正文不改，修訂寫成 Notes 條目，必要時加 `Revisions` 或 `Superseded by`。
3. `Last Updated` 改成當天。

完成條件：§7 檢核表每項都符合，且雙方 ADR 的連結都已更新。

## 7. 檢核表

| 項目 | 合格標準 |
| --- | --- |
| 門檻 | §1 三項同時成立 |
| 區塊完整 | Metadata、Context、Decision、Consequences、Compliance、Notes 都有實質內容 |
| Metadata | 只有 §4 的 key（或專案規範所列）；日期欄位是單一日期，連結欄位只有連結 |
| Status | §3 的一個值（或專案規範所列） |
| 編號 | 檔名、路徑與 H1 的編號一致 |
| Compliance | 有具體可驗證的機制 |
| 連結 | 取代或繼承關係在雙方都有相對路徑連結 |
| 機密 | 沒有硬編碼的密鑰、憑證或私有 token |
