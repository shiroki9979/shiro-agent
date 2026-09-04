---
name: after-code-review
description: >
  將 matt pocock /code-review 的雙軸報告分流成「下一 commit」與「開票追蹤」建議，並產出可執行草稿（commit 要點、issue title/body）。
  在剛跑完 code-review、使用者問哪些 finding 該立刻修／哪些該開票、貼上完整 Standards/Spec 報告要求分流，或說 after-code-review / triage review findings 時使用。
  本技能只給建議，不開票、不改碼、不重跑 code-review。
---

# After Code Review：分流處置建議

接在 `/code-review` 之後：把雙軸 findings 分成可併入下一 commit（少可追溯）與應開票追蹤，並產出草稿。不執行 `gh issue create`、不改工作區程式碼、不重跑 review。

若 `docs/agents/issue-tracker.md` 或 `docs/agents/triage-labels.md` 存在，開票草稿對齊其慣例；缺檔則用通用 GitHub issue 形狀，label 字串仍建議 `needs-triage`。

---

## 步驟 1：取得輸入報告

優先從**同一對話**擷取完整的 `/code-review` 產出（需含 `## Standards` 與 `## Spec`，或明確註記 Spec 略過）。

- 有完整報告 → 以此為唯一輸入。
- 無報告，但使用者貼上同等結構的全文 → 接受貼文。
- 兩者皆無 → **硬失敗**：說明缺報告，請先跑 `/code-review` 或貼上完整報告。不自行重跑 review。

完成標準：手中有可逐條引用的 findings 清單（含軸別），或已硬失敗並停止。

---

## 步驟 2：逐條分流

對每一條 finding 只歸一桶（可選附註忽略）：

| 桶 | 意義 |
| :--- | :--- |
| **下一 commit** | 併入後續 commit 收尾；不開票；接受較少可追溯 |
| **開票** | 脫離本變更主線，需獨立追蹤 |
| **建議忽略**（附註，非預設桶） | 僅明確誤報，或 repo 文件標準已覆蓋／否決該 baseline smell |

**主準則 — 同變更親和**：仍屬這次 diff／這條 PR 未完成工作（缺實作、錯實作、本次引入的違規）→ 下一 commit；與本次無關的債務、後續重構、跨主題改善 → 開票。

**輔準則 — 成本／範圍**：雖同源，但需另開設計討論、大範圍調查、或獨立驗收 → 仍開票，不塞進下一 commit。

**忽略**：預設不用。只有誤報或標準覆蓋時才標「建議忽略」，並寫一句理由。

完成標準：每條 finding 都有桶別與一句分流理由（引用原報告要點即可）。

---

## 步驟 3：分軸呈現與打包

**維持 Standards / Spec 分欄**（不跨軸合併排序）。每一軸依序輸出：

1. **下一 commit**
2. **開票**
3. **建議忽略**（若有）

同一軸內多條「下一 commit」：預設建議**併成一個** follow-up commit，給一組訊息要點；僅在主題明顯無關時拆成多組。

開票項：每條給 title + body 草稿；建議 label **一律** `needs-triage`（本技能不做完整 triage）。Body 可附一句「後續 triage 方向」供人工參考，不假裝已選定 `ready-for-agent` / `ready-for-human`。

完成標準：兩軸（或僅有的一軸）皆已輸出；草稿可直接複製使用；全文未宣稱已開票或已改碼。

---

## 輸出模板

```markdown
# After code review

輸入：<同 session 報告 | 使用者貼文>

## Standards

### 下一 commit
- **打包**：<一組 | 拆成 N 組>
- **建議 commit 要點**：
  - …
- **Findings**：
  - <原 finding 摘要> — <分流理由>

### 開票
#### <title>
- **Label**：`needs-triage`
- **Body**：
  …
- **分流理由**：…

### 建議忽略
- <finding> — <理由>

## Spec

（同上結構；若 code-review 略過 Spec，註明並省略本節）

## 下一步（建議，不執行）
- 下一 commit：可接 `/prepare-commit` 或手動提交
- 開票：以草稿執行 `gh issue create`（需使用者自行確認）
```

---

## 邊界

- 不修改 `/code-review` 行為，不在其報告末尾自動鏈式呼叫本技能。
- 找不到輸入時只提示補報告，不補跑 review。
- 純建議：開票與修碼留待使用者確認後另行動作。
