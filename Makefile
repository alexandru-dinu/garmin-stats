SRC := $(shell ls src/*.py)

run-dashboard: src/dashboard.py
	@uv run $^

lint:
	@ruff check $(SRC)

format:
	@autoflake --in-place --remove-all-unused-imports $(SRC) \
		&& isort $(SRC) \
		&& black --line-length 100 $(SRC)
