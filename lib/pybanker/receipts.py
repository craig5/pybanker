"""
"""
import collections
import logging
import os

import pybanker.shared


class DuplicateReceiptException(Exception):
    pass


class _ReceiptItem(collections.UserDict):

    def __init__(self, relative_path):
        """
        """
        super().__init__({})
        self['relative-path'] = relative_path

    @property
    def receipt_id(self):
        return self['relative-path']


class Receipts(object):

    def __init__(self):
        name = self.__class__.__name__
        self.logger = logging.getLogger(name)
        self.global_config = pybanker.shared.GlobalConfig()
        self._receipts = None

    @property
    def receipts_dir(self):
        return os.path.join(self.global_config.data_dir, 'receipts')

    def _find_all_receipts(self):
        self.logger.debug(f'Finding receipts in: {self.receipts_dir}')
        receipts = dict()
        base_dir = self.global_config.data_dir
        for dir_path, dir_names, file_names in os.walk(self.receipts_dir):
            for cur in file_names:
                full_file = os.path.join(dir_path, cur)
                relative_file = full_file.replace(base_dir, '', 1)
                new_receipt = _ReceiptItem(relative_file)
                new_receipt['file-path'] = full_file
                if new_receipt.receipt_id in receipts:
                    msg = 'Duplicate receipt: {}'.format(new_receipt.receipt_id)
                    raise DuplicateReceiptException(msg)
                receipts[new_receipt.receipt_id] = new_receipt
        return receipts

    @property
    def receipts(self):
        if self._receipts is None:
            self._receipts = self._find_all_receipts()
        return self._receipts

    def verify_data(self):
        # TODO finish
        pass


if __name__ == '__main__':
    pass
