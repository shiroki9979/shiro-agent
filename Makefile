.DEFAULT_GOAL := help
.PHONY: help build deploy dry-run test skills-list skills-fetch

help: ## 顯示所有可用指令與說明
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## 編譯所有 Agent 設定至 dist/ 目錄
	uv run python scripts/build.py

deploy: ## 編譯並部署所有 Agent 設定至系統全域目錄
	uv run python scripts/build.py --deploy

dry-run: ## 模擬編譯與部署流程 (Dry-run)
	uv run python scripts/build.py --dry-run

test: ## 執行單元測試套件
	uv run python -m unittest discover -s tests -p "test_*.py" -v

skills-list: ## 列出清單中所有 Skills
	uv run python scripts/fetch_skills.py --list

skills-fetch: ## 下載所有已啟用的第三方 Skills
	uv run python scripts/fetch_skills.py --all
