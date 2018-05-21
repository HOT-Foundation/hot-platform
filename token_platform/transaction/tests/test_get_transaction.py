from tests.test_utils import BaseTestClass
from aiohttp.test_utils import unittest_run_loop

import asynctest


class TestGetTransactionHashFromRequest(BaseTestClass):
    async def setUpAsync(self):
        self.address = 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF'
        self.transaction_url = '/wallet/{}/get-transaction-hash'.format(self.address)
        self.params = {'meta': '1'}
        self.tx_hash = '4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9'

    @unittest_run_loop
    @asynctest.patch('transaction.get_transaction.get_transaction_hash')
    async def test_get_transaction_hash_from_request_success(self, mock_get_transaction_hash):
        mock_get_transaction_hash.return_value = self.tx_hash

        response = await self.client.get(self.transaction_url, params=self.params)
        resp = await response.json()
        assert resp == self.tx_hash
