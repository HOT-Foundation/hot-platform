from tests.test_utils import BaseTestClass

from aiohttp.test_utils import unittest_run_loop
from asynctest import patch
from conf import settings
from joint_wallet.generate_joint_wallet import (build_joint_wallet,
                                                generate_joint_wallet)
from router import reverse


class TestGenerateJointWallet(BaseTestClass):
    async def setUpAsync(self):
        self.host = settings['HOST']

    @unittest_run_loop
    @patch('joint_wallet.generate_joint_wallet.generate_joint_wallet')
    async def test_generate_jount_wallet_from_request(self, mock_joint_wallet):
        mock_joint_wallet.return_value = {}
        deal_address = 'GC5D6IXB2DW3RWU2Y4YBKJMWH3LOAHNWEAN5NDDGNO74AL5IWXK6XJ4O'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        url = reverse('generate-joint-wallet', wallet_address=deal_address)
        data = {
            'parties': [{
                'address': 'address',
                'amount': 10
                }],
            'creator_address':'HOTNOW_ADDRESS',
            'starting_xlm': 5,
            'transaction_source_address' : transaction_source_address
            }

        resp = await self.client.request('POST', url, json=data)
        assert resp.status == 200
        body = await resp.json()
        mock_joint_wallet.assert_called_once_with(transaction_source_address, deal_address, data['parties'], data['creator_address'], 5, None)

    @unittest_run_loop
    @patch('joint_wallet.generate_joint_wallet.build_joint_wallet')
    async def test_generate_joint_wallet_with_out_meta(self, mock_build):
        deal_address = 'deal_address'
        parties = [
            {
                'address': 'address1',
                'amount': 10
            },{
                'address': 'address2',
                'amount': 20
            }
        ]
        creator = 'creator_address'
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        mock_build.return_value = ('create_joint_wallet_xdr', 'create_joint_wallet_tx_hash')
        result = await generate_joint_wallet(transaction_source_address, deal_address, parties, creator, 5)

        expect = {
            "@id": reverse('generate-joint-wallet', wallet_address='deal_address'),
            "@transaction_url": reverse('transaction', transaction_hash='create_joint_wallet_tx_hash'),
            "signers": [{
                    "public_key": "address1",
                    "weight": 1
                },{
                    "public_key": "address2",
                    "weight": 1
                },{
                    "public_key": "creator_address",
                    "weight": 1
                },{
                    "public_key": "deal_address",
                    "weight": 1
                }
            ],
            "xdr": "create_joint_wallet_xdr",
            "transaction_hash": "create_joint_wallet_tx_hash"
        }

        assert result == expect

    @unittest_run_loop
    @patch('joint_wallet.generate_joint_wallet.build_joint_wallet')
    async def test_generate_joint_wallet_with_meta(self, mock_build):
        deal_address = 'deal_address'
        parties = [
            {
                'address': 'address1',
                'amount': 10
            },{
                'address': 'address2',
                'amount': 20
            }
        ]
        creator = 'creator_address'
        meta = {
            "expiration_date": "2018-05-15"
        }
        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        mock_build.return_value = ('create_joint_wallet_xdr', 'create_joint_wallet_tx_hash')
        result = await generate_joint_wallet(transaction_source_address, deal_address, parties, creator, 5, meta)

        expect = {
            "@id": reverse('generate-joint-wallet', wallet_address='deal_address'),
            "@transaction_url": reverse('transaction', transaction_hash='create_joint_wallet_tx_hash'),
            "signers": [{
                    "public_key": "address1",
                    "weight": 1
                },{
                    "public_key": "address2",
                    "weight": 1
                },{
                    "public_key": "creator_address",
                    "weight": 1
                },{
                    "public_key": "deal_address",
                    "weight": 1
                }
            ],
            "xdr": "create_joint_wallet_xdr",
            "transaction_hash": "create_joint_wallet_tx_hash"
        }

        assert result == expect

    @unittest_run_loop
    @patch('joint_wallet.generate_joint_wallet.Builder')
    async def test_build_joint_wallet(self, mock_builder):
        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_trust_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.append_payment_op.return_value = 'test'
        instance.gen_xdr.return_value = b'generate-joint-wallet-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'

        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        deal_address = 'GAYIEFTTY52HSXAHKTQGK4K4OQRKMD324WCG4O2HGIQUGVTVE6RZW25F'
        creator = 'GABEAFZ7POCHDY4YCQMRAGVVXEEO4XWYKBY4LMHHJRHTC4MZQBWS6NL6'
        parties = [{
            "address": "GDR3AGPEISYHLHAB6EVP3HD4COCIT7SPGL7WTSIZR3PNBWKFKZGTUJSN",
            "amount": 10
        },{
            "address": "GAYIEFTTY52HSXAHKTQGK4K4OQRKMD324WCG4O2HGIQUGVTVE6RZW25F",
            "amount": 15
        }]
        result_xdr, result_hash = await build_joint_wallet(transaction_source_address, deal_address, parties, creator, 5)
        assert result_xdr == 'generate-joint-wallet-xdr'
        assert result_hash == '74782d68617368'

    @unittest_run_loop
    @patch('joint_wallet.generate_joint_wallet.Builder')
    async def test_build_joint_wallet_with_meta(self, mock_builder):
        instance = mock_builder.return_value
        instance.append_create_account_op.return_value = 'test'
        instance.append_trust_op.return_value = 'test'
        instance.append_set_options_op.return_value = 'test'
        instance.append_payment_op.return_value = 'test'
        instance.gen_xdr.return_value = b'generate-joint-wallet-xdr'
        instance.te.hash_meta.return_value = b'tx-hash'

        transaction_source_address = 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ'
        deal_address = 'GAYIEFTTY52HSXAHKTQGK4K4OQRKMD324WCG4O2HGIQUGVTVE6RZW25F'
        creator = 'GABEAFZ7POCHDY4YCQMRAGVVXEEO4XWYKBY4LMHHJRHTC4MZQBWS6NL6'
        parties = [{
            "address": "GDR3AGPEISYHLHAB6EVP3HD4COCIT7SPGL7WTSIZR3PNBWKFKZGTUJSN",
            "amount": 10
        },{
            "address": "GAYIEFTTY52HSXAHKTQGK4K4OQRKMD324WCG4O2HGIQUGVTVE6RZW25F",
            "amount": 15
        }]
        meta = {
            "expiration_date": "2018-05-15"
        }
        result_xdr, result_hash = await build_joint_wallet(transaction_source_address, deal_address, parties, creator, 5, meta)
        assert result_xdr == 'generate-joint-wallet-xdr'
        assert result_hash == '74782d68617368'
