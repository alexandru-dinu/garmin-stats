SRC := $(shell ls *.py)

run-dashboard: dashboard.py
	@uv run $^

lint:
	@ruff check $(SRC)

format:
	@autoflake --in-place --remove-all-unused-imports $(SRC) \
		&& isort $(SRC) \
		&& black --line-length 100 $(SRC)
