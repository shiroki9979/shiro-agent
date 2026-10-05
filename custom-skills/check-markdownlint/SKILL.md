---
name: check-markdownlint
description: 檢查 Markdown 格式與 markdownlint 規則。使用於 check-markdownlint、Markdown lint、文件排版檢查或 Markdown CI 失敗診斷；沿用專案規則並回報檔案、行號與規則代碼。
compatibility: 需要 Node.js 22 以上與 npm/npx。首次執行需能下載 npm 套件；既有 Makefile 入口另需 make。
---

# Markdown 格式檢查

> 建立日期：2026-10-05
> 最後更新：2026-10-05

## 執行流程

1. 確認目標專案、要求範圍與專案指引。在專案根目錄讀取 Makefile、套件指令、
   `.markdownlint-cli2.*` 與 `.markdownlint.*` 設定，確認 globs、ignores、
   gitignore、規則及是否啟用自動修復。選擇只檢查的入口；若既有設定強制寫入，
   先回報該限制，避免檢查造成文件變更。
2. 全專案檢查優先使用既有入口：

   ```bash
   make check-markdownlint
   ```

   沿用專案指定的版本與設定。若只有等效套件指令，使用該入口。
3. 缺少入口時，沿用來源 Makefile 的固定版本。在有設定 globs 的
   `.markdownlint-cli2.*` 專案執行：

   ```bash
   npx --yes markdownlint-cli2@0.23.3
   ```

   若專案未定義掃描 globs，明確傳入範圍；單檔或目錄檢查使用
   `--no-globs`，避免設定中的全專案 globs 擴大範圍：

   ```bash
   npx --yes markdownlint-cli2@0.23.3 --no-globs "docs/**/*.md" "#node_modules/**"
   npx --yes markdownlint-cli2@0.23.3 --no-globs ":docs/usage guide.md"
   ```

   選擇符合要求的一個命令並換成實際路徑。引號保留 glob；`:` 指定字面檔名。
4. 沒有 `.markdownlint-cli2.*` 設定、且需要來源 Makefile 的全專案預設時，
   將 `<skill-dir>` 換成此技能所在的絕對路徑，使用隨附的基礎設定：

   ```bash
   npx --yes markdownlint-cli2@0.23.3 --config "<skill-dir>/assets/default.markdownlint-cli2.yaml"
   ```

   基礎設定掃描 `**/*.md`、遵循 `.gitignore`、排除 `node_modules/**`。
   專案已有 CLI2 設定時以該設定為準；Git 追蹤與否不決定此工具的掃描範圍。
5. 記錄命令、退出碼、實際掃描檔案數，以及每個問題的路徑、行號、MD 規則代碼
   與訊息。區分 lint 違規、設定錯誤與套件下載／執行失敗。

## 完成條件與回報

完成要求範圍的檢查，或明確記錄執行阻礙。回報命令、設定來源、掃描範圍與
結果；掃描檔案數為 0 時回報未檢查到文件。僅檢查時保留文件與規則設定；
使用者要求修復時，銜接 [fix-markdown](../fix-markdown/SKILL.md) 技能處理並以相同範圍重跑。
