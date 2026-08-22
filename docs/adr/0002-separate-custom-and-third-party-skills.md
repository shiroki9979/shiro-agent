# 分離自建技能與第三方依賴目錄並於編譯時聚合

我們決定將自有撰寫的技能存放於 `custom-skills/` 目錄，而第三方技能則維持在 `.agents/skills/` 由 Agent Skills CLI 與 `skills-lock.json` 管理。雖然全部放在 `.agents/skills/` 保持單一目錄，但目錄分離能在原始碼層級實現物理隔離，避免自建技能被 CLI 工具意外覆寫；`build.py` 在編譯與部署時會聚合兩處技能輸出至 `dist/` 與全域環境，並在發生名稱衝突時嚴格中斷報錯。
