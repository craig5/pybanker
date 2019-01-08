"""
Command line tool to mange your finances.
"""
# core python packages
import argparse
import logging
# third party packages
# custom packages
import pybanker.shared


class PyBankerCli(object):

    def __init__(self):
        self._init_vars()
        self._init_logger()
        self._init_cli()

    def _init_vars(self):
        self.global_config = pybanker.shared.GlobalConfig()
        self.logger = None
        self.command = None

    def _init_logger(self):
        logger_name = self.global_config.base_logger_name
        self.logger = logging.getLogger(logger_name)
        format_string = '[%(levelname)s]'
        format_string += ' %(name)s(%(lineno)d)'
        format_string += ' - %(message)s'
        formatter = logging.Formatter(format_string)
        stdout = logging.StreamHandler()
        stdout.setFormatter(formatter)
        stdout.setLevel(self.global_config.logger_level)
        self.logger.setLevel(self.global_config.logger_level)
        self.logger.addHandler(stdout)
        self.logger.debug('Logger initialized: {0}'.format(logger_name))

    def _init_cli(self):
        self.logger.debug('Initializing CLI.')
        self.cli = argparse.ArgumentParser(description=__doc__)
        self.cli.add_argument(
            '--log-level',
            choices=['debug', 'info', 'warn'],
            help='Change logging level.'
        )
        command_opts = [cur['option'] for cur in self.global_config.commands]
        default_command = command_opts[0]
        self.cli.add_argument(
            'command',
            nargs='?',
            default=default_command,
            choices=command_opts,
            help='Command to run. (Default: {})'.format(default_command)
        )

    def parse_args(self):
        self.logger.debug('Parsing cli args.')
        self.args = self.cli.parse_args()
        level_name = self.args.log_level
        if level_name is not None:
            self.logger.debug('Level name: {}'.format(level_name))
            level = logging.getLevelName(level_name.upper())
            self.logger.debug('Level: {}'.format(level))
            self.logger.setLevel(level)
            for handler in self.logger.handlers:
                handler.setLevel(level)
            self.logger.debug('Logger level reset to: {}'.format(level_name))
        self.command = self.args.command
        self.logger.debug('Command: {}'.format(self.command))

    def __call__(self):
        self.logger.debug('Inside call.')
        self.parse_args()
        bank = pybanker.Banker()
        bank(self.command)


def main():
    cli_obj = PyBankerCli()
    cli_obj()


if __name__ == '__main__':
    pass
