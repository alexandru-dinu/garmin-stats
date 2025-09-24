SRC := dashboard.py client.py

run-dashboard: dashboard.py
	@uv run $^

lint:
	@uv tool run ruff check $(SRC)

format:
	@uv tool run autoflake --in-place --remove-all-unused-imports $(SRC) \
		&& uv tool run isort $(SRC) \
		&& uv tool run black --line-length 100 $(SRC)