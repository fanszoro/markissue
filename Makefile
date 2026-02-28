# MarkIssue Pure File-System Tracker Makefile

.PHONY: help install clean test run status logs

# Colors
GREEN := \033[0;32m
CYAN := \033[0;36m
YELLOW := \033[1;33m
RESET := \033[0m

PYTHON := python3
PIP := pip3
PORT := 8505

help: ## Show this help message
	@echo "$(CYAN)MarkIssue Tracker Makefile$(RESET)"
	@echo "$(CYAN)==========================$(RESET)"
	@echo " $(GREEN)install$(RESET) - Install Python dependencies (requires venv active or global)"
	@echo " $(GREEN)run$(RESET)     - Start the Streamlit Tracker App on port $(PORT)"
	@echo " $(GREEN)test$(RESET)    - Run the pytest suite"
	@echo " $(GREEN)clean$(RESET)   - Clean Python cache and temporary files"

install:
	@echo "$(YELLOW)Installing dependencies...$(RESET)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Done$(RESET)"

run:
	@echo "$(YELLOW)Starting MarkIssue Tracker on port $(PORT)...$(RESET)"
	streamlit run tracker_app.py --server.port $(PORT)

test:
	@echo "$(YELLOW)Running pytest suite...$(RESET)"
	PYTHONPATH=. pytest tests/ -v

clean:
	@echo "$(YELLOW)Cleaning up...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Done$(RESET)"

docker-up:
	@echo "$(YELLOW)Starting Docker containers...$(RESET)"
	docker-compose up -d

docker-down:
	@echo "$(YELLOW)Stopping Docker containers...$(RESET)"
	docker-compose down

push:
	@echo "$(YELLOW)Exporting to GitHub repo folder...$(RESET)"
	@bash scripts/export_to_github.sh
