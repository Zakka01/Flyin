PYTHON = python3
MAIN = fly_in.py
CONFIG = config.txt

install:
	python3 -m venv v

run :
	@$(PYTHON) $(MAIN) --no-render $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
