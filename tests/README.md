# Hints

Some hints on running the tests manually.

One can run just a single test and set the lgoger level to 'debug':
```
./venv/bin/pytest \
	--capture=no \
	--log-cli-level=debug
	tests/test_frequency_utils.py
```
