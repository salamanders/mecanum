install:
	uv sync

run:
	uv run python3 app.py

test:
	uv run python3 wiring_check.py

lint:
	uv run ruff check .
	uv run ruff format .