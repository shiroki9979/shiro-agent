# Workflow: Grill With Docs

## Trigger
- 使用者要求在檢驗計畫、設計或決策的同時產出文件，或使用 grill-with-docs 等觸發詞。

## Protocol
- 沿用 Grill Me 的決策推進流程。
- 決策落定後即時同步更新文件，不批次延後。

## Documentation Standards
- **CONTEXT.md**:
  - 術語一經確認即寫入 glossary。
  - 挑戰與既有定義衝突或模糊用語，以具體情境進行壓力測試。
  - 僅記錄領域語言，不包含實作細節。
- **ADR (Architecture Decision Records)**:
  - 僅在三者皆成立時提議建立：
    1. 難以逆轉。
    2. 無脈絡下令人意外。
    3. 源自真實取捨。
