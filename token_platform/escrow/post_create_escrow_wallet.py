import binascii
from decimal import ROUND_UP, Decimal
from typing import Dict, List

from aiohttp import web
from stellar_base.builder import Builder
from stellar_base.utils import DecodeError

from conf import settings
from transaction.transaction import get_signers, get_threshold_weight


async def post_create_escrow_wallet_from_request(request: web.Request) -> web.Response:
    """AIOHTTP Request create account xdr and presigned transaction xdr"""
    body = await request.json()

    try:
        escrow_address = request.match_info['escrow_address']
        provider_address = body['provider_address']
        creator_address = body['creator_address']
        destination_address = body['destination_address']
        starting_balance = body['starting_balance']
        cost_per_transaction = body['cost_per_tx']
        expiration_date = body['expiration_date']
    except KeyError as e:
        msg = str(e)
        raise web.HTTPBadRequest(reason=f'Parameter {msg} not found. Please ensure parameters is valid.')

    try:
        int(starting_balance)
    except ValueError as ex:
        raise web.HTTPBadRequest(reason=f'Parameter starting_balance is not valid.')

    try:
        int(cost_per_transaction)
    except ValueError as ex:
        raise web.HTTPBadRequest(reason=f'Parameter cost_per_tx is not valid.')

    result = await create_escrow_wallet(escrow_address,
                                creator_address,
                                destination_address,
                                provider_address,
                                starting_balance,
                                expiration_date,
                                cost_per_transaction)

    result['@id'] = escrow_address
    return web.json_response(result)


async def create_escrow_wallet(escrow_address: str,
                                           creator_address: str,
                                           destination_address: str,
                                           provider_address: str,
                                           starting_balance: str,
                                           expiration_date: str,
                                           cost_per_transaction: str
                                           ) -> Dict:
    '''Making transaction for creating escrow wallet

        number_of_transaction + 2 due to transfer to merchant and merge back to hotnow
        number of entries is 8 due to escrow account have 1 trust line, add 2 signers and 5 data entries
    '''
    starting_balance = Decimal(starting_balance)
    cost_per_transaction = Decimal(cost_per_transaction)

    number_of_transaction = (starting_balance / cost_per_transaction) + 2
    starting_xlm: Decimal = calculate_initial_xlm(8, number_of_transaction)
    starting_custom_asset: Decimal = starting_balance

    unsigned_xdr, tx_hash = await build_create_escrow_wallet_transaction(escrow_address = escrow_address,
        provider_address = provider_address,
        creator_address = creator_address,
        destination_address = destination_address,
        cost_per_transaction = cost_per_transaction,
        expiration_date = expiration_date,
        starting_native_asset = starting_xlm,
        starting_custom_asset = starting_custom_asset
    )

    host = settings['HOST']
    return {
        'escrow_address': escrow_address,
        '@url': f'{host}/escrow/{escrow_address}/create-wallet',
        '@transaction_url': f'{host}/transaction/{tx_hash}',
        'signers': [escrow_address, creator_address, provider_address],
        'unsigned_xdr': unsigned_xdr
    }

def calculate_initial_xlm(number_of_entries: int, number_of_transaction: int) -> Decimal:
    '''Calculate starting balance for wallet
    starting balance: minimum balance + transaction fee
    minimum balance = (2 + number of entries) × base reserve
    '''

    transaction_fee = Decimal('0.00001')
    base_reserve = Decimal('0.5')
    number_of_transaction = Decimal(number_of_transaction)
    number_of_entries = Decimal(number_of_entries)
    minumum_balance_raw = ((2 + number_of_entries) * base_reserve) + (number_of_transaction * transaction_fee)
    our_value = Decimal(minumum_balance_raw)
    result = Decimal(our_value.quantize(Decimal('.0001'), rounding=ROUND_UP))

    return result

async def build_create_escrow_wallet_transaction(escrow_address: str,
                                           creator_address: str,
                                           destination_address: str,
                                           provider_address: str,
                                           expiration_date: str,
                                           cost_per_transaction: Decimal,
                                           starting_native_asset: Decimal,
                                           starting_custom_asset: Decimal
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

    builder = Builder(address=creator_address,
                      network=settings['STELLAR_NETWORK'])
    builder.append_create_account_op(
        source=creator_address, destination=escrow_address, starting_balance=starting_native_asset)

    try:
        builder.append_trust_op(
            source=escrow_address, destination=settings['ISSUER'], code=settings['ASSET_CODE'])
    except DecodeError:
        raise web.HTTPBadRequest(reason='Parameter escrow_address or issuer address are not valid.')
    except Exception as e:
        msg = str(e)
        raise web.HTTPInternalServerError(reason=msg)

    builder.append_manage_data_op(source=escrow_address, data_name='creator_address', data_value=creator_address)
    builder.append_manage_data_op(source=escrow_address, data_name='destination_address', data_value=destination_address)
    builder.append_manage_data_op(source=escrow_address, data_name='provider_address', data_value=provider_address)
    builder.append_manage_data_op(source=escrow_address, data_name='expiration_date', data_value=expiration_date)
    builder.append_manage_data_op(source=escrow_address, data_name='cost_per_transaction', data_value=str(cost_per_transaction))

    builder.append_set_options_op(
        source=escrow_address, signer_address=creator_address, signer_type='ed25519PublicKey', signer_weight=1)
    builder.append_set_options_op(
        source=escrow_address, signer_address=provider_address, signer_type='ed25519PublicKey', signer_weight=1)
    builder.append_set_options_op(source=escrow_address,
                                  master_weight=0, low_threshold=2, med_threshold=2, high_threshold=2)


    builder.append_payment_op(source=provider_address,
                                destination=escrow_address,
                                asset_type=settings['ASSET_CODE'],
                                asset_issuer=settings['ISSUER'],
                                amount=starting_custom_asset)

    try:
        unsigned_xdr = builder.gen_xdr()
    except Exception as e:
        raise web.HTTPBadRequest(reason='Bad request, Please ensure parameters are valid.')

    tx_hash = builder.te.hash_meta()

    return unsigned_xdr.decode(), binascii.hexlify(tx_hash).decode()
