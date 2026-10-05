---
name: check-links
description: 檢查 Markdown 連結有效性。使用於 check-links、檢查文件死連結，或驗證文件搬移後的相對路徑；支援指定檔案或目錄，回報失敗與未驗證項目。
compatibility: 需要 Git、Node.js、npm/npx；後備指令使用 Bash、GNU grep 與 GNU xargs。首次執行需能下載 npm 套件，外部連結需網路。
---

# Markdown 連結檢查

> 建立日期：2026-10-05
> 最後更新：2026-10-05

## 執行流程

1. 確認目標儲存庫、使用者指定的範圍與專案指引。在儲存庫根目錄讀取
   Makefile、套件指令及 `.markdown-link-check.json`，確認實際檢查範圍與排除項目。
2. 優先執行既有 `check-links` 入口。若 Makefile 支援 `CHECK_LINKS_PATH`：

   ```bash
   make check-links
   make check-links CHECK_LINKS_PATH=docs
   make check-links CHECK_LINKS_PATH="docs/usage guide.md"
   ```

   依要求選擇全專案、目錄或單檔其中一種，將範例路徑換成實際範圍。
3. 缺少專案入口時，在 Bash 中執行下列後備指令。沿用來源 Makefile 的
   `markdown-link-check@3.15.0`；既有入口的版本以專案為準。

   ```bash
   set -o pipefail
   check_links_path='.'
   link_config=()
   if [ -f .markdown-link-check.json ]; then
     link_config=(--config .markdown-link-check.json)
   fi
   export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }\
   --dns-result-order=ipv4first --no-network-family-autoselection"
   git ls-files -z -- "$check_links_path" |
     { grep -zE '\.md$' || test $? -eq 1; } |
     xargs -0 -r npx --yes markdown-link-check@3.15.0 "${link_config[@]}" --
   ```

   將 `check_links_path` 設為要求的檔案或目錄。NUL 分隔與 `--` 保護含空白或
   特殊字元的檔名；`pipefail` 保留上游失敗。IPv4 選項避免部分網站因 IPv6
   連線失敗而誤報。
4. 記錄命令、退出碼與失敗的檔案／URL。區分不存在的路徑、HTTP 404、
   登入限制、429、DNS／TLS／連線錯誤；網路錯誤不直接證明文件連結錯誤。

## 範圍與判讀

- 後備指令只檢查 Git 追蹤的 `.md`。盤點要求範圍內是否有未追蹤文件；
  若要涵蓋它們，以相同 Node 選項、版本與設定，將明確檔案路徑傳給
  `markdown-link-check`，並保留 `--`。檢查不需要改動 Git index。
- 找不到符合範圍的文件時，回報「沒有符合範圍的 Markdown」，避免把空集合
  的退出碼 0 宣稱為已驗證。
- 沿用專案的 headers 與 ignorePatterns。排除項目代表未驗證；私人網域、
  DOI 與 mailto 的例外屬於個別專案，不能直接套用到其他儲存庫。
- 此工具的結果不代表已驗證所有 Markdown 標題錨點；需要時另行比對目標標題
  與渲染平台的 anchor 規則。
- 本技能執行檢查並提出修正方向。使用者要求修復時，銜接
  [fix-markdown](../fix-markdown/SKILL.md) 技能。

## 完成條件與回報

完成要求範圍的檢查，或明確記錄工具／網路阻礙。精簡回報執行命令、實際
涵蓋範圍、退出碼，以及失敗的檔案、URL、原因。列出未追蹤文件、排除項目
或其他未驗證範圍；只有實際檢查通過的範圍可標示通過。
