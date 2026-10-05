.DEFAULT_GOAL := help
.PHONY: help build deploy dry-run test skills-list skills-add skills-update release

help: ## 顯示所有可用指令與說明
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## 清理目標舊產物並編譯所有 Agent 設定至 dist/ 目錄
	uv run python scripts/build.py

deploy: ## 編譯、部署至全域目錄並清理已失去來源的受管檔案
	uv run python scripts/build.py --deploy

dry-run: ## 編譯並預覽全域部署、備份與清理操作 (Dry-run)
	uv run python scripts/build.py --dry-run

test: ## 執行單元測試套件
	uv run python -m unittest discover -s tests -p "test_*.py" -v

skills-list: ## 列出已安裝之 Agent Skills
	npx skills list

skills-add: ## 新增 Agent Skill (使用方式: make skills-add PKG=<source>)
	@if [ -z "$(PKG)" ]; then echo "錯誤：請指定 PKG 參數，例如 make skills-add PKG=mattpocock/skills"; exit 1; fi
	npx skills add $(PKG)

skills-update: ## 更新所有已安裝之 Agent Skills
	npx skills update

release: test ## 發布新版本並建立 Git Tag (使用方式: make release TAG=v0.1.0)
	@if [ -z "$(TAG)" ]; then echo "錯誤：請指定 TAG 參數，例如 make release TAG=v0.1.0"; exit 1; fi
	git tag -a $(TAG) -m "Release $(TAG)"
	@echo "已建立標籤: $(TAG)。推送指令: git push origin $(TAG)"
