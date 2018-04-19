from tests.test_utils import BaseTestClass
from aiohttp.test_utils import unittest_run_loop
from wallet.get_next_tx_sequence import get_next_tx_sequence_from_request
from asynctest import patch
# from aiohttp.web_exceptions import HTTPBadRequest

class TestGetNextTransactionNumber(BaseTestClass):

    @unittest_run_loop
    @patch('wallet.get_next_tx_sequence.get_next_sequence_number')
    async def test_get_next_tx_sequence_from_request_success(self, mock_seq_no) -> None:
        mock_seq_no.return_value = 12314355345345
        wallet_address = 'GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5'
        url = f'/wallet/{wallet_address}/transaction/next-sequence'

        resp = await self.client.request("GET", url)
        assert resp.status == 200

        message = await resp.json()
        seq_number = message.get('next_sequence', )
        assert isinstance(seq_number, int)
        mock_seq_no.assert_called_once_with('GASF2Q2GZMQMMNSYDU34MU4GJKSZPSN7FYKQEMNH4QJMVE3JR3C3I3N5')
