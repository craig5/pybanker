"""
Classes related to the accounts.
"""
# core python libraries
import logging
# third party libraries


class Account(object):

    def __init__(self, number, data):
        self.__init_logger()
        self.number = number
        self.__load_data(data)

    def __init_logger(self):
        name = self.__class__.__name__
        self.logger = logging.getLogger(name)

    def __load_data(self, data):
        self.name = data['name']
        self.type = data['type']
        self.active = data['active']
        self.visible = data['visible']
        self.account_end = data.get('account_end', None)
        self.short_name = data['short_name']

    def __str__(self):
        return self.name

    def get_summary(self):
        """Show a short summary of the account."""
        output = self.name
        return output
# End of file.
