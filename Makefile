#
DEFAULT: help
.DEFAULT: help

VENV_DIR = venv
TESTS_DIR = tests
SETUP_PY = setup.py
BIN_DIR = $(VENV_DIR)/bin
PYTHON_CMD = $(BIN_DIR)/python3
PIP_CMD = $(BIN_DIR)/pip3
#
PYTEST_CMD = $(BIN_DIR)/pytest
PYTEST_ARGS =
PYTEST_ARGS_MANUAL = --log-level debug --capture=no -x --pdb
FLAKE8_CMD = $(BIN_DIR)/flake8
FLAKE8_ARGS =
ISORT_CMD = $(BIN_DIR)/isort
ISORT_ARGS = --check-only
PUR_CMD = $(BIN_DIR)/pur
#
# SYS_PYTHON_CMD = $(shell which python3)
# Force the "oldest supported version".
# TODO don't hard-code the python path.
SYS_PYTHON_CMD = /opt/homebrew/bin/python3.11

ifeq ("$(DISABLE_VIRTUAL_ENV)", "true")
$(warning "Resetting commands for CI.")
PIP_CMD = pip3
PYTHON_CMD = python3
PYTEST_CMD = pytest
FLAKE8_CMD = flake8
ISORT_CMD = isort
endif

# To install venv on ubuntu 14.04:
#	sudo apt-get install python3-venv
_local_virtualenv:
	$(SYS_PYTHON_CMD) -m venv $(VENV_DIR)

_pip_reqs:
	$(PIP_CMD) install --upgrade pip
	$(PIP_CMD) install --progress-bar off --upgrade setuptools
	$(PIP_CMD) install --progress-bar off --upgrade pur
	$(PIP_CMD) install --progress-bar off -r tests/requirements.txt
	$(PIP_CMD) install --progress-bar off -r requirements.txt

_dev_reqs:
	$(PIP_CMD) install --progress-bar off -r dev_requirements.txt

_setup_develop:
	$(PYTHON_CMD) $(SETUP_PY) develop

ci-dev: _pip_reqs _setup_develop

dev: _local_virtualenv ci-dev _dev_reqs

run:
	PYTHONBREAKPOINT=ipdb.set_trace $(BIN_DIR)/pybanker --log-level debug

update-reqs:
	$(PUR_CMD) --requirement requirements.txt
	$(PUR_CMD) --requirement tests/requirements.txt
	$(PUR_CMD) --requirement dev_requirements.txt

info:
	@echo "VENV_DIR = $(VENV_DIR)"
	@echo "SYS_PYTHON_CMD = $(SYS_PYTHON_CMD)"
	@echo "sys python version: $(shell $(SYS_PYTHON_CMD) --version)"
	@echo "PIP_CMD = $(PIP_CMD)"
	@echo "PYTHON_CMD = $(PYTHON_CMD)"
	$(PYTHON_CMD) $(SETUP_PY) info

_test_pip_outdated:
	$(PIP_CMD) list --outdated

_test_flake8:
	$(FLAKE8_CMD) $(FLAKE8_ARGS)

manual-pytest:
	$(PYTEST_CMD) \
		$(PYTEST_ARGS) \
		$(PYTEST_ARGS_MANUAL)

_test_pytest:
	$(PYTEST_CMD) $(PYTEST_ARGS)

_test_isort:
	$(ISORT_CMD) $(ISORT_ARGS) setup.py
	$(ISORT_CMD) $(ISORT_ARGS) lib
	$(ISORT_CMD) $(ISORT_ARGS) $(TESTS_DIR)

test: _test_pip_outdated _test_flake8 _test_isort _test_pytest

clean-cover:
	find . -depth -name \*.cover -exec rm {} \;

gh_actions:
	act --container-architecture linux/amd64

clean:
	rm -rf $(VENV_DIR)
	rm -rf build
	rm -rf dist
	rm -rf $(TESTS_DIR)/.lib
	# python $(SETUP_PY) clean
	find . -depth -name *.egg-info -exec rm -rf {} \; || true
	find lib -name \*\.pyc -exec rm {} \;

help:
	@echo "Choose from the following:"
	@echo "	dev		Create a virtualenv (in $(VENV_DIR))."
	@echo "	info		Show various info."
	@echo "	test		Run unit PEP8 and unit tests."
	@echo "	update-reqs	Update requirements files (using pur)."
	@echo "	clean		Delete various development files and dirs."
	@echo "	help		This message."
