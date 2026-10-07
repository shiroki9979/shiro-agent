---
name: extract-till-you-drop
description: 遵循 Uncle Bob 的 Extract Till You Drop 原則，落實單一抽象層級（SLAP）與下樓梯法則（Stepdown Rule）。適用於重構長函式、拆解控制流區塊、優化函式閱讀順序，或在 Code Review 時檢驗函式顆粒度。
---

# Extract Till You Drop

> 建立日期：2026-08-23
> 最後更新：2026-10-07

本技能遵循 Uncle Bob (Robert C. Martin) 的 **Extract Till You Drop** 哲學，結合**單一抽象層級原則（SLAP）**與**下樓梯法則（Stepdown Rule）**，提供可操作的長函式重構流程與審查清單。

---

## 核心原則

1. **只做一件事（Do One Thing）**：函式應只做一件事、做好這件事、只做這件事。若函式可再切分出不同抽象層級的步驟，即代表它做了多件事。
2. **單一抽象層級原則（Single Level of Abstraction Principle, SLAP）**：函式內的每一行陳述句，必須處於同一個抽象層級。高層協調邏輯絕不可與底層實作細節（如字串拼接、位元運算、原始資料解析）混雜在同一個函式中。
3. **下樓梯法則（Stepdown Rule）**：程式碼應像文章敘事一樣由上而下閱讀。主呼叫函式置於最上方，被呼叫的子函式緊排於其下方，每向下讀一層，抽象層級便下降一階。

---

## 四步重構 SOP（4-Step Extraction SOP）

當重構長函式或複合邏輯時，依序執行以下四步驟：

### 步驟 1：劃分抽象層級（Identify Levels）

- 閱讀目標函式，識別**高階業務流程（High-level Narrative）**與**低階操作細節（Low-level Details）**。
- 將高階主流程標示為頂層主幹，其餘分支細節列為待提取候選。

### 步驟 2：提取意圖函式（Extract Intention-Revealing Functions）

- **控制流單一化**：優先將跨抽象層級的 `if` / `else` 與迴圈區塊提取為具名函式；每次提取前檢查防禦煞車條件。同層次的 guard clause 或緊密原子操作可保留，避免無意義拆分。
- **揭露意圖**：以領域語意命名提取出的函式（說明 *What* 或 *Why*），隱藏 *How*。
- **維持 SLAP**：確保主函式維持同層次的協調邏輯；因煞車條件保留的區塊，指出具體原因與尚存的層級混雜。

### 步驟 3：下樓梯編排（Arrange in Stepdown Order）

- 調整檔案內的函式定義順序：
  - 頂層公開介面／主流程函式置於最前。
  - 第一層輔助函式緊隨其後。
  - 更底層的工具函式置於最後。
- 閱讀者只需由上往下閱讀即可掌握完整脈絡，無需上下跳躍搜尋。

### 步驟 4：煞車檢核與測試驗證（Check Stopping Criteria & Verify）

- 對照**防禦煞車條件**，確認未發生過度提取。
- 執行既有單元測試（或在重構前先建立測試防護網），確保行為完全一致。

---

## 三大防禦煞車條件（Stopping Criteria）

「持續提取直到無法再提取為止」的前提是**不破壞工程可維護性**。候選區塊一旦觸發以下任一條件，停止該項提取並保留區塊；其他候選仍可分別評估：

1. **參數膨脹（Parameter Bloating）**
   - 提取出的子函式需要傳遞 > 3 個參數，或被迫建立不自然的臨時資料結構以傳遞狀態。
2. **語意冗餘（Vacuous / Meaningless Naming）**
   - 無法為子函式命名出具備實質領域語意的名稱（例如只能叫 `processPart1()`、`doConditionTrue()`、`helperFunc()`）。
3. **內聚碎裂（Cohesion Loss）**
   - 2~3 行緊密綁定的原生計算或轉換，提取後反而打碎原子操作，顯著增加上下文理解負擔。

---

## 審查檢查清單（Code Review Checklist）

在撰寫新程式碼或進行 Code Review 時，對照以下項目進行驗收：

| 檢核項目 | 合格標準 |
| :--- | :--- |
| **SLAP 一致性** | 函式維持單一抽象層級；因煞車條件保留的混雜已明列為限制 |
| **控制流區塊** | 跨抽象層級的控制流已提取，或有具體煞車理由；同層次的 guard clause 與原子操作可保留 |
| **Stepdown 順序** | 函式垂直排列符合由上而下閱讀敘事，呼叫者在上、被呼叫者在下 |
| **參數精簡** | 函式參數數量 ≤ 3，無 Tramp Data 傳遞 |
| **命名清晰** | 函式名稱明確揭露業務意圖，無需註解解釋其行為 |
| **未過度提取** | 每次提取均通過煞車檢核；遇停止條件時保留區塊並說明原因，保持模組高內聚 |

---

## 範例示範

### 重構前（Before：混雜抽象層級、巢狀與底層細節）

```python
def process_user_registration(request_data: dict) -> dict:
    # 驗證輸入（低階細節）
    if not request_data.get("email") or "@" not in request_data["email"]:
        raise ValueError("Invalid email address")
    if not request_data.get("password") or len(request_data["password"]) < 8:
        raise ValueError("Password must be at least 8 characters")

    # 密碼雜湊（低階機制）
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac("sha256", request_data["password"].encode(), salt, 100000)

    # 儲存使用者（中階操作）
    user = db.users.insert({
        "email": request_data["email"].lower().strip(),
        "password_hash": hashed_password.hex(),
        "salt": salt.hex(),
        "status": "pending_verification"
    })

    # 發送通知信（底層網路與字串組裝）
    token = jwt.encode({"user_id": user["id"]}, SECRET_KEY, algorithm="HS256")
    url = f"https://example.com/verify?token={token}"
    mail_client.send(to=user["email"], subject="Verify Email", body=f"Click here: {url}")

    return {"status": "success", "user_id": user["id"]}
```

### 重構後（After：SLAP、下樓梯排列、意圖揭露）

```python
def process_user_registration(request_data: dict) -> dict:
    validate_registration_payload(request_data)
    user = create_pending_user(request_data)
    send_verification_email(user)
    return build_registration_response(user)


def validate_registration_payload(payload: dict) -> None:
    if not is_valid_email(payload.get("email", "")):
        raise ValueError("Invalid email address")
    if not is_valid_password(payload.get("password", "")):
        raise ValueError("Password must be at least 8 characters")


def is_valid_email(email: str) -> bool:
    return bool(email and "@" in email)


def is_valid_password(password: str) -> bool:
    return bool(password and len(password) >= 8)


def create_pending_user(payload: dict) -> dict:
    password_hash, salt = hash_password(payload["password"])
    return db.users.insert({
        "email": payload["email"].lower().strip(),
        "password_hash": password_hash,
        "salt": salt,
        "status": "pending_verification"
    })


def hash_password(password: str) -> tuple[str, str]:
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return hashed.hex(), salt.hex()


def send_verification_email(user: dict) -> None:
    verification_url = generate_verification_url(user["id"])
    mail_client.send(
        to=user["email"],
        subject="Verify Email",
        body=f"Click here: {verification_url}"
    )


def generate_verification_url(user_id: str) -> str:
    token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm="HS256")
    return f"https://example.com/verify?token={token}"


def build_registration_response(user: dict) -> dict:
    return {"status": "success", "user_id": user["id"]}
```
