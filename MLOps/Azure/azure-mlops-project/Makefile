# ===== Config =====
# Set which paths to check/format. Override when calling: `make format ML_CODE=src tests`
ML_CODE ?= .

# Python tools (override if you use poetry/uv/pipx, e.g., BLACK=poetry run black)
AUTOFLAKE ?= autoflake
ISORT     ?= isort
BLACK     ?= black
FLAKE8    ?= flake8

# ===== Phony targets =====
.PHONY: format lint check ci hooks bootstrap

# 1) Auto-format (autoflake + isort + black)
format:
	$(AUTOFLAKE) --remove-all-unused-imports --remove-unused-variables --in-place -r $(ML_CODE)
	$(ISORT) $(ML_CODE) --profile black
	$(BLACK) $(ML_CODE) --line-length 79

# 2) Lint
lint:
	$(FLAKE8) $(ML_CODE)

# Run everything (format then lint)
check: format lint

# For CI systems that shouldn't modify code, lint only
ci: lint

# Install Git hooks (pre-commit + pre-push)
hooks:
	@mkdir -p .git/hooks
	@printf '%s\n' '#!/usr/bin/env bash' \
	'set -euo pipefail' \
	'ML_CODE="${ML_CODE:-.}"' \
	'AUTOFLAKE="${AUTOFLAKE:-autoflake}"' \
	'ISORT="${ISORT:-isort}"' \
	'BLACK="${BLACK:-black}"' \
	'FLAKE8="${FLAKE8:-flake8}"' \
	'echo "[pre-commit] formatting…"' \
	'$$AUTOFLAKE --remove-all-unused-imports --remove-unused-variables --in-place -r "$$ML_CODE"' \
	'$$ISORT "$$ML_CODE" --profile black' \
	'$$BLACK "$$ML_CODE" --line-length 79' \
	'git add -A' \
	'echo "[pre-commit] linting…"' \
	'$$FLAKE8 "$$ML_CODE"' \
	> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@printf '%s\n' '#!/usr/bin/env bash' \
	'set -euo pipefail' \
	'ML_CODE="${ML_CODE:-.}"' \
	'FLAKE8="${FLAKE8:-flake8}"' \
	'echo "[pre-push] linting…"' \
	'$$FLAKE8 "$$ML_CODE"' \
	> .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "✔ Git hooks installed."

# (Optional) install tools in your current Python env
bootstrap:
	pip install -U autoflake isort black flake8
