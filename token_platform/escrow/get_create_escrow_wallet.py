import binascii
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

from aiohttp import web
from stellar_base.builder import Builder
from stellar_base.utils import DecodeError

from conf import settings
from transaction.transaction import get_signers, get_threshold_weight


async def get_create_escrow_wallet_from_request(request: web.Request) -> web.Response:
    """AIOHTTP Request create account xdr and presigned transaction xdr"""
    try:
        body = await request.json()
    except:
        raise TypeError('Please ensure parameter is in json format.')

    stellar_escrow_address = body.get('stellar_escrow_address', None)
    if not stellar_escrow_address:
        raise web.HTTPBadRequest(reason='Parameter stellar_escrow_address not found. Please ensure parameters is valid.')

    stellar_merchant_address = body.get('stellar_merchant_address', None)
    if not stellar_merchant_address:
        raise web.HTTPBadRequest(reason='Parameter stellar_merchant_address not found. Please ensure parameters is valid.')

    stellar_hotnow_address = body.get('stellar_hotnow_address', None)
    if not stellar_hotnow_address:
        raise web.HTTPBadRequest(reason='Parameter stellar_hotnow_address not found. Please ensure parameters is valid.')

    starting_balance = body.get('starting_balance', None)
    if not starting_balance:
        raise web.HTTPBadRequest(reason='Parameter starting_balance not found. Please ensure parameters is valid.')
    starting_balance = int(starting_balance)

    cost_per_tx = body.get('cost_per_tx', None)
    if not cost_per_tx:
        raise web.HTTPBadRequest(reason='Parameter cost_per_tx not found. Please ensure parameters is valid.')
    cost_per_tx = int(cost_per_tx)


    result = await create_escrow_wallet(stellar_escrow_address,
                                stellar_merchant_address,
                                stellar_hotnow_address,
                                starting_balance,
                                cost_per_tx)

    return web.json_response(result)


async def create_escrow_wallet(stellar_escrow_address: str,
                                           stellar_merchant_address: str,
                                           stellar_hotnow_address: str,
                                           starting_balance: int,
                                           cost_per_tx: int
                                           ) -> Dict:
    '''Making transaction for creating escrow wallet'''
    number_of_transaction = (starting_balance / cost_per_tx) + 2
    starting_xlm: int = calculate_initial_xlm(3, number_of_transaction)
    starting_custom_asset: int = starting_balance

    unsigned_xdr, tx_hash = await build_create_escrow_wallet_transaction(stellar_escrow_address,
        stellar_merchant_address,
        stellar_hotnow_address,
        starting_xlm,
        starting_custom_asset
    )

    host = settings['HOST']
    return {
        'escrow_address': stellar_escrow_address,
        '@url': '{}/create-escrow'.format(host),
        '@transaction_url': '{}/transaction/{}'.format(host, tx_hash),
        'signers': [stellar_escrow_address, stellar_merchant_address, stellar_hotnow_address],
        'unsigned_xdr': unsigned_xdr
    }

def calculate_initial_xlm(number_of_entries: int, number_of_transaction: int) -> int:
    '''Calculate starting balance for wallet
    starting balance: minimum balance + transaction fee
    minimum balance = (2 + number of entries) × base reserve
    '''
    transaction_fee = 0.00001
    minumum_balance_raw = ((2 + number_of_entries) * 0.5) + (number_of_transaction * transaction_fee)
    our_value = Decimal(minumum_balance_raw)
    result = Decimal(our_value.quantize(Decimal('.0001'), rounding=ROUND_HALF_UP))

    return result

async def build_create_escrow_wallet_transaction(stellar_escrow_address: str,
                                           stellar_merchant_address: str,
                                           stellar_hotnow_address: str,
                                           starting_native_asset: int,
                                           starting_custom_asset: int
                                           ) -> Dict:
    '''Building transaction for generating escrow wallet with minimum balance of lumens
        and return unsigned XDR and transaction hash.

        Args:

        * stellar_escrow_address: an address of new wallet
        * stellar_merchant_address: an address of merchant wallet
        * stellar_hotnow_address: an address of source wallet which is owner of the transaction.
        * starting_native_asset: starting amount of XLM.
        * starting_custom_asset: starting amount of custom asset.
    '''

    builder = Builder(address=stellar_hotnow_address,
                      network=settings['STELLAR_NETWORK'])
    builder.append_create_account_op(
        source=stellar_hotnow_address, destination=stellar_escrow_address, starting_balance=starting_native_asset)
    try:
        builder.append_trust_op(
            source=stellar_escrow_address, destination=settings['ISSUER'], code=settings['ASSET_CODE'])
    except DecodeError:
        raise web.HTTPBadRequest(reason='Parameter values are not valid.')
    except Exception as e:
        msg = str(e)
        raise web.HTTPInternalServerError(reason=msg)

    builder.append_set_options_op(
        source=stellar_escrow_address, signer_address=stellar_hotnow_address, signer_type='ed25519PublicKey', signer_weight=1)
    builder.append_set_options_op(
        source=stellar_escrow_address, signer_address=stellar_merchant_address, signer_type='ed25519PublicKey', signer_weight=1)
    builder.append_set_options_op(source=stellar_escrow_address,
                                  master_weight=0, low_threshold=2, med_threshold=2, high_threshold=2)

    builder.append_payment_op(source=stellar_merchant_address,
                                destination=stellar_escrow_address,
                                asset_type=settings['ASSET_CODE'],
                                asset_issuer=settings['ISSUER'],
                                amount=starting_custom_asset)

    try:
        unsigned_xdr = builder.gen_xdr()
    except Exception as e:
        raise web.HTTPBadRequest(reason='Bad request, Please ensure parameters are valid.')

    tx_hash = builder.te.hash_meta()

    return unsigned_xdr.decode(), binascii.hexlify(tx_hash).decode()
