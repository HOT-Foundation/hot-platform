from stellar_base.operation import ManageData
# from stellar_base.exceptions import XdrLengthError
from stellar_base.stellarxdr import Xdr


class PlatformMangeData(ManageData):

    def __init__(self, opts):

        assert type(opts) is dict

        self.source = opts.get('source')
        self.body = Xdr.nullclass()
        self.data_name = opts.get('data_name')
        self.data_value = opts.get('data_value')

        valid_data_name_len = len(self.data_name) <= 64
        valid_data_val_len = len(self.data_value) <= 64

        # if not valid_data_name_len or not valid_data_val_len:
        #     raise XdrLengthError(
        #         "Data or value should be <= 64 bytes (ascii encoded).")
