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
FLAKE8_CMD = $(BIN_DIR)/flake8
FLAKE8_ARGS =
#
SYS_PYTHON_CMD = $(shell which python3)

ifeq ("$(TRAVIS)", "true")
$(warning "Resetting commands for travis.")
PIP_CMD = pip3
PYTHON_CMD = python3
PYTEST_CMD = pytest
FLAKE8_CMD = flake8
endif

travis-setup: pip_reqs setup_develop

develop: _local_virtualenv pip_reqs setup_develop

# To install venv on ubuntu 14.04:
#	sudo apt-get install python3-venv
_local_virtualenv:
	$(SYS_PYTHON_CMD) -m venv $(VENV_DIR)

pip_reqs:
	$(PIP_CMD) install --upgrade pip
	$(PIP_CMD) install --progress-bar off --upgrade setuptools
	$(PIP_CMD) install --progress-bar off -r tests/requirements.txt
	$(PIP_CMD) install --progress-bar off -r requirements.txt
	$(PIP_CMD) install --progress-bar off -r dev_requirements.txt

setup_develop:
	$(PYTHON_CMD) $(SETUP_PY) develop

info:
	@echo "VENV_DIR = $(VENV_DIR)"
	@echo "SYS_PYTHON_CMD = $(SYS_PYTHON_CMD)"
	@echo "PIP_CMD = $(PIP_CMD)"
	@echo "PYTHON_CMD = $(PYTHON_CMD)"
	$(PYTHON_CMD) $(SETUP_PY) info

test:
	$(PIP_CMD) list --outdated
	$(FLAKE8_CMD) $(FLAKE8_ARGS)
	$(PYTEST_CMD) $(PYTEST_ARGS)

clean:
	rm -rf $(VENV_DIR)
	rm -rf build
	rm -rf dist
	rm -rf $(TESTS_DIR)/.lib
	# python $(SETUP_PY) clean
	find .  -name *.egg-info -depth -exec rm -rf {} \; || true
	find lib -name \*\.pyc -exec rm {} \;

help:
	@echo "Choose from the following:"
	@echo "	develop	Create a virtualenv (in $(VENV_DIR))."
	@echo "	info	Show various info."
	@echo "	test	Run unit PEP8 and unit tests."
	@echo "	clean	Delete various development files and dirs."
	@echo "	help	This message."
