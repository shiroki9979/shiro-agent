---
name: adr-writing
description: ADR（架構決策紀錄）的建立門檻、撰寫與維護。使用於判斷決策是否值得寫 ADR、新增 ADR，或修訂既有 ADR、變更其 Status（Proposed／Accepted／Superseded／Deprecated／Rejected）。
---

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

**正文凍結**：正文是 H1 與 Context、Decision、Consequences、Compliance 四個區塊。`Proposed` 的正文可以直接改。`Accepted` 之後正文保持原貌，修訂寫成 Notes 條目；決策本身改變時開新 ADR。Plain Language Summary 不是正文，見 §5。

## 4. Metadata

H1 之後的第一個區塊，blockquote 清單、英文 key，依下列順序：

| Key | 規則 |
| --- | --- |
| `Created` | 必填，單一 `YYYY-MM-DD` |
| `Last Updated` | 必填，單一 `YYYY-MM-DD`；Plain Language Summary、正文或 Notes 有變動時改成當天 |
| `Author` | 選填；向使用者確認，不臆造 |
| `Status` | 必填，§3 的一個值 |
| `Related` | 選填，只放連結 |
| `Supersedes`、`Superseded by` | 選填，只放連結 |
| `Revisions` | 選填，本身有修訂時放一個指向本檔 Notes 的錨點連結 |

連結以 `、` 分隔。Metadata 只放上述值；變更經過（改了什麼、審查輪次、票號、PR 號）寫在 commit message。

## 5. 寫法

一份 ADR 有兩種讀者。Plain Language Summary 寫給沒參與討論、也沒讀過專案術語表的工程師，讓他讀完一段就知道這份 ADR 在做什麼。正文寫給要依這個決策動手、或要引用它的人，用正式術語寫到精確。

### 5.1 Plain Language Summary

- **位置**：Metadata 之後、`## 1. Context` 之前，標題為 `## Plain Language Summary`，不編號。編號會讓其他文件對本檔的 `§N` 引用錯位。
- **長度與內容**：一段話，五句以內，依序交代問題、決定、代價。
- **用詞**：專案術語換成日常說法，或在同一句裡解釋。通用技術詞（資料庫、快取、回測）直接用。
- **不用反引號**：程式識別字、檔名、路徑、參數名、設定值都留在正文。想寫反引號時，表示這一句寫到了實作層，改成它的作用。
- **部分被取代的 ADR**：另加一句，指出哪一部分已改由哪份 ADR 決定並附連結；這一句不計入五句。
- **不受正文凍結限制**：任何 Status 都可以新增或改寫，但不得改變決策的意思。與正文不一致時以正文為準，並改寫這一段。

範例：

```markdown
## Plain Language Summary

做回測時，我們要假裝回到過去某個時刻，只用當時手上有的資料來預測。但現有的查詢只看「這筆資料講的是哪個時間」，不看「我們是什麼時候拿到它的」，所以會用到當時還沒拿到的資料，回測成績比實際好看。我們決定研究一律讀一份凍結下來的資料庫副本，並用每筆資料的寫入時間判斷當時知不知道它。代價是副本比原本的訓練資料檔大得多，研究也不能再直接連正式資料庫。
```

### 5.2 正文

以下三項適用新寫的 ADR 與 `Proposed` 的 ADR；`Accepted` 的正文依 §3 不回頭改。

- **標題**：H1 的決策摘要要讓沒讀過專案術語表的人也看得懂。專案術語換成日常說法；換了會失準時，保留術語並把它的意思寫進同一句。
- **Decision 的層級**：逐句問「換一種實作方式，這句還成立嗎？」成立的留下。不成立的是實作細節，例如函式名、參數名、資料表與欄位清單、檔案路徑、例外類別、設定值；把它搬到下列位置，原處留一句結論與連結：
  - 專案有規定時，依專案規定。
  - 已實作的行為：描述系統現況的文件（reference 或規格）。
  - 尚未實作的範圍：工作票或規格。
  - `Compliance` 不受此限，它要寫出具體的測試與檢查。
- **術語**：使用專案術語表的正式用語。每個專案術語在正文首次出現時連到術語表，或在同一句附一句解釋。

## 6. 模板

```markdown
# ADR-NNNN：<決策摘要>

> - Created: YYYY-MM-DD
> - Last Updated: YYYY-MM-DD
> - Status: Proposed
> - Related: [ADR-000N](000N-slug.md)

## Plain Language Summary

<一段話，五句以內：遇到什麼問題、決定怎麼做、付出什麼代價。不用專案術語，不用反引號。>

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

## 7. 流程

### A. 新增 ADR

1. 對照 §1 三項門檻，三項都成立才往下。
2. 依專案規範或 §2 決定目錄、編號與 slug。
3. 與使用者確認核心問題、候選方案、選定決策；寫 `Author` 時一併確認作者。
4. 依 §6 模板與 §5.2 撰寫正文：`Rationale` 列出每個候選方案的取捨，`Compliance` 寫出可驗證的手段。
5. 正文寫完後，依 §5.1 寫 Plain Language Summary。
6. 涉及既有 ADR 時，在雙方建立連結（`Related`，或取代關係的 `Supersedes`／`Superseded by` 加 Notes）。

完成條件：§8 檢核表每項都符合。

### B. 修訂或變更 Status

1. 讀目標 ADR 全文與它連結的 ADR。
2. 依 §3 的轉換表做同步動作；`Accepted` 的正文不改，修訂寫成 Notes 條目，必要時加 `Revisions` 或 `Superseded by`。
3. 目標 ADR 沒有 Plain Language Summary 時依 §5.1 補上；這次修訂讓它不再正確時改寫。
4. `Last Updated` 改成當天。

完成條件：§8 檢核表每項都符合，且雙方 ADR 的連結都已更新。

## 8. 檢核表

| 項目 | 合格標準 |
| --- | --- |
| 門檻 | §1 三項同時成立 |
| 區塊完整 | Metadata、Plain Language Summary、Context、Decision、Consequences、Compliance、Notes 都有實質內容 |
| Plain Language Summary | 位於 Metadata 與 Context 之間、不編號；一段話、五句以內；交代問題、決定、代價；沒有反引號，沒有未解釋的專案術語 |
| 正文寫法 | 新寫與 `Proposed` 的 ADR：標題不需讀術語表就看得懂；Decision 每一句換一種實作仍成立，搬走的細節留有連結；專案術語首次出現時有連結或解釋 |
| Metadata | 只有 §4 的 key（或專案規範所列）；日期欄位是單一日期，連結欄位只有連結 |
| Status | §3 的一個值（或專案規範所列） |
| 編號 | 檔名、路徑與 H1 的編號一致 |
| Compliance | 有具體可驗證的機制 |
| 連結 | 取代或繼承關係在雙方都有相對路徑連結 |
| 機密 | 沒有硬編碼的密鑰、憑證或私有 token |
