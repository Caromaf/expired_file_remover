# タスクランナーのためのMakefile

# デフォルトシェルを指定
SHELL := /bin/bash

# グローバルな変数
PACKAGE_NAME := expired_file_remover
SRC_DIR := src/$(PACKAGE_NAME)
TEST_DIR := tests
DOCS_DIR := docs

.PHONY: help
help:
	@echo "利用可能なコマンド:"
	@echo "  make install           依存関係をインストールする"
	@echo "  make test              テストを実行する"
	@echo "  make coverage          テストカバレッジレポートを生成する"
	@echo "  make format            コードをフォーマットする（isort, black）"
	@echo "  make lint              コードをチェックする（flake8, mypy）"
	@echo "  make docs              ドキュメントをビルドする"
	@echo "  make clean             生成されたファイルをクリーンアップする"
	@echo "  make build             パッケージをビルドする"
	@echo "  make all               すべてのチェックとテストを行う"

.PHONY: install
install:
	poetry install

.PHONY: test
test:
	poetry run pytest

.PHONY: coverage
coverage:
	poetry run pytest --cov=$(SRC_DIR) --cov-report=html

.PHONY: format
format:
	poetry run isort $(SRC_DIR) $(TEST_DIR)
	poetry run black $(SRC_DIR) $(TEST_DIR)

.PHONY: lint
lint:
	poetry run flake8 $(SRC_DIR) $(TEST_DIR)
	PYTHONPATH=src poetry run mypy $(SRC_DIR)
	PYTHONPATH=. poetry run mypy $(TEST_DIR)

.PHONY: docs
docs:
	@if [ ! -d "$(DOCS_DIR)/node_modules" ]; then \
		echo "Installing Docusaurus dependencies..." && \
		cd $(DOCS_DIR) && npm install; \
	fi
	@echo "Building documentation..."
	cd $(DOCS_DIR) && npm run build
	@echo "Documentation built successfully in $(DOCS_DIR)/build/"

.PHONY: docs-dev
docs-dev:
	@if [ ! -d "$(DOCS_DIR)/node_modules" ]; then \
		echo "Installing Docusaurus dependencies..." && \
		cd $(DOCS_DIR) && npm install; \
	fi
	@echo "Starting documentation development server..."
	@echo "Access the documentation at http://localhost:3000"
	cd $(DOCS_DIR) && npm run start

.PHONY: docs-serve
docs-serve:
	@if [ ! -d "$(DOCS_DIR)/build" ]; then \
		echo "Documentation not built. Building..." && \
		make docs; \
	fi
	@echo "Serving documentation at http://localhost:3000"
	cd $(DOCS_DIR) && npm run serve

.PHONY: clean
clean:
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf $(DOCS_DIR)/build/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: build
build:
	poetry build

.PHONY: all
all: format lint test build
