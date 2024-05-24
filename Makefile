PYTHON = python3
SOURCES = src/main.py
TESTS = test_solver

run:
	python3 -m src.main

test:
	$(foreach test,$(TESTS),python3 -m unittest tests.$(test);)

test_verbose:
	$(foreach test,$(TESTS),python3 -m unittest tests.$(test) -v;)

conda_install:
	conda env create -f environment.yml

conda_remove:
	conda remove --name emitter --all

.PHONY: run