.PHONY: install run test benchmark presentations docker-up docker-down clean help

help:
	@echo "ChameleonShell - Active Cyber Deception Engine & Research Platform"
	@echo "Available commands:"
	@echo "  make install         Install backend Python dependencies"
	@echo "  make run             Start local FastAPI + Web SOC Server on http://localhost:8080"
	@echo "  make test            Execute pytest test suite"
	@echo "  make benchmark       Run A/B thesis benchmark evaluation against Cowrie"
	@echo "  make presentations   Generate PowerPoint (.pptx) decks for Review 1, 2, and 3"
	@echo "  make docker-up       Start containerized honey-network via docker-compose"
	@echo "  make docker-down     Stop containerized honey-network"
	@echo "  make clean           Clean cache and temporary test artifacts"

install:
	python -m pip install -r backend/requirements.txt

run:
	python -m backend.main

test:
	python -m pytest tests/ -v

benchmark:
	python -c "from backend.member3_telemetry_sandbox.benchmark_evaluator import run_benchmark_suite; print(run_benchmark_suite())"

presentations:
	python docs/presentations/generate_ppts.py

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
	python -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.pytest_cache')]"
