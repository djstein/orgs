.DEFAULT_GOAL := help

.PHONY: help
help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies
	flit install --deps develop --symlink

.PHONY: lint
lint: ## Run code linters
	black --check spice_orgs
	prospector -X spice_orgs

.PHONY: format
format: ## Run code formatters
	black --preview spice_orgs
	isort spice_orgs

.PHONY: test
test: ## Run tests
	pytest .

.PHONY: test-cov
test-cov: ## Run tests with coverage
	pytest --cov=ninja --cov-report term-missing .
