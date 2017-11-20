#
DEFAULT: help
.DEFAULT: help

VENV_DIR = venv
TESTS_DIR = tests
LIB_DIR = lib
SETUP_PY = setup.py
BIN_DIR = $(VENV_DIR)/bin
PYTHON_CMD = $(BIN_DIR)/python3
PIP_CMD = $(BIN_DIR)/pip
#
NOSE_CMD = $(BIN_DIR)/nose2
NOSE_ARGS =
FLAKE8_CMD = $(BIN_DIR)/flake8
FLAKE8_ARGS =
# This sucks...
# Shouldn't need a hard-coded path, but my path is messed up.
SYS_PYTHON_CMD = /usr/bin/python3

develop: _local_virtualenv pip_reqs setup_develop

# To install venv on ubuntu 14.04:
#	sudo apt-get install python3-venv
_local_virtualenv:
	$(SYS_PYTHON_CMD) -m venv $(VENV_DIR)
	$(PIP_CMD) install --upgrade pip

pip_reqs:
	$(PIP_CMD) install -r tests/requirements.txt
	$(PIP_CMD) install -r requirements.txt
	$(PIP_CMD) install -r dev_requirements.txt

setup_develop:
	$(PYTHON_CMD) $(SETUP_PY) develop

info:
	@echo "VENV_DIR = $(VENV_DIR)"
	@echo "SYS_PYTHON_CMD = $(SYS_PYTHON_CMD)"
	$(PYTHON_CMD) $(SETUP_PY) info

test:
	$(FLAKE8_CMD) $(FLAKE8_ARGS) $(LIB_DIR)
	$(FLAKE8_CMD) $(FLAKE8_ARGS) $(TESTS_DIR)
	$(FLAKE8_CMD) $(FLAKE8_ARGS) $(SETUP_PY)
	$(NOSE_CMD) $(NOSE_ARGS)

clean:
	rm -rf $(VENV_DIR)
	rm -rf build
	rm -rf dist
	rm -rf $(TESTS_DIR)/.lib
	# python $(SETUP_PY) clean
	find lib/work_tools.egg-info -type f -exec rm {} \; || true
	find lib -name \*\.pyc -exec rm {} \;

help:
	@echo "Choose from the following:"
	@echo "	develop		Create a virtualenv (in $(VENV_DIR))"
	@echo "	clean		Delete various development files and dirs."
	@echo "	help		This message."
