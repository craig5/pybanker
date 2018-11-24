"""
Classes related to the accounts.
"""
# core python packages
import collections
import logging
# third party packages
import yaml
# custom packages
import pybanker.shared


class Accounts(collections.OrderedDict):
    config = pybanker.shared.GlobalConfig()

    def __init__(self):
        super().__init__()
        name = self.__class__.__name__
        self.logger = logging.getLogger(name)
        self._load_accounts()

    def _load_accounts(self):
        file_name = self.config.accounts_file
        self.logger.debug('Loading accounts: {}'.format(file_name))
        with open(file_name, 'r') as fp:
            raw = yaml.load(fp)
        for cur_id, cur_data in raw.items():
            new_account = _SingleAccount(cur_id, cur_data)
            # TODO check for duplicate accounts
            self[new_account.account_id] = new_account

    def show_summary(self):
        print('Accounts')
        print('========')
        for cur in self.values():
            print(cur.get_summary_output(), end='')


class _SingleAccount(object):

    def __init__(self, number, data):
        """
        :param number: Integer for the account ID.
        :param data: Dictionary container the basic account data.
        """
        name = self.__class__.__name__
        self.logger = logging.getLogger(name)
        #
        self.number = number
        self._load_data(data)

    @property
    def account_id(self):
        """
        The 'short name' for this account.
        """
        return self.short_name

    def _load_data(self, data):
        """
        Put the data dictionary into instance variables.
        """
        # TODO add some exceptions if required data is missing
        # TODO have some defaults for missing data
        self.name = data['name']
        self.type = data['type']
        self.active = data['active']
        self.visible = data['visible']
        self.account_end = data.get('account_end', None)
        try:
            self.short_name = data['short_name']
        except KeyError:
            self.short_name = self.name

    def __str__(self):
        return self.name

    @property
    def summary_data(self):
        """
        Build a dictionary with the "summary data" for this account.
        """
        data = {
            'Name': self.name,
            'Type': self.type
        }
        return {self.short_name: data}

    def get_summary_output(self):
        """
        Return a string that can be printed that shows this account's summary data.
        """
        output = yaml.dump(
            self.summary_data,
            indent=2,
            default_flow_style=False
        )
        return output


if __name__ == '__main__':
    pass
