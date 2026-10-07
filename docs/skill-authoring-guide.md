# Agent Skills 撰寫與驗證指南

> 建立日期：2026-10-07
> 最後更新：2026-10-07

新增自建技能、調整觸發範圍或排查技能漏做步驟時，使用本指南。文章與工作流的來源核對見 [研究筆記](skills-workflow-research.md)；已安裝技能功能見 [第三方技能手冊](third-party-skills.md)。

本文將第一手來源轉為本 repo 的實作建議；下列範例與檢查表為專案應用，不代表各來源的強制規範，也尚未構成本 repo 的模型效果評測。

## 1. 從實際失敗提取一個完整任務

先記錄一次真實任務的輸入、成功產物、人工修正與失敗原因，再決定是否需要技能。範圍應能形成一個可驗證結果；太大難以準確觸發，太碎則增加串接成本。來源：[Agent Skills 撰寫建議][practices]。

本 repo 的選擇順序：

| 需要保存的內容 | 優先位置 | 取捨 |
| --- | --- | --- |
| 已有技能涵蓋的操作方法 | 使用既有技能，補必要的專案參考 | 避免產生兩套相同流程 |
| 跨任務共用的行為規則 | `shared/` | 常駐成本高，只保留共通約束 |
| 新的可重用任務流程 | `custom-skills/<name>/SKILL.md` | 可獨立觸發，但需維護與評測 |
| 研究證據與設計理由 | `docs/`，由入口按情境連入 | 保留可追溯性，不擴大技能本體 |

上述目錄分工依 [AGENTS.md](../AGENTS.md)；第三方技能由 CLI 管理，專案增補保存在自有文件。

## 2. 先寫觸發條件，再寫流程

`description` 說明任務與適用情境。用使用者會提出的需求描述範圍，並以相近但不適用的案例檢查邊界；只寫「協助文件」難以可靠選中技能。來源：[描述優化指南][descriptions]。

依本 repo 的 Context Pointer 原則，關鍵動詞或領域名詞放前面；一個任務分支對應一個觸發條件。來源：[writing-for-agents][writing]。

例如「檢查技能清單是否漏列已安裝項目」與「撰寫全新技能」是不同任務。前者的描述可寫為：

```yaml
description: >-
  Audit the documented skill inventory against installed SKILL.md files.
  Use when checking missing entries or stale skill names in an inventory.
```

## 3. 把步驟寫成可判定的完成條件

每步定義完成證據，避免以「充分理解」「仔細檢查」作為終點。若技能會交接，交接物要足以讓下一步繼續。來源：[writing-for-agents][writing]。

以下為本 repo 的清單稽核設計範例，尚未新增為技能：

| 步驟 | 完成證據 | 異常分支 |
| --- | --- | --- |
| 讀取指定清單與技能目錄 | 記錄實際讀取路徑與技能名稱 | 缺少必要路徑時列出缺項 |
| 比對已安裝技能與文件條目 | 每個差異有名稱、檔案位置及類型 | 無法解析的檔案列為未驗證 |
| 產出報告 | 區分漏列、過時條目與未驗證項目 | 零差異時仍交代檢查範圍 |

寫入操作另依使用者授權與專案規則判斷；研究或稽核的產物本身不等於部署指令。

## 4. 主流程留在本體，分支資料按需讀取

共同步驟放 `SKILL.md`；特定情境才需要的規格放 `references/`，並寫明讀取條件。格式規範建議本體低於 500 行、5,000 tokens，這是整理方向，不是品質達標線。來源：[Agent Skills 規範][spec]。

例如：「僅在清單名稱與 frontmatter 不一致時，讀取 `references/naming.md` 判定命名規則。」比「更多資訊見 references」更容易執行。概念、限制與例外宜放在一起；保留單一規範來源。來源：[writing-for-agents][writing]。

## 5. 給預設做法與具體例外

流程指定一個合理預設，再列出切換條件。反覆出現的解析或驗證程式可抽成附帶腳本；有固定格式的產物可提供小型範本。來源：[Agent Skills 撰寫建議][practices]。

本 repo 的例子：以 `skills-lock.json` 查第三方來源，以實際 `SKILL.md` 確認已安裝行為；兩者不一致時回報差異。新增指南不複製完整技能清單，直接連至既有手冊。

## 6. 分清格式標準與平台擴充

可攜技能保留 `name` 與 `description`；名稱需符合規範並與目錄一致，描述上限為 1,024 字元。其他欄位與腳本相依需按目標平台確認。來源：[Agent Skills 規範][spec]。

Claude Code 的 `disable-model-invocation: true` 可控制手動觸發，`context: fork` 可指定子代理執行，兩者均為平台擴充。這些機制不能直接推論為其他客戶端的行為；跨平台部署須分別驗證。來源：[Claude Code skills 文件][claude]。

## 7. 分開驗證「有沒有觸發」與「做得對不對」

| 驗證層 | 方法 | 記錄內容 |
| --- | --- | --- |
| 觸發 | 真實語句、間接需求、相近反例；觀察是否載入技能 | 漏觸發、誤觸發、客戶端與模型 |
| 產物 | 相同任務比較有技能與無技能，或新版與舊版 | 正確性、缺項、實際輸出證據 |
| 成本 | 查看執行軌跡，而不只最終答覆 | 多餘步驟、耗時與可取得的 token 用量 |

觸發評測依 [描述優化指南][descriptions]；產物與成本比較依 [品質評測指南][evals]。後者建議從 2–3 個案例開始，每次使用乾淨脈絡；這個數量不是穩定性保證。修改後保留未參與調整的案例，避免只對測試措辭有效。

清單稽核範例的初始案例可為：正常清單、漏列一項、來源檔案不存在。斷言檢查差異是否正確及缺項是否明示；不要求固定句子。觸發反例可用「幫新技能寫 description」，確認不會誤進清單稽核。

## 8. 在本 repo 交付前檢查

- [ ] 自建技能名稱未與第三方技能衝突。
- [ ] 輸入、產物、完成條件與已知失敗分支明確。
- [ ] 每個外部參考有讀取條件；部署後的相對路徑仍可解析。
- [ ] 需要跨平台能力時，記錄已驗證與未驗證的客戶端。
- [ ] 更新建立／最後更新日期，從適當入口連入文件。
- [ ] 依變更範圍完成格式、連結與必要評測，記錄未執行項目。
- [ ] 提交前執行 `make test`；技能或模板變更另檢查編譯產物。

此清單為本 repo 的交付建議。`make test` 驗證專案程式，不代表技能觸發率或產物品質已通過模型評測。既有測試與來源分工要求見 [AGENTS.md](../AGENTS.md)。

[practices]: https://agentskills.io/skill-creation/best-practices
[descriptions]: https://agentskills.io/skill-creation/optimizing-descriptions
[writing]: https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md
[spec]: https://agentskills.io/specification
[claude]: https://code.claude.com/docs/en/skills
[evals]: https://agentskills.io/skill-creation/evaluating-skills
