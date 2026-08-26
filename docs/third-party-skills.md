# 第三方 Agent Skills 功能與架構參考手冊

建立日期：2026-08-24  
最後更新：2026-08-26  

本文件詳細彙整 [.agents/skills/](../.agents/skills) 目錄下透過社群標準 CLI（`npx skills` / [skills-lock.json](../skills-lock.json)）安裝之 53 個第三方 Agent Skills。內容涵蓋套件來源、觸發情境、運作機制、輸出產物與核心工作流程。

---

## 1. 技能總覽與分類架構

目前的 53 個第三方技能主要源自 `mattpocock/skills`（36 個）、`anthropics/skills`（16 個）與 `vercel-labs/skills`（1 個 `find-skills`），依軟體開發生命週期與功能定位分為 11 大類別：

| 分類領域 | 包含技能 | 核心功能摘要 |
| :--- | :--- | :--- |
| **1. 流程導航與探索** | [`ask-matt`](../.agents/skills/ask-matt/SKILL.md), [`find-skills`](../.agents/skills/find-skills/SKILL.md) | 技能路由器、開源生態系技能搜尋與安裝 |
| **2. 需求質詢與決策** | [`grilling`](../.agents/skills/grilling/SKILL.md), [`grill-me`](../.agents/skills/grill-me/SKILL.md), [`grill-with-docs`](../.agents/skills/grill-with-docs/SKILL.md), [`to-questionnaire`](../.agents/skills/to-questionnaire/SKILL.md), [`wait-what`](../.agents/skills/wait-what/SKILL.md) | 設計樹質詢原型、無狀態/狀態化訪談、問卷生成、重述對齊 |
| **3. 宏觀規劃與迷霧探索** | [`wayfinder`](../.agents/skills/wayfinder/SKILL.md) | 超大型任務決策地圖（Map）與決策工單驅散戰爭迷霧 |
| **4. 領域建模與架構設計** | [`domain-modeling`](../.agents/skills/domain-modeling/SKILL.md), [`codebase-design`](../.agents/skills/codebase-design/SKILL.md), [`improve-codebase-architecture`](../.agents/skills/improve-codebase-architecture/SKILL.md), [`setup-ts-deep-modules`](../.agents/skills/setup-ts-deep-modules/SKILL.md) | 領域語言收斂與 ADR 門檻、深模組（Deep Module）設計詞彙、視覺化架構報告、TypeScript 邊界隔離配置 |
| **5. 規格制定與工單拆分** | [`to-spec`](../.agents/skills/to-spec/SKILL.md), [`to-tickets`](../.agents/skills/to-tickets/SKILL.md) | 對話無訪談綜合規格書、Tracer-bullet 垂直切片與阻擋依賴工單拆解 |
| **6. 開發實作與測試驅動** | [`implement`](../.agents/skills/implement/SKILL.md), [`implement-spec`](../.agents/skills/implement-spec/SKILL.md), [`tdd`](../.agents/skills/tdd/SKILL.md), [`prototype`](../.agents/skills/prototype/SKILL.md), [`migrate-to-shoehorn`](../.agents/skills/migrate-to-shoehorn/SKILL.md), [`frontend-design`](../.agents/skills/frontend-design/SKILL.md), [`mcp-builder`](../.agents/skills/mcp-builder/SKILL.md), [`webapp-testing`](../.agents/skills/webapp-testing/SKILL.md), [`skill-creator`](../.agents/skills/skill-creator/SKILL.md) | 單 Session/多 Agent 並行實作、TDD 垂直切片、邏輯與 UI 拋棄式原型、測試型別斷言遷移、反模板化前端視覺、MCP Server 建構、Playwright 本機測試、Skill 撰寫與評測 |
| **7. 程式碼審查與除錯維護** | [`code-review`](../.agents/skills/code-review/SKILL.md), [`diagnosing-bugs`](../.agents/skills/diagnosing-bugs/SKILL.md), [`resolving-merge-conflicts`](../.agents/skills/resolving-merge-conflicts/SKILL.md) | 規範與需求雙軸並行 Code Review、頑固 Bug 與效能回歸診斷閉環、Git 意圖衝突解決 |
| **8. 工單分流與儲存庫配置** | [`setup-matt-pocock-skills`](../.agents/skills/setup-matt-pocock-skills/SKILL.md), [`triage`](../.agents/skills/triage/SKILL.md) | 儲存庫 Issue Tracker 與標籤初始化配置、議題與外部 PR 狀態機分流 |
| **9. 交接、輔助與寫作系統** | [`handoff`](../.agents/skills/handoff/SKILL.md), [`claude-handoff`](../.agents/skills/claude-handoff/SKILL.md), [`research`](../.agents/skills/research/SKILL.md), [`wizard`](../.agents/skills/wizard/SKILL.md), [`teach`](../.agents/skills/teach/SKILL.md), [`loop-me`](../.agents/skills/loop-me/SKILL.md), [`writing-for-agents`](../.agents/skills/writing-for-agents/SKILL.md), [`writing-fragments`](../.agents/skills/writing-fragments/SKILL.md), [`writing-shape`](../.agents/skills/writing-shape/SKILL.md), [`writing-beats`](../.agents/skills/writing-beats/SKILL.md), [`git-guardrails-claude-code`](../.agents/skills/git-guardrails-claude-code/SKILL.md), [`setup-pre-commit`](../.agents/skills/setup-pre-commit/SKILL.md), [`scaffold-exercises`](../.agents/skills/scaffold-exercises/SKILL.md), [`doc-coauthoring`](../.agents/skills/doc-coauthoring/SKILL.md), [`internal-comms`](../.agents/skills/internal-comms/SKILL.md) | 對話交接文件/背景派發、一手來源研究、人工操作互動式嚮導、長期教學工作區、生活工作流規格化、Agent 文件寫作準則、寫作三部曲、Git 防護鉤子、Pre-commit 與練習題骨架、結構化共寫文件、內部溝通套版 |
| **10. 文件產製與編輯** | [`docx`](../.agents/skills/docx/SKILL.md), [`pptx`](../.agents/skills/pptx/SKILL.md), [`pdf`](../.agents/skills/pdf/SKILL.md), [`xlsx`](../.agents/skills/xlsx/SKILL.md) | Word／PowerPoint／PDF／試算表之建立、讀取、編輯與轉換（Anthropic source-available，非 Apache 2.0） |
| **11. 視覺設計與生成產出** | [`canvas-design`](../.agents/skills/canvas-design/SKILL.md), [`algorithmic-art`](../.agents/skills/algorithmic-art/SKILL.md), [`theme-factory`](../.agents/skills/theme-factory/SKILL.md), [`brand-guidelines`](../.agents/skills/brand-guidelines/SKILL.md), [`slack-gif-creator`](../.agents/skills/slack-gif-creator/SKILL.md), [`web-artifacts-builder`](../.agents/skills/web-artifacts-builder/SKILL.md) | 靜態海報／藝術 PNG／PDF、p5.js 生成藝術、工件主題套用、Anthropic 品牌樣式、Slack GIF、複雜 React HTML artifact |

---

## 2. 標準主流程（Main Flow: Idea → Ship）

Matt Pocock 技能體系定義了一套從構想到交付的標準工作流路徑：

```text
[ Idea / 構想 ]
      │
      ▼
[/grill-with-docs] ──(需驗證狀態/UI)──► [/handoff] ──► [/prototype] ──► [/handoff]
      │                                                                     │
      ▼                                                                     │
(確認為多 Session 專案?) ◄───────────────────────────────────────────────────┘
 ├── 是 ──► [/to-spec] ──► [/to-tickets] ──(單一 Ticket 清理 Context)──► [/implement]
 └── 否 ─────────────────────────────────────────────────────────────────► [/implement]
                                                                                │
                                           ┌────────────────────────────────────┘
                                           ▼
                                   [/tdd] (紅綠循環切片)
                                           │
                                           ▼
                                   [/code-review] (雙軸審查: Standards + Spec)
                                           │
                                           ▼
                                      [ Commit / PR ]
```

---

## 3. 各技能詳細功能說明

### 類別 1：流程導航與生態探索 (Routing & Discovery)

#### [`ask-matt`](../.agents/skills/ask-matt/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/ask-matt/`)
- **觸發情境**：使用者不確定當前工作階段該使用哪一個技能或工作流時呼叫。
- **功能描述**：技能體系的頂層路由器（Router）。內建完整的「Idea → Ship」主流程、三條匯入主流程的匝道（On-ramps：Triage, Diagnosing, Wayfinder）、程式碼健康維護與底層語彙對照表。
- **輸入 / 輸出**：接收使用者當前情境描述，輸出推薦執行的技能名稱與下一步工作指引。

#### [`find-skills`](../.agents/skills/find-skills/SKILL.md)

- **來源**：`vercel-labs/skills` (`skills/find-skills/`)
- **觸發情境**：使用者詢問「是否有技能可以做 X」、「如何擴充 Agent 能力」或尋找特定工具/框架外掛時。
- **功能描述**：透過 `npx skills find` 與 [skills.sh](https://skills.sh/) 搜尋開源生態系中的 Agent 技能，並依據安裝量、來源信譽與 GitHub Stars 進行品質把關後提供安裝指令。
- **輸入 / 輸出**：關鍵字查詢，輸出推薦技能名稱、來源、安裝指令（`npx skills add <pkg> -g -y`）。

---

### 類別 2：需求質詢與決策 (Grilling & Decision Making)

#### [`grilling`](../.agents/skills/grilling/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/productivity/grilling/`)
- **觸發情境**：壓力測試構想、檢驗設計邊界或任何包含 `grill` 觸發詞之場景。
- **功能描述**：質詢機制的底層核心（Primitive）。將決策建模為「設計樹（Design Tree）」，按輪次（Rounds）推進「前沿邊界（Frontier）」。每輪一次性提出前提已滿足的全部問題，為每題編號並附上建議答案。環境事實由 Agent 自行查證，決策留給使用者裁定。
- **輸入 / 輸出**：使用者構想或需求，輸出逐輪結構化問答與收斂後的決策清單。

#### [`grill-me`](../.agents/skills/grill-me/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/productivity/grill-me/`)
- **觸發情境**：在**無專案儲存庫/無工作目錄**的情境下（例如思考獨立演算法、文章或抽象計畫），進行純對話式高強度質詢。
- **功能描述**：無狀態（Stateless）包裝器，內部直接呼叫 `grilling`，不落盤產出 `CONTEXT.md` 或 ADR。

#### [`grill-with-docs`](../.agents/skills/grill-with-docs/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/grill-with-docs/`)
- **觸發情境**：在**工作目錄/專案庫**中釐清需求或進行架構設計時。
- **功能描述**：狀態化（Stateful）質詢流程。內部同時組合呼叫 `grilling` 與 `domain-modeling`，在推進質詢決策的同時，即時且同步更新 `CONTEXT.md` 術語表，並在符合條件時建立架構決策紀錄（ADR）。

#### [`to-questionnaire`](../.agents/skills/to-questionnaire/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/productivity/to-questionnaire/`)
- **觸發情境**：關鍵決策所需的資訊不在使用者腦中，而在第三方或特定利害關係人（如 PM、客戶、資深工程師）身上時。
- **功能描述**：將單向質詢反轉為對外部對象的探索問卷。Agent 不對技術本體提問，而是質詢「發送目標（誰來填寫、角色、信任關係）」與「預期產出（需要帶回什麼具體決策）」，生成 Markdown 問卷文件（`to-questionnaire-<slug>.md`）。
- **輸入 / 輸出**：受訪者資訊與決策缺口，輸出排版完善且依主題分組的非同步問卷文件。

#### [`wait-what`](../.agents/skills/wait-what/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/productivity/wait-what/`)
- **觸發情境**：使用者在任何對話過程中發現 Agent 解釋過於晦澀、術語混亂或難以理解時。
- **功能描述**：中斷當前節奏並強制重述。要求 Agent 以簡化技術英語（ASD-STE100 Simplified Technical English）風格與 `CONTEXT.md` 的通用語言，重新說明當前進度與脈絡。

---

### 類別 3：宏觀規劃與迷霧探索 (Wayfinding & Large Efforts)

#### [`wayfinder`](../.agents/skills/wayfinder/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/wayfinder/`)
- **觸發情境**：面對跨多個 Session、範圍巨大且前方路徑模糊的專案（如全新大型系統、架構重構、完整課程規劃）時。
- **功能描述**：
  - **產出決策而非交付物**：在 Issue Tracker 上建立標記為 `wayfinder:map` 的索引地圖（Map Issue），底下掛載子工單（Decision Tickets）。
  - **工單類型**：區分為 `research`（AFK 背景調查）、`prototype`（HITL 拋棄式原型）、`grilling`（HITL 訪談）、`task`（手動解鎖操作）。
  - **戰爭迷霧（Fog of War）**：地圖維護「已決策（Decisions so far）」、「未明確（Not yet specified，迷霧區域）」與「範圍外（Out of scope）」。每解決一張工單即推進前沿並解鎖新工單。
  - **單 Session 單工單原則**：每個對話 Session 僅專注處理一張決策工單，完成後將摘要回填地圖並關閉工單。

---

### 類別 4：領域建模與架構設計 (Domain Modeling & Codebase Design)

#### [`domain-modeling`](../.agents/skills/domain-modeling/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/domain-modeling/`)
- **觸發情境**：定義/調整領域模型、修改 `CONTEXT.md` 詞彙表或評估是否建立 ADR 時。
- **功能描述**：主動挑戰模糊或超載的領域名詞（如區分 User vs Customer），強制維護領域語言純度。嚴格規範 `CONTEXT.md` 僅能包含通用詞彙（Glossary），不可寫入實作細節；並把關 ADR 建立三大門檻（難以逆轉、無脈絡下令人意外、源自真實取捨）。

#### [`codebase-design`](../.agents/skills/codebase-design/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/codebase-design/`)
- **觸發情境**：模組介面設計、尋找深模組重構機會、劃分測試邊界（Seam）或供其他技能調用共用語彙時。
- **功能描述**：深模組（Deep Modules）架構底層規範。定義專用精確語彙：**Module**（模組）、**Interface**（介面完整知識面）、**Depth**（深度/槓桿率）、**Seam**（接縫）、**Adapter**（適配器）、**Leverage**（槓桿）、**Locality**（局部性）。提出「刪除測試（Deletion Test）」：若刪除模組會使複雜度回流至多個呼叫端，該模組即具備高價值。

#### [`improve-codebase-architecture`](../.agents/skills/improve-codebase-architecture/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/improve-codebase-architecture/`)
- **觸發情境**：系統定期架構維護、尋找淺模組改善空間以提升可測試性與 AI 可導航性時。
- **功能描述**：掃描 Git Commit 熱點與程式碼摩擦點，於系統暫存目錄產出獨立美觀的 HTML 視覺化架構報告（使用 Tailwind CDN 與 Mermaid 繪製 Before/After 圖表）。使用者選定候選項目後，直接進入 `grilling` 深入設計重構方案。

#### [`setup-ts-deep-modules`](../.agents/skills/setup-ts-deep-modules/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/in-progress/setup-ts-deep-modules/`)
- **觸發情境**：TypeScript 專案需要強制落實套件邊界封裝，避免內部私有檔案被深層匯入（Deep Import）時。
- **功能描述**：配置 `dependency-cruiser` 規則，強制套件僅能透過根目錄進入點（Root Entry Points，如 `index.ts`, `client.ts`）對外暴露，所有子目錄（`lib/`, `tests/`）皆視為內部私有，並透過暫時性違規匯入進行驗證。

---

### 類別 5：規格制定與工單拆分 (Spec Writing & Ticket Breakdown)

#### [`to-spec`](../.agents/skills/to-spec/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/to-spec/`)
- **觸發情境**：對話訪談收斂後，將討論結果轉化為標準規格文件並發布至 Issue Tracker。
- **功能描述**：**不進行額外提問**，純粹綜合當前上下文資訊。依標準模板產出：問題陳述、解決方案、詳盡使用者故事（User Stories）、實作決策（不含易過期的具體檔案路徑）、測試決策（明確約定 Seam）與範圍外事項（Out of Scope），標記為 `ready-for-agent`。

#### [`to-tickets`](../.agents/skills/to-tickets/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/to-tickets/`)
- **觸發情境**：規格書完成後，需要拆解為可獨立執行之開發工單時。
- **功能描述**：將規格切分為端到端垂直切片（Tracer-bullet）工單，每張工單皆明確宣告阻擋依賴邊（Blocking Edges）。針對大範圍破壞性重構（Wide Refactor）自動套用 **Expand–Contract** 策略。支援發布至本地 Markdown（`.scratch/<feature>/issues/`）或線上 Issue Tracker（GitHub / GitLab / Linear）。

---

### 類別 6：開發實作與測試驅動 (Implementation, TDD & Testing)

#### [`implement`](../.agents/skills/implement/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/implement/`)
- **觸發情境**：單一 Session 內依據規格或單張工單執行具體編碼。
- **功能描述**：於約定的 Seam 上驅動 `tdd` 進行垂直切片開發，定期執行型別檢查與單元測試，完成後調用 `code-review` 驗證，並提交至當前分支。

#### [`implement-spec`](../.agents/skills/implement-spec/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/in-progress/implement-spec/`)
- **觸發情境**：需要並行交付整份包含多工單任務圖（Task Graph）之完整規格時。
- **功能描述**：多代理協同模式。解析工單相依關係，建立 Draft PR，利用背景 Sub-agents 在獨立 Git Worktree 中並行實作前沿（Frontier）工單，透過 Merger Agent 逐步合併至 PR 分支，最後統整執行 `code-review`。

#### [`tdd`](../.agents/skills/tdd/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/tdd/`)
- **觸發情境**：以測試先行方式開發功能或修復 Bug。
- **功能描述**：落實嚴格的 Red → Green → Refactor 循環。原則包括：僅在公開介面接縫（Seam）測試、禁止實作細節耦合測試、禁止同構斷言（Tautological Assertions）、禁止預先寫滿全部測試的水平切片（Horizontal Slicing），每次僅專注一個垂直切片。

#### [`prototype`](../.agents/skills/prototype/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/prototype/`)
- **觸發情境**：設計決策難以在紙上定案，需透過可執行程式碼驗證狀態邏輯或介面外觀時。
- **功能描述**：拋棄式原型工具，分為兩大分支：
  - **狀態邏輯驗證**：產出單一可點擊互動的 HTML 檔案，包含狀態機切換與引導式演練。
  - **UI 外觀探索**：在單一路由上提供多種視覺風格切換（透過 URL 參數與底部懸浮控制列）。
  - 驗證完成後將決策融入正式程式碼，原型作為一手來源提交至 `prototype/<name>` 分支保存。

#### [`migrate-to-shoehorn`](../.agents/skills/migrate-to-shoehorn/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/misc/migrate-to-shoehorn/`)
- **觸發情境**：測試程式碼充斥 `as Type` 或 `as unknown as Type` 假資料斷言時。
- **功能描述**：安裝並遷移至 `@total-typescript/shoehorn`。將局部型別模擬改為 `fromPartial()`，將故意出錯的測試資料改為 `fromAny()`，確保僅在測試範圍內安全模擬型別。

#### [`frontend-design`](../.agents/skills/frontend-design/SKILL.md)

- **來源**：`anthropics/skills` (`skills/frontend-design/`)
- **觸發情境**：建立新 UI 或重構現有介面，需要具備辨識度、量身定制之視覺風格、排版與字體設計時。
- **功能描述**：反模板化（Anti-templated）前端視覺設計指引。核心要素包括：
  - **主題收斂**：在設計前明確鎖定主題本質、受眾與單一核心任務，由業務領域名詞推導視覺語彙。
  - **設計原則**：Hero 區塊作為論點、字型承載個性（Display / Body 搭配）、結構即資訊（避免無意義序號裝飾）、克制使用動態微互動與高維度文案。
  - **兩階段規劃**：第一階段規劃精簡 Token 系統（4–6 色彩 Palette、字型組合、ASCII Wireframe 版面、Signature 記憶點）；第二階段自我審查並剔除 AI 常見預設套路後再行實作。

#### [`mcp-builder`](../.agents/skills/mcp-builder/SKILL.md)

- **來源**：`anthropics/skills` (`skills/mcp-builder/`)
- **觸發情境**：建立 MCP Server 以讓 LLM 透過工具介接外部 API 或服務時（Python FastMCP 或 TypeScript MCP SDK）。
- **功能描述**：四階段建構指引：研究與規劃（tool 命名、分頁、錯誤訊息）、實作（Zod／Pydantic schema、annotations）、審查測試（MCP Inspector）、撰寫唯讀評測題組。附 Python／TypeScript 實作參考與 evaluation 格式。

#### [`webapp-testing`](../.agents/skills/webapp-testing/SKILL.md)

- **來源**：`anthropics/skills` (`skills/webapp-testing/`)
- **觸發情境**：驗證本機 Web 應用前端行為、除錯 UI、擷取瀏覽器截圖或 console log 時。
- **功能描述**：以 Python Playwright 撰寫自動化腳本。內建 `with_server.py` 管理開發伺服器生命週期；採偵察後行動（先等 `networkidle`、截圖／探勘 DOM，再以發現的 selector 執行動作）。

#### [`skill-creator`](../.agents/skills/skill-creator/SKILL.md)

- **來源**：`anthropics/skills` (`skills/skill-creator/`)
- **觸發情境**：從零建立 skill、修改既有 skill、跑 eval、或優化 `description` 觸發準確度時。
- **功能描述**：指導 SKILL.md 結構（frontmatter 觸發、漸進式揭露、scripts／references／assets）、反覆評測與 description 優化，避免 under-trigger。

---

### 類別 7：程式碼審查與除錯維護 (Review, Debugging & Merge)

#### [`code-review`](../.agents/skills/code-review/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/code-review/`)
- **觸發情境**：審查分支、PR 或相對於特定 Git 錨點（Fixed Point）之變更時。
- **功能描述**：**雙軸獨立平行審查**。透過兩個互不干擾的平行 Sub-agents 同時檢查：
  1. **Standards 軸**：檢查是否違反專案編碼規範及內建的 12 項 Fowler Code Smells 基準。
  2. **Spec 軸**：比對原始規格，揪出未實作項目、範圍蔓延（Scope Creep）與實作錯誤。
  - 雙軸報告並列呈現，不互相稀釋或重新加權排序。

#### [`diagnosing-bugs`](../.agents/skills/diagnosing-bugs/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/diagnosing-bugs/`)
- **觸發情境**：遭遇頑固 Bug、間歇性錯誤或效能衰退時。
- **功能描述**：6 階段嚴格除錯閉環：
  - **Phase 1: Build a feedback loop**（核心關鍵：建立秒級、確定性、可自動執行的 Tight Red Loop，未建立前嚴禁推測假說）。
  - **Phase 2: Reproduce + minimise**（最小化重現路徑，剔除無關變數）。
  - **Phase 3: Hypothesise**（提出 3–5 個具備可偽證性的排序假說）。
  - **Phase 4: Instrument**（針對假說單變量插樁，使用唯一標籤如 `[DEBUG-xxxx]`）。
  - **Phase 5: Fix + regression test**（在正確接縫建立回歸測試後套用修復）。
  - **Phase 6: Cleanup**（驗證修復、清除所有除錯日誌與拋棄式程式碼）。

#### [`resolving-merge-conflicts`](../.agents/skills/resolving-merge-conflicts/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/resolving-merge-conflicts/`)
- **觸發情境**：Git Merge 或 Rebase 過程中發生衝突時。
- **功能描述**：檢視衝突雙方的 Git Commit 與原始 PR/工單意圖，按區塊（Hunk）在保留雙方核心意圖的前提下進行語意整合，嚴禁擅自 `--abort` 或隨意保留單邊行數，並於解決後執行自動化驗證。

---

### 類別 8：工單分流與儲存庫配置 (Issue Triage & Tracker Integration)

#### [`setup-matt-pocock-skills`](../.agents/skills/setup-matt-pocock-skills/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/setup-matt-pocock-skills/`)
- **觸發情境**：新專案首次使用工程技能套件時之初始化配置。
- **功能描述**：引導設定 Issue Tracker（GitHub / GitLab / 本地 Markdown）、分流標籤詞彙表（`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`）與領域文件路徑結構（單一上下文 vs 多上下文），產出 `docs/agents/*.md`。

#### [`triage`](../.agents/skills/triage/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/triage/`)
- **觸發情境**：維護者整理未處理之 Issues 或外部 PRs 時。
- **功能描述**：議題狀態機管理。分類 `bug` / `enhancement`，驗證重現路徑與程式碼重複性；必要時發起質詢，為合格工單產出可直接派發給 Agent 執行的 Agent Brief，或將拒絕項目歸檔至 `.out-of-scope/`。

---

### 類別 9：交接、輔助與寫作系統 (Handoff, Automation & Writing)

#### [`handoff`](../.agents/skills/handoff/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/productivity/handoff/`)
- **觸發情境**：需結束當前 Session 並將上下文轉移至全新 Agent、新工作目錄或同事時。
- **功能描述**：將對話重點壓縮為可攜式 Markdown 交接摘要，儲存於使用者作業系統的暫存目錄（避免污染專案庫），並包含建議下一個 Agent 調用的技能列表與敏感資訊過濾。

#### [`claude-handoff`](../.agents/skills/claude-handoff/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/in-progress/claude-handoff/`)
- **觸發情境**：在 Claude Code 環境中，將工作立即派發給背景 Agent 接續執行。
- **功能描述**：產出交接摘要後，直接於系統背景呼叫 `claude --bg --name "<name>" "<summary>"` 啟動非同步執行個體。

#### [`research`](../.agents/skills/research/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/research/`)
- **觸發情境**：需要深度閱讀官方文件、原始碼或 API 規範等一手來源時。
- **功能描述**：啟動背景 Agent 針對一手高信任來源進行閱讀與查證，產出帶有精確引用來源的 Markdown 研究筆記檔案，讓主 Session 可持續進行其他工作。

#### [`wizard`](../.agents/skills/wizard/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/engineering/wizard/`)
- **觸發情境**：需要引導人類完成 Agent 無法代勞的手動操作（如雲端主機開通、第三方後台點擊、API 金鑰申請、一次性遷移）時。
- **功能描述**：生成互動式 Bash 嚮導腳本（基於標準化模板），具備跨平台開啟瀏覽器網頁、隱藏金鑰輸入、自動寫入 `.env` 與 GitHub Secrets、分段確認與進度展示等功能。

#### [`teach`](../.agents/skills/teach/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/productivity/teach/`)
- **觸發情境**：跨 Session 長期學習特定領域知識或技能。
- **功能描述**：將當前目錄視為教學工作區，維護 `MISSION.md`、`RESOURCES.md`、`learning-records/` 與美觀自包含的 HTML 課程（`lessons/*.html`），透過難度適中（Zone of Proximal Development）的提取練習強化長期記憶。

#### [`loop-me`](../.agents/skills/loop-me/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/in-progress/loop-me/`)
- **觸發情境**：梳理使用者日常生活或開發流程中的重複循環並規格化為工作流程時。
- **功能描述**：以循環鏡頭（Loop Lens）質詢使用者習慣與觸發條件（Trigger/Checkpoint/Push-right/Brief），產出 `workflows/*.md` 規格。

#### [`writing-for-agents`](../.agents/skills/writing-for-agents/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/productivity/writing-for-agents/`)
- **觸發情境**：撰寫或修改 Agent 技能（`SKILL.md`）、`AGENTS.md` 或 `CLAUDE.md` 時。
- **功能描述**：為 Agent 設計文件的頂層指導方針。核心概念包括：上下文指針（Context Pointer）、上下文負載與認知負載權衡、漸進式揭露（Progressive Disclosure）、明確完成條件（Completion Criteria）、前置詞（Leading Words）與冗餘修剪（Pruning）。

#### [`writing-fragments`](../.agents/skills/writing-fragments/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/in-progress/writing-fragments/`)
- **觸發情境**：寫作探索初期（Explore 階段），收集靈感與原始素材。
- **功能描述**：透過發散式訪談收集金句、論點、代碼片段或前置詞碎片，無結構地累加記錄於單一 Markdown 文件中。

#### [`writing-shape`](../.agents/skills/writing-shape/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/in-progress/writing-shape/`)
- **觸發情境**：寫作提煉階段（Exploit 階段），將碎片礦山雕塑為結構化文章。
- **功能描述**：界定讀者認知前提（Grounding），段落式推進寫作，針對段落形式（散文/清單/表格/引用）進行結構性辯論與雕塑。

#### [`writing-beats`](../.agents/skills/writing-beats/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/in-progress/writing-beats/`)
- **觸發情境**：寫作推進階段（Exploit 階段），將素材組織為節奏鮮明的冒險歷程。
- **功能描述**：在已鋪墊概念（Grounded Concepts）的約束下，每次提供 2–3 個候選節奏點（Beats）供作者選擇，步步解鎖並推進文章旅程。

#### [`git-guardrails-claude-code`](../.agents/skills/git-guardrails-claude-code/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/misc/git-guardrails-claude-code/`)
- **觸發情境**：防止 Agent 誤執行破壞性 Git 操作時。
- **功能描述**：於 `.claude/settings.json` 或全域設定中配置 PreToolUse 攔截腳本，封鎖 `git push`（含 `--force`）、`git reset --hard`、`git clean -f`、`git branch -D` 與 `git checkout .`。

#### [`setup-pre-commit`](../.agents/skills/setup-pre-commit/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/misc/setup-pre-commit/`)
- **觸發情境**：專案需要快速配置提交前品質檢查時。
- **功能描述**：自動偵測套件管理器並安裝配置 Husky、lint-staged (Prettier)、Typecheck 與 Tests 腳本。

#### [`scaffold-exercises`](../.agents/skills/scaffold-exercises/SKILL.md)

- **來源**：`mattpocock/skills` (`skills/misc/scaffold-exercises/`)
- **觸發情境**：建置課程章節或程式練習題結構時。
- **功能描述**：依照標準命名（`XX-section/XX.YY-exercise/`）自動建立 `problem/`、`solution/`、`explainer/` 子目錄與 `readme.md` 模板，並通過 linter 檢查。

#### [`doc-coauthoring`](../.agents/skills/doc-coauthoring/SKILL.md)

- **來源**：`anthropics/skills` (`skills/doc-coauthoring/`)
- **觸發情境**：撰寫文件、提案、技術規格、決策文件、PRD 或 RFC 等結構化內容時。
- **功能描述**：三階段共寫工作流：Context Gathering（補齊作者與模型的脈絡落差）→ Refinement & Structure（逐節腦力激盪、篩選、起草）→ Reader Testing（以無上下文的新對話驗證讀者能否正確解讀）。

#### [`internal-comms`](../.agents/skills/internal-comms/SKILL.md)

- **來源**：`anthropics/skills` (`skills/internal-comms/`)
- **觸發情境**：撰寫內部溝通稿，如 3P updates、公司電子報、FAQ、狀態報告、領導層更新、專案更新或事故報告時。
- **功能描述**：依溝通類型載入 `examples/` 對應指引（`3p-updates.md`、`company-newsletter.md`、`faq-answers.md`、`general-comms.md`），套用該類型之格式、語氣與資訊蒐集步驟。

---

### 類別 10：文件產製與編輯 (Document Creation & Editing)

此組技能為 Claude 文件能力之 source-available 參考實作，授權為 Anthropic proprietary（非 Apache 2.0）。

#### [`docx`](../.agents/skills/docx/SKILL.md)

- **來源**：`anthropics/skills` (`skills/docx/`)
- **觸發情境**：建立、讀取、編輯 Word 文件（`.docx`／`.dotx`），或產出含目錄、標題、頁碼、信頭的專業文件時。
- **功能描述**：新建文件以 `docx`（npm）腳本產出；既有檔案採 unzip → 編輯 `word/document.xml` → zip。支援修訂追蹤、註解、找替與影像插入；產出後以 LibreOffice 轉 PDF 做視覺核對。

#### [`pptx`](../.agents/skills/pptx/SKILL.md)

- **來源**：`anthropics/skills` (`skills/pptx/`)
- **觸發情境**：任何涉及 `.pptx`／`.potx` 的工作：建立投影片或 pitch deck、讀取／擷取文字、編輯既有簡報、合併／拆分、處理講者備註或註解。
- **功能描述**：新建 deck 以 `pptxgenjs` 腳本產出；既有檔案編輯 XML。可用 `markitdown` 讀內容，或以 thumbnail 腳本做視覺格狀預覽。

#### [`pdf`](../.agents/skills/pdf/SKILL.md)

- **來源**：`anthropics/skills` (`skills/pdf/`)
- **觸發情境**：讀取或擷取 PDF 文字／表格、合併拆分、旋轉、浮水印、填表、加解密、抽圖、掃描件 OCR，或產出新 PDF 時。
- **功能描述**：以 `pypdf`、`pdfplumber`、`reportlab` 與 `qpdf`／Poppler 等工具對應常見操作；表單填寫另見 `FORMS.md`。

#### [`xlsx`](../.agents/skills/xlsx/SKILL.md)

- **來源**：`anthropics/skills` (`skills/xlsx/`)
- **觸發情境**：試算表為主要輸入或輸出時（`.xlsx`／`.csv`／`.tsv` 之建立、編輯、公式、圖表、髒資料清理或格式轉換）。
- **功能描述**：以 `openpyxl`／`pandas` 操作；強制使用公式而非寫死結果，並以 LibreOffice 重算驗證。避開 LibreOffice 無法求值的新版 Excel 函數（如 `XLOOKUP`）。

---

### 類別 11：視覺設計與生成產出 (Visual Design & Generative Output)

#### [`canvas-design`](../.agents/skills/canvas-design/SKILL.md)

- **來源**：`anthropics/skills` (`skills/canvas-design/`)
- **觸發情境**：使用者要求海報、靜態藝術、設計或其他靜態視覺作品時。
- **功能描述**：先產出設計哲學（`.md`），再以該哲學繪製單頁 PNG／PDF。文字極少、以構圖與空間傳達；附 `canvas-fonts` 字型資源。禁止複製既有藝術家作品。

#### [`algorithmic-art`](../.agents/skills/algorithmic-art/SKILL.md)

- **來源**：`anthropics/skills` (`skills/algorithmic-art/`)
- **觸發情境**：以程式碼、生成藝術、演算法藝術、流場或粒子系統創作時。
- **功能描述**：先寫演算法哲學，再以 p5.js 實作為可互動的單一 HTML（seeded randomness、參數滑桿、種子巡覽）。禁止複製既有藝術家作品。

#### [`theme-factory`](../.agents/skills/theme-factory/SKILL.md)

- **來源**：`anthropics/skills` (`skills/theme-factory/`)
- **觸發情境**：為投影片、文件、報告或 HTML landing page 套用一致配色與字體時。
- **功能描述**：內建 10 套主題（Ocean Depths、Midnight Galaxy 等），先展示 `theme-showcase.pdf` 供選擇後套用；亦可依描述現場產生新主題。

#### [`brand-guidelines`](../.agents/skills/brand-guidelines/SKILL.md)

- **來源**：`anthropics/skills` (`skills/brand-guidelines/`)
- **觸發情境**：產出物需套用 Anthropic 官方品牌色與字體時。
- **功能描述**：套用 Anthropic 視覺識別（主色 `#141413`／`#faf9f5`、強調橘 `#d97757` 等；標題 Poppins、內文 Lora）。此為 Anthropic 品牌，非通用品牌系統。

#### [`slack-gif-creator`](../.agents/skills/slack-gif-creator/SKILL.md)

- **來源**：`anthropics/skills` (`skills/slack-gif-creator/`)
- **觸發情境**：製作給 Slack 使用的動畫 GIF（訊息或 emoji）時。
- **功能描述**：提供 Slack 尺寸／色盤／時長限制、GIFBuilder 組幀與驗證、easing 與常見動畫概念（shake、pulse、bounce 等）。Emoji 建議 128×128、訊息 480×480。

#### [`web-artifacts-builder`](../.agents/skills/web-artifacts-builder/SKILL.md)

- **來源**：`anthropics/skills` (`skills/web-artifacts-builder/`)
- **觸發情境**：製作需要狀態管理、路由或 shadcn/ui 的複雜 HTML artifact，而非單檔 HTML／JSX 時。
- **功能描述**：以腳本初始化 React + TypeScript + Vite + Tailwind + shadcn/ui 專案，開發後打包為單一 `bundle.html`。刻意避開紫漸層、Inter 等常見 AI 預設審美。

---

## 4. 相關設定與鎖定檔案

- **技能鎖定檔**：[skills-lock.json](../skills-lock.json)（記錄各技能之來源儲存庫、相對路徑與 SHA256 雜湊值）。
- **共用規範對照**：[shared/workflows/grill-me.md](../shared/workflows/grill-me.md) 與 [shared/workflows/grill-with-docs.md](../shared/workflows/grill-with-docs.md)。
- **自建技能目錄**：[custom-skills/](../custom-skills/)（與第三方技能隔離，支援模板展開）。
