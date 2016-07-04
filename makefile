#
DEFAULT: help
.DEFAULT: help

OS_PYTHON = /usr/bin/python3
VENV_DIR = venv
TESTS_DIR = tests
BIN_DIR = $(VENV_DIR)/bin
PYTHON_CMD = $(BIN_DIR)/python
PIP_CMD = $(BIN_DIR)/pip


help:
	@echo "Choose from the following:"
	@echo "	develop		Create a virtualenv (in $(VENV_DIR))"
	@echo "	clean		Delete various development files and dirs."
	@echo "	help		This message."

develop:
	virtualenv -p $(OS_PYTHON) $(VENV_DIR)
	$(PIP_CMD) install -r tests/requirements.txt -t tests/.lib
	$(PIP_CMD) install -r requirements.txt
	$(PYTHON_CMD) setup.py develop

info:
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

# End of file.
