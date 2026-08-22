# Coding Style & Engineering Principles

## Core Principles

- 嚴格遵循 DRY, KISS, YAGNI, SOLID, Clean Code 原則。
- 只實作當前需求，不預埋未確定的擴充點。
- 優先使用語言原生 API 與標準函式庫；引入第三方套件需簡要說明必要性。
- 防禦性考量：預防 SQL Injection, XSS, Path Traversal 等安全漏洞與 N+1 Query、無窮迴圈等效能問題。

## Clean Code Guidelines

- 函式設計：短小、單一職責、參數盡量 ≤ 3。
- 命名風格：明確揭露意圖，避免混淆；通用業界縮寫（HTTP, ctx, id）除外。
- 邏輯結構：避免魔法數字；使用提早回傳（Early Return）降低巢狀層級。
- 模組解耦：透過清晰的公開介面互動。

## Documentation & Comments

- 註解語言：正體中文，重點解釋「Why」而非「What」。
- 視角：不使用第一、第二人稱。
- 程式內字串與錯誤訊息：一律使用英文。
- 文件標註：標記建立與最後更新日期。

## Error Handling

- 杜絕靜默失敗：錯誤需明確拋出或回傳可追蹤狀態，並附帶充足上下文。
- 邊界驗證：僅在系統邊界（I/O、網路、外部輸入）進行防禦性驗證。

## Testing Principles

- 採 Red -> Green -> Refactor 流程。
- 垂直切片：單一測試對應最小實作。
- 測試公開介面行為，不綁定內部實作細節。
- 命名結構清楚（Arrange / Act / Assert），聚焦關鍵路徑。
