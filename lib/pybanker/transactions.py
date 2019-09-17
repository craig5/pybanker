"""
"""
# core python packages
import collections
import hashlib
import os
import re
# third party packages
import yaml
# custom packages
import pybanker.shared


class BadTransactionFileException(Exception):
    pass


class BadTransactionException(Exception):
    pass


class _TransactionItem(collections.UserDict):

    def __init__(self, transaction_id):
        """
        """
        super().__init__({})
        self['transaction-id'] = transaction_id

    @property
    def transaction_id(self):
        return self['transaction-id']

    @property
    def date_string(self):
        return self['date'].strftime('%Y-%m-%d')

    @property
    def amount_string(self):
        return str(self['amount'])

    def load_data(self, data):
        self.update(data)

    def calc_id(self):
        if 'entered_nano' not in self:
            raise BadTransactionException('Entered time is missing.')
        if self['entered_nano'] is None:
            raise BadTransactionException('Entered time is none.')
        hashed_string = str(self['entered_nano'])
        sha_obj = hashlib.sha256(hashed_string.encode('utf-8'))
        return sha_obj.hexdigest()

    def verify_data(self):
        self._verify_id()
        self._verify_splits()

    def _verify_id(self):
        calced_id = self.calc_id()
        if self.transaction_id != calced_id:
            raise BadTransactionException('Bad ID: {0} != {1}'.format(
                self.transaction_id, calced_id))
        return

    def calc_split_total(self):
        total = 0
        for cur in self['splits']:
            total += cur['amount']
        return total

    def _verify_splits(self):
        if self['amount'] != self.calc_split_total():
            raise BadTransactionException(
                'Split total not equal to transaction amount: {}'.format(
                    self.transaction_id))


class Transactions(object):

    def __init__(self):
        self.config = pybanker.shared.GlobalConfig()
        self.logger = self.config.build_logger(self)
        self.transactions = dict()
        self._load_all_transactions()

    @property
    def transactions_dir(self):
        return os.path.join(self.config.data_dir, 'transactions')

    def add_transaction(self, transaction):
        cur_id = transaction.transaction_id
        if cur_id in self.transactions:
            raise BadTransactionException('Duplicate ID: {}'.format(cur_id))
        self.transactions[cur_id] = transaction

    def parse_file(self, file_name):
        with open(file_name, 'r') as fp:
            if file_name.endswith('.yaml'):
                all_data = yaml.safe_load(fp)
            # TODO add json support (need some tests)
            else:
                raise BadTransactionFileException(
                    'Unknown file type: {}'.format(file_name))
        for cur_id, cur_data in all_data.items():
            new_transaction = _TransactionItem(cur_id)
            new_transaction.load_data(cur_data)
            self.add_transaction(new_transaction)

    def _load_all_transactions(self):
        self.logger.debug(f'Finding transactions in: {self.transactions_dir}')
        file_matcher = re.compile(r'/.*/\d{4}-\d{2}.(yaml|json)')
        for cur in os.listdir(self.transactions_dir):
            full = os.path.join(self.transactions_dir, cur)
            if file_matcher.match(full) is None:
                continue
            self.parse_file(full)

    def verify_data(self):
        for cur_id, cur_transaction in self.transactions.items():
            cur_transaction.verify_data()

    def link_receipts(self, receipts_obj):
        for cur in self.transactions.values():
            for cur_receipt in cur['receipts']:
                cur_file_name = cur_receipt['file_name']
                if cur_file_name in receipts_obj.receipts:
                    link_rec = receipts_obj.receipts[cur_file_name]
                    link_rec['linked-transaction-id'] = cur.transaction_id
                else:
                    raise BadTransactionException('Unknown receipt file: {}'.format(
                        cur_file_name))


if __name__ == '__main__':
    pass
