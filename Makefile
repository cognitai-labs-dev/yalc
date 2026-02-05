.PHONY: help
help: # Show help for each of the Makefile recipes
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m: $$(echo $$l | cut -f 2- -d'#')\n"; done

TA ?= -v tests/

ruff-lint: # Run ruff linter
	uv run ruff check --fix yalc/

ruff-format: # Run ruff formatter
	uv run ruff format yalc/

mypy: # Run mypy type checker
	uv run mypy yalc/

lint: # Run pre-commit
	pre-commit run --all-files

test: # Run tests
	uv run pytest $(TA)
