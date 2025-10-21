CIAF_ROOT := $(shell pwd)
PYTHON := python3
PIP := pip3

# Colors for output
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

.PHONY: help install test demo-healthcare demo-banking demo-government demo-all verify-receipts benchmarks clean

help: ## Show this help message
	@echo "$(GREEN)CIAF Make Commands$(NC)"
	@echo "=================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install CIAF and dependencies
	@echo "$(GREEN)Installing CIAF framework...$(NC)"
	$(PIP) install -e .
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ CIAF installation complete$(NC)"

test: ## Run comprehensive test suite
	@echo "$(GREEN)Running CIAF test suite...$(NC)"
	python -m pytest tests/ -v --tb=short
	python scripts/validate_frameworks.py
	python scripts/validate_regulatory_mappings.py
	@echo "$(GREEN)✅ All tests passed$(NC)"

demo-healthcare: ## Run Healthcare SaMD compliance demo
	@echo "$(GREEN)🏥 Running Healthcare SaMD Demo...$(NC)"
	@echo "Demonstrates FDA 21 CFR 820 compliance with ISO 14971 risk management"
	python examples/golden_paths/healthcare_samd_demo.py
	@echo "$(GREEN)✅ Healthcare demo complete - Evidence generated$(NC)"

demo-banking: ## Run Banking SR 11-7 compliance demo  
	@echo "$(GREEN)🏦 Running Banking SR 11-7 Demo...$(NC)"
	@echo "Demonstrates Federal Reserve Model Risk Management compliance"
	python examples/golden_paths/banking_sr11_7_demo.py
	@echo "$(GREEN)✅ Banking demo complete - Evidence generated$(NC)"

demo-government: ## Run Government OMB M-24-10 transparency demo
	@echo "$(GREEN)🏛️ Running Government OMB M-24-10 Demo...$(NC)"
	@echo "Demonstrates FOIA-ready AI transparency with Chief AI Officer compliance"
	python examples/golden_paths/government_omb_m24_10_demo.py
	@echo "$(GREEN)✅ Government demo complete - Evidence generated$(NC)"

demo-all: demo-healthcare demo-banking demo-government ## Run all golden path demos
	@echo "$(GREEN)🎯 All golden path demonstrations complete!$(NC)"
	@echo "Evidence packages available for investor/buyer review"

verify-receipts: ## Verify cryptographic receipts
	@echo "$(GREEN)🔒 Verifying cryptographic receipts...$(NC)"
	python scripts/ciaf-verify examples/receipts/ --full-audit
	@echo "$(GREEN)✅ Receipt verification complete$(NC)"

benchmarks: ## Run ROI benchmarking analysis
	@echo "$(GREEN)📊 Running ROI benchmarking analysis...$(NC)"
	cd benchmarks/audit-time && python ciaf_roi_analysis.py
	@echo "$(GREEN)✅ Benchmarking analysis complete$(NC)"

serve-docs: ## Serve documentation locally
	@echo "$(GREEN)📚 Starting documentation server...$(NC)"
	@echo "Opening CIAF documentation at http://localhost:8000"
	cd Docs && python -m http.server 8000

quality-check: ## Run comprehensive quality checks
	@echo "$(GREEN)🔍 Running quality checks...$(NC)"
	mypy ciaf/ --ignore-missing-imports
	bandit -r ciaf/ -f json -o security-report.json
	python -m pytest --cov=ciaf --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Quality checks complete$(NC)"

investor-package: benchmarks verify-receipts demo-all ## Generate complete investor package
	@echo "$(GREEN)📦 Generating investor due diligence package...$(NC)"
	mkdir -p investor_package
	cp README.md investor_package/
	cp docs/compliance_cross_walk.csv investor_package/
	cp benchmarks/audit-time/ciaf_roi_analysis_data.json investor_package/
	cp -r examples/receipts investor_package/ 2>/dev/null || echo "Receipt examples will be generated during demos"
	@echo "$(GREEN)✅ Investor package ready in ./investor_package/$(NC)"

production-deploy: quality-check test ## Validate production readiness
	@echo "$(GREEN)🚀 Validating production deployment readiness...$(NC)"
	python scripts/validate_frameworks.py
	python scripts/validate_regulatory_mappings.py
	python examples/golden_paths/test_golden_paths.py
	@echo "$(GREEN)✅ Production deployment validated$(NC)"

clean: ## Clean build artifacts and temp files
	@echo "$(YELLOW)🧹 Cleaning build artifacts...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/
	rm -f security-report.json validation_report.json framework_validation_report.json
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

# Quick start for new users
quickstart: install demo-healthcare verify-receipts ## Quick start: install, demo, verify
	@echo "$(GREEN)🎯 CIAF Quick Start Complete!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  • Run 'make demo-all' to see all industry demonstrations"
	@echo "  • Run 'make benchmarks' to see ROI analysis"  
	@echo "  • Run 'make investor-package' to generate due diligence materials"
	@echo "  • Visit http://localhost:8000 for full documentation (make serve-docs)"

# Development helpers
lint: ## Run code linting
	@echo "$(GREEN)🔍 Running code linting...$(NC)"
	flake8 ciaf/ --max-line-length=100
	black ciaf/ --check
	isort ciaf/ --check-only

format: ## Auto-format code
	@echo "$(GREEN)🎨 Formatting code...$(NC)"
	black ciaf/
	isort ciaf/

# Performance testing
perf-test: ## Run performance benchmarks
	@echo "$(GREEN)⚡ Running performance tests...$(NC)"
	python tests/performance/receipt_generation_benchmark.py
	python tests/performance/policy_enforcement_benchmark.py

# Security scanning
security-scan: ## Run comprehensive security scan
	@echo "$(GREEN)🛡️ Running security scan...$(NC)"
	bandit -r ciaf/ -f text
	safety check
	
# Docker helpers (if containerizing)
docker-build: ## Build Docker image
	@echo "$(GREEN)🐳 Building Docker image...$(NC)"
	docker build -t ciaf:latest .

docker-demo: ## Run demos in Docker container
	@echo "$(GREEN)🐳 Running demos in Docker...$(NC)"
	docker run -it --rm ciaf:latest make demo-all