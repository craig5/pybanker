#
DEFAULT: help
.DEFAULT: help

VENV_DIR = venv
TESTS_DIR = tests
BIN_DIR = $(VENV_DIR)/bin
PYTHON_CMD = $(BIN_DIR)/python3
PIP_CMD = $(BIN_DIR)/pip
#
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
	$(PIP_CMD) install -r tests/requirements.txt -t tests/.lib
	$(PIP_CMD) install -r requirements.txt
	$(PIP_CMD) install -r dev_requirements.txt

setup_develop:
	$(PYTHON_CMD) setup.py develop

info:
	@echo "VENV_DIR = $(VENV_DIR)"
	@echo "SYS_PYTHON_CMD = $(SYS_PYTHON_CMD)"
	$(PYTHON_CMD) setup.py info

test:
	$(PYTHON_CMD) setup.py flake8
	$(PYTHON_CMD) setup.py test
#	$(NOSE_CMD) --verbose

clean:
	rm -rf $(VENV_DIR)
	rm -rf build
	rm -rf dist
	rm -rf $(TESTS_DIR)/.lib
	# python setup.py clean
	find lib/work_tools.egg-info -type f -exec rm {} \; || true
	find lib -name \*\.pyc -exec rm {} \;

help:
	@echo "Choose from the following:"
	@echo "	develop		Create a virtualenv (in $(VENV_DIR))"
	@echo "	clean		Delete various development files and dirs."
	@echo "	help		This message."
