# Coding Style & Engineering Principles

## Core Principles

- 遵循 **DRY、KISS、YAGNI、SOLID、Clean Code**；只實作當前需求，不預埋未確定的擴充點。
- 優先使用語言原生 API 與標準函式庫；引入第三方套件需簡要說明必要性。
- 防禦性考量：預防常見安全漏洞（SQL Injection、XSS、路徑穿越）及效能陷阱（N+1 Query、無限迴圈）。

## Clean Code Guidelines

- 函式設計：短小、參數少（理想 ≤ 3）；命名揭露意圖，業界通用縮寫（HTTP、ctx、id 等）除外。
- 邏輯結構：避免魔法數字；以早回傳（Early Return）降低巢狀；複雜邏輯拆成可獨立理解的小單元。
- 模組解耦：模組間透過清晰介面互動，降低耦合。

## Documentation & Comments

- 註解語言：註解以正體中文撰寫，說明 Why 而非 What；若需大量註解解釋程式碼，優先重構。
- 視角與用詞：不使用第一、第二人稱；程式內字串、錯誤訊息一律使用英文。
- 文件標註：文件標注建立／最後更新日期。

## Error Handling

- 杜絕靜默失敗：不允許靜默失敗；錯誤需明確拋出或回傳可追蹤狀態，附帶充足上下文。
- 邊界驗證：僅在系統邊界（I/O、網路、使用者輸入）做防禦性驗證。

## Testing Principles

- 核心邏輯須附單元測試，採 **Red → Green → Refactor** 流程：垂直切片（一測試 → 一最小實作）。
- 介面隔離：測試公開介面（seam）行為，不綁定內部實作細節。
- 斷言與邊界：預期值來自規格或已知範例，避免同構斷言；聚焦關鍵路徑，不窮舉邊界。
- 結構與環境：測試命名描述情境，遵循 Arrange / Act / Assert；外部相依以 mock / stub 隔離，整合測試用真實 fixture 或 snapshot。
