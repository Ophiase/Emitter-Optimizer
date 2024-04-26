
PYTHON = python3
SOURCES = src/main.py
TESTS = test_solver

run:
	python3 src/main.py

test:
	$(foreach test,$(TESTS),python3 -m unittest tests.$(test);)

test_verbose:
	$(foreach test,$(TESTS),python3 -m unittest tests.$(test) -v;)

.PHONY: run