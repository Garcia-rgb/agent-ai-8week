.PHONY: install install-semantic run test lint doctor version build ingest docker-up

install:
	python -m pip install -e ".[dev]"

# 需要在本地跑语义向量时用这个（会把 onnxruntime 与 tokenizers 一起装上）。
install-semantic:
	python -m pip install -e ".[semantic,dev]"

run:
	uvicorn support_agent.main:app --reload

test:
	pytest -q

lint:
	ruff check --no-cache .

# 环境自检：配置、数据库与语料规模、向量后端、模型、缓存与限流逐项报告。
doctor:
	python -m support_agent doctor

version:
	python -m support_agent version

build:
	python -m build

# 把本地资料目录导入当前 DATABASE_URL 指向的知识库，用法：make ingest SOURCE="D:\资料汇总"
ingest:
	python scripts/ingest_smartpv.py --source "$(SOURCE)"

docker-up:
	docker compose up --build
