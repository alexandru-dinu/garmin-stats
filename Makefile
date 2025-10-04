SRC := $(shell ls src/*.py)

run-dashboard: src/dashboard.py
	@uv run $^

lint:
	@ruff check $(SRC)

clean:
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '.ipynb_checkpoints' -exec rm -rf {} +
	@find . -type d -name '.ruff_cache' -exec rm -rf {} +

format:
	@autoflake --in-place --remove-all-unused-imports $(SRC) \
		&& isort $(SRC) \
		&& black --line-length 100 $(SRC)
