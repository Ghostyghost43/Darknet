.PHONY: help install install-dev clean test lint format run console

help:
	@echo "Darknet - Wireless Security Framework"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install the package"
	@echo "  make install-dev  - Install with development dependencies"
	@echo "  make clean        - Remove build artifacts and cache"
	@echo "  make test         - Run test suite"
	@echo "  make lint         - Run linters (flake8, pylint)"
	@echo "  make format       - Format code with black"
	@echo "  make run          - Run Darknet CLI"
	@echo "  make console      - Start interactive console"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,web]"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

test:
	pytest tests/ -v --cov=darknet --cov-report=html

lint:
	flake8 darknet/ --count --select=E9,F63,F7,F82 --show-source --statistics
	pylint darknet/ --exit-zero

format:
	black darknet/ tests/

run:
	python -m darknet.cli

console:
	python -m darknet.console
