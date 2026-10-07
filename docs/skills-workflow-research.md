# Skills 工程工作流來源查證

> 建立日期：2026-10-07
> 最後更新：2026-10-07
> 查證範圍：指定文章及其 References；以作者維護的 README、SKILL.md、CHANGELOG 和本機鎖定技能交叉核對。

## 結論與版本邊界

[指定文章][article] 適合作為導覽；正式採用流程時，應回到所安裝版本的技能及本專案規範。技巧如何落實為自建技能，另見 [Skill 撰寫指南](skill-authoring-guide.md)。

本次於 2026-10-07 讀取上游 `main`；其 [package.json][package] 顯示 `1.3.1`。這是查閱時的分支快照，未取得整體 commit SHA，不宣稱全部檔案同屬不可變版本。本機依 [skills-lock.json](../skills-lock.json) 的來源、路徑與內容雜湊識別，不能由該檔推定整包的 release 版本。上游與本機的差異需逐項處理，不能以重新安裝取代查證。

## 原文參考資料核對

| 查核項目 | 第一手結果與採用邊界 |
| :--- | :--- |
| 官方定位與安裝 | [README][readme] 強調小而可組合的技能，列出需求對齊、共享語言、回饋迴圈與架構四類問題。CLI 安裝由 [skills.sh 套件頁][directory] 交叉確認；安裝量和星數不能作為效能或品質證據。 |
| setup 是否必要 | [setup][setup] 明確要求其他工程技能首次使用前設定 issue tracker、triage labels、domain docs；沒有安裝 triage 時略過標籤。這是該套工程流程的前置配置，不是所有 Agent Skills 的格式要求。既有配置可直接維護，無須每次重跑。 |
| 除錯技能名稱 | 現行 [SKILL.md][diagnose] 的正式名稱為 `diagnosing-bugs`，`diagnose` 是 description 中的觸發字；本 repo 的鎖定名稱亦為 `diagnosing-bugs`。文章 References 的連結已指向現行路徑。此結果只確認現況，不推定歷史上從未存在舊名稱。 |
| TDD 的循環 | [上游 tdd][tdd] 與[本機 tdd](../.agents/skills/tdd/SKILL.md) 均要求一個測試、一個最小實作，經公開介面驗證；目前將重構放在 review 階段。README 仍以 red-green-refactor 概括，來源內存在粒度差異。本 repo 的 [AGENTS.md](../AGENTS.md) 明定 Red → Green → Refactor，研究不覆寫它。 |
| 訪談與文件 | [grill-with-docs][grill] 僅組合 `grilling` 與 `domain-modeling`，以共享能力完成工作，無須在 wrapper 複製兩套流程。 |
| 架構改善 | [架構技能][architecture] 先依指定範圍或近期變更熱點探索，再交付候選方案 HTML 報告，待選定方案後討論；不是掃描後直接全面重構。README 建議每隔幾天使用，但這是作者建議頻率，非執行門檻。 |
| skills.sh | [套件頁][directory] 可驗證安裝入口與當時清單；頁面是動態索引，不足以證明某篇舊文當時的技能集合。 |
| v1.1 影片 | 已追到 [YouTube 原始連結][video]，但工具無法取得影片或逐字稿，故未驗證影片內的口述、歷史命名與流程細節。 |

未能證實的主張：[文章][article] 所載歷史星數／Fork 數缺少當日 API 快照；「每完成 3–5 個 issue」的歸因在已讀第一手資料中未找到。標示為未驗證，不據此判定歷史敘述錯誤，也不納入本 repo 的固定規範。

## 可採用的流程技巧

以下按第一手文件獨立整理，不把導覽文章的排列當成每個任務必跑的流水線。

1. **以決策分支路由。** [ask-matt][router] 在訪談後先判斷是否需要可執行原型，再判斷是否跨 session：小任務直接 `implement`，較大任務才 `to-spec` → `to-tickets` → 實作。除錯、triage、wayfinder 是不同入口；研究結果提供後續決策所需證據。
2. **把完成條件寫成可觀察證據。** [diagnosing-bugs][diagnose] 要求先有實際跑過、能針對原症狀失敗的回饋命令，再縮小重現、提出可證偽假設並觀測；完成時還要重跑原情境及清除暫時工具。可借用這種「先證據、後下一階段」的設計，不必照搬除錯的全部步驟。
3. **用行為回饋控制批次大小。** [tdd][tdd] 的核心是一條公開介面上的可驗證行為；預期值來自規格或已知範例，不能複製實作公式作為斷言。這能把技能的驗收標準連回真實用途。
4. **把可重用能力和編排分開。** [grill-with-docs][grill] 是薄編排層；[架構技能][architecture] 重用 `codebase-design` 和 `domain-modeling`，只保留自身的探索、交付、選擇流程。共用詞彙和原則各保留一個維護點。
5. **把工作設定當作輸入契約。** [setup][setup] 將 tracker、標籤和文件位置放入 `docs/agents/`，入口文件僅保留指向它們的摘要。後續技能沿用既有設定，避免自行猜測或各存一份。

## 對本 repo 的整併方式

| 項目 | 處理方式與理由 |
| :--- | :--- |
| 專案初始化 | 已有 [issue tracker](agents/issue-tracker.md)、[triage labels](agents/triage-labels.md)、[domain docs](agents/domain.md) 與 AGENTS 入口，這次研究無須重新執行 setup。 |
| 領域詞彙檔 | 上游 [1.3.0 變更紀錄][changes] 將 `CONTEXT.md` 改稱 `GLOSSARY.md`；本機部分技能也已使用新名，但本 repo 的 [AGENTS.md](../AGENTS.md)、[CONTEXT.md](../CONTEXT.md) 和 domain 設定仍指定舊名。依本專案明示規範讀取 `CONTEXT.md`；若另行遷移，須同步入口與引用，本次不改名。 |
| 寫作準則 | 與既有 [writing-for-agents](../.agents/skills/writing-for-agents/SKILL.md) 和 [skill-creator](../.agents/skills/skill-creator/SKILL.md) 對照，提煉本 repo 的實務指南，不改寫第三方技能或增加同名技能。 |
| 路徑與平台差異 | 沿用 [探索路徑研究](agent-skill-paths-research.md)；斜線指令是示意，不代表每個 Target Agent 的呼叫介面相同。上游 [1.2.0／1.3.0 變更紀錄][changes] 也區分 Codex metadata 與 Claude frontmatter，並修正跨技能呼叫。 |

## 來源與查閱紀錄

所有來源查閱日期均為 2026-10-07。GitHub `main` 連結可能隨後更新；下列網址中的追蹤參數已移除。影片僅解析出網址，未列為已讀證據。

- [AI 郵報指定文章][article]：研究起點，非官方規範來源。
- [mattpocock/skills README][readme]、[package.json][package]、[CHANGELOG][changes]：定位、版本與演進背景。
- [setup-matt-pocock-skills][setup]、[diagnosing-bugs][diagnose]、[tdd][tdd]、[grill-with-docs][grill]、[improve-codebase-architecture][architecture]：文章所列技能的一手規範。
- [ask-matt][router]：補查官方流程路由。
- [skills.sh 套件頁][directory]：安裝入口。
- [Matt Pocock v1.1 影片][video]：未取得內容。

[article]: https://www.aiposthub.com/mattpocock-skills-complete-guide-ai-engineering-workflow/
[readme]: https://github.com/mattpocock/skills/blob/main/README.md
[package]: https://github.com/mattpocock/skills/blob/main/package.json
[changes]: https://github.com/mattpocock/skills/blob/main/CHANGELOG.md
[setup]: https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md
[diagnose]: https://github.com/mattpocock/skills/blob/main/skills/engineering/diagnosing-bugs/SKILL.md
[tdd]: https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md
[grill]: https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md
[architecture]: https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md
[router]: https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md
[directory]: https://www.skills.sh/mattpocock/skills
[video]: https://www.youtube.com/watch?v=A8mokin_YOs
