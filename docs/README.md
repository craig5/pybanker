# Overview

There are many applications that will manage your finances.
But, most (all?) of them use a GUI to make data entry easier
and more intuitive.
However, that doesn't lend itself to automation.

The main goal of this project is to create a "command line"
driven application with an API that will one to take control
of their financial data.

# High Level Configuration

There exists a main configuration file located at
$HOME/.pybanker/config.ini

Example content:
```
[default]
data_dir = Documents/finances/
```
(The `data_dir` is relative to your home directory.)
