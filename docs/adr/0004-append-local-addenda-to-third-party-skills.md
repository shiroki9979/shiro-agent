# ADR-0004：以編譯時附加的本地補充段落調整第三方技能

> - Created: 2026-10-25
> - Last Updated: 2026-10-25
> - Author: Bo-Xue Huang
> - Status: 核准
> - Related: [ADR-0002](0002-separate-custom-and-third-party-skills.md)

---

## 1. Context

[ADR-0002](0002-separate-custom-and-third-party-skills.md) 將第三方技能視為由 `npx skills` 管理的靜態依賴，`.agents/skills/` 內容須與 `skills-lock.json` 雜湊一致，直接修改會在 `make skills-update` 時被覆寫。

實際使用時，部分第三方技能需要補上本地資訊才能正確運作。以 `code-review` 審查 shiro-mlops PR #85 為例：

- 固定點為 PR 編號時，技能仍以 `HEAD`（本地分支）計算 diff，需手動改為比對 PR 的 base 與 head。
- Standards 軸只搜尋 repo 內的規範檔，看不到 `shared/coding-style.md` 的共用規範。
- 只讀 diff 的審查漏掉 Nginx 重導丟失連接埠與含點路由 404，實際執行設定才發現。

上游更新頻繁（`code-review` 於 2026-08 至 2026-10 間有 10 次提交），本地調整需能在同步上游後持續生效。

## 2. Decision

新增 `skill-addenda/<技能名稱>.md`。`scripts/build.py` 編譯第三方技能時，將對應檔案展開 `<!-- INCLUDE:... -->` 後附加至輸出的 `SKILL.md` 結尾；`.agents/skills/` 原檔不變。補充段落自行聲明在衝突時優先於上游步驟。

補充段落只能對應 `.agents/skills/` 中存在的第三方技能；名稱對不到或指向自建技能時，編譯中斷並報錯。

### Rationale & Alternatives Considered

- **選定方案（編譯時附加）**：上游更新照常同步；補充段落可透過 INCLUDE 引用 `shared/`，維持單一真實來源；同一機制可套用於其他需要本地調整的第三方技能（如 `domain-modeling` 的術語檔名稱）。
- **候選方案 A（Fork 為自建技能）**：完全掌控內容，但需從鎖定檔移除第三方版本，之後每次上游更新都要手動移植。
- **候選方案 B（自建包裝技能，呼叫第三方技能後補充指示）**：不需修改編譯流程，但僅在使用者明確呼叫包裝技能時生效；直接呼叫原技能或由模型自動選用時，補充內容不會載入。
- **候選方案 C（向上游提交 PR）**：可惠及其他使用者，但共用規範屬本地需求無法上游化，且接受與否及時程不確定；可與選定方案並行，上游合併後刪除對應補充段落。

## 3. Consequences

- **正面效益（Positive）**：第三方技能可依本地環境調整而不失去上游更新；`npx skills` 的雜湊檢查維持有效。
- **代價與風險（Trade-offs & Risks）**：
  - 部署後的技能內容與上游原檔不同，排查技能行為時需同時檢視 `skill-addenda/`。
  - 補充段落附加於檔尾，與上游步驟衝突時依賴措辭界定優先順序；上游大幅改寫後，補充段落可能引用已不存在的步驟編號，需於同步上游時一併檢查。
- **不做／延後範圍（Out of Scope / Deferred）**：不支援插入至上游檔案中段或修改上游段落；不支援非 `SKILL.md` 檔案的補充。

## 4. Compliance

- [tests/test_build.py](../../tests/test_build.py) 的 `test_compile_skills_appends_addendum_to_third_party_skill` 驗證附加內容、INCLUDE 展開及上游原檔不變；`test_compile_skills_rejects_addendum_without_third_party_skill` 驗證名稱對不到或指向自建技能時中斷。
- 執行 `make test` 與 `make build` 確保編譯與測試通過。
- 同步上游技能（`make skills-update`）後，人工比對 `skill-addenda/` 中引用的步驟名稱是否仍存在於上游 `SKILL.md`；無自動化強制機制。

## 5. Notes

- **與既有決策的關係**：延伸 [ADR-0002](0002-separate-custom-and-third-party-skills.md)；第三方技能原檔仍維持靜態，僅編譯輸出附加本地內容，未取代該決策。
- **實作與遷移紀錄**：首個補充段落為 [skill-addenda/code-review.md](../../skill-addenda/code-review.md)，處理 PR 固定點、共用規範與執行期設定驗證。
