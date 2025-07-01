.PHONY: help install test clean format lint type-check demo run dev-setup all

# Default target
help:
	@echo "Smart Budget Manager - Development Commands"
	@echo "==========================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      Install the application and dependencies"
	@echo "  dev-setup    Set up development environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  test         Run all tests"
	@echo "  format       Format code with black"
	@echo "  lint         Run linting with flake8"
	@echo "  type-check   Run type checking with mypy"
	@echo "  demo         Run the demo script"
	@echo ""
	@echo "Application Commands:"
	@echo "  run          Run the CLI application"
	@echo "  ui/web       Launch the web interface"
	@echo "  reset        Reset database (delete all data)"
	@echo "  clean        Clean up build artifacts"
	@echo ""
	@echo "Combo Commands:"
	@echo "  all          Run format, lint, type-check, and test"

# Installation
install:
	@echo "🚀 Installing Smart Budget Manager..."
	@./install.sh

dev-setup:
	@echo "🔧 Setting up development environment..."
	@python3 -m venv venv
	@source venv/bin/activate && pip install --upgrade pip
	@source venv/bin/activate && pip install -r requirements.txt
	@source venv/bin/activate && pip install -e .
	@echo "✅ Development environment ready!"

# Testing
test:
	@echo "🧪 Running tests..."
	@source venv/bin/activate && pytest tests/ -v --cov=budget_manager --cov-report=term-missing

# Code quality
format:
	@echo "🎨 Formatting code..."
	@source venv/bin/activate && black budget_manager/ tests/ demo.py

lint:
	@echo "🔍 Running linter..."
	@source venv/bin/activate && flake8 budget_manager/ tests/ demo.py --max-line-length=100 --ignore=E203,W503

type-check:
	@echo "🔬 Running type checker..."
	@source venv/bin/activate && mypy budget_manager/ --ignore-missing-imports

# Demo and running
demo:
	@echo "🎬 Running demo..."
	@source venv/bin/activate && python demo.py

run:
	@echo "🏃 Running budget manager CLI..."
	@source venv/bin/activate && budget-manager --help

ui:
	@echo "🌐 Launching Web Interface..."
	@source venv/bin/activate && streamlit run app.py

web: ui

reset:
	@echo "🗑️  Resetting database..."
	@python reset_database.py

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -name ".coverage" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@rm -rf build/ dist/
	@echo "✅ Cleanup complete!"

# Development workflow
all: format lint type-check test
	@echo "✅ All checks passed!"

# Quick commands for daily development
quick-test:
	@source venv/bin/activate && pytest tests/ -v

quick-run:
	@source venv/bin/activate && python -m budget_manager

# Package building
build:
	@echo "📦 Building package..."
	@source venv/bin/activate && python setup.py sdist bdist_wheel
	@echo "✅ Package built successfully!"

# Install in development mode
install-dev:
	@echo "📦 Installing in development mode..."
	@source venv/bin/activate && pip install -e .
	@echo "✅ Development installation complete!" 