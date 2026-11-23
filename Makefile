PY ?= .venv/bin/python

.PHONY: setup test outputs check all

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

test:
	$(PY) -m pytest

outputs:
	$(PY) code/estimates.py
	$(PY) code/build_workbook.py
	$(PY) code/backtest.py > output/backtest.txt

check:
	$(PY) code/check.py

all: test outputs check
