from typing import Dict, Tuple, Any, List
from stellar_base.builder import Builder
from escrow.get_escrow_wallet import get_escrow_wallet_detail
from router import reverse
from decimal import Decimal
from conf import settings
from aiohttp import web
from stellar_base.horizon import Horizon

import binascii


async def generate_merge_transaction(transaction_source_address: str, wallet_address: str, parties_wallet: List=None) -> Dict:
    """ Generate close escrow wallet function by escrow address then get escrow wallet detail by that address then build generate for return xdr and transaction hash

    Args;
        escrow_address :  Address of escrow wallet
        parties_walles : list of provider address and amount for payback
    return Dict type
        escrow_address : Address of escrow wallet
        transaction_url : Url for GET transaction detail
        signers : Array of signers use for sign xdr
        xdr : Xdr for sign
        transaction_hash: Transaction hash number for get transaction detail
    """
    wallet_detail = await get_escrow_wallet_detail(wallet_address)

    unsigned_xdr, tx_hash = await build_generate_merge_transaction(transaction_source_address, wallet_detail, parties_wallet)

    return {
        'wallet_address' : wallet_address,
        'transaction_url' : reverse('transaction', transaction_hash=tx_hash),
        'signers' : wallet_detail['signers'],
        'xdr' : unsigned_xdr,
        'transaction_hash' : tx_hash
    }


async def build_generate_merge_transaction(transaction_source_address: str, wallet_detail: Dict, parties_wallet: List=None) -> Tuple[Any, str]:
    """ Builder transaction close escrow wallet by payment remaining HTKN from escrow_wallet to provider_wallet and merge account from escrow_wallet to creator_wallet, Finally, return xdr and transaction_hash

    Args:
        escrow_wallet: escrow wallet response from get_escrow_wallet_detail
        parties_walles : list of provider address and amount for payback
    """

    wallet_address = wallet_detail['escrow_address']
    wallet_data = wallet_detail['data']
    creator_address = wallet_data['creator_address'] if wallet_data and 'creator_address' in wallet_data.keys() else await get_creator_address(wallet_address)

    builder = Builder(address=transaction_source_address, horizon=settings['HORIZON_URL'])

    if not parties_wallet:
        parties_wallet = await generate_parties_wallet(wallet_detail)

    balance = Decimal(wallet_detail['asset'][settings['ASSET_CODE']])
    if not await is_match_balance(parties_wallet, balance):
        raise web.HTTPBadRequest(reason='Total amount not match wallet balance')

    await build_payment_operation(builder, wallet_address, parties_wallet)
    await build_remove_trustlines_operation(builder, wallet_address)
    await build_remove_manage_data_operation(builder, wallet_address, wallet_data.keys())
    await build_account_merge_operation(builder, wallet_address, creator_address)

    try:
        xdr = builder.gen_xdr()
    except Exception as e:
        raise web.HTTPBadRequest(reason='Bad request, Please ensure parameters are valid.')

    tx_hash = builder.te.hash_meta()

    return xdr.decode(), binascii.hexlify(tx_hash).decode()


async def get_creator_address(wallet_address: str) -> str:
    ''' Get creator address from Stellar via Horizon account operations and then return that address

    Args:
        wallet_address: address for search creator address  '''
    horizon = Horizon(settings['HORIZON_URL'])
    result = horizon.account_operations(wallet_address, params={'limit' : 1, 'order' : 'asc'}).get('_embedded').get('records')[0]
    return result['source_account']


async def generate_parties_wallet(wallet_detail: Dict) -> List:
    ''' Generate parties wallet from wallet detail and then return list of address provider and amount of payback

    Args:
        wallet_detail: wallet detail dict it's result of escrow.get_escrow_wallet.get_escrow_wallet_detail '''
    parties_wallet = []
    wallet = {
        'address' : wallet_detail['data']['provider_address'],
        'amount' : wallet_detail['asset'][settings['ASSET_CODE']]
    }
    parties_wallet.append(wallet)
    return parties_wallet


async def is_match_balance(parties_wallet: List, balance: Decimal) -> bool:
    ''' Check match balance between total payback amount of list provider and wallet amount and then return True of False

    Args:
        parties_wallet: list of  provider
        balance: balance of wallet'''
    amount: Decimal = Decimal(0)

    for wallet in parties_wallet:
        amount += Decimal(wallet['amount'])

    return amount == balance


async def build_payment_operation(builder: Builder, source: str, parties_wallet: List):

    for wallet in parties_wallet:
        destination = wallet['address']
        amount = Decimal(wallet['amount'])
        if amount > 0:
            builder.append_payment_op(destination=destination, amount=amount, asset_type=settings['ASSET_CODE'], asset_issuer=settings['ISSUER'], source=source)


async def build_remove_trustlines_operation(builder: Builder, source: str):
    builder.append_trust_op(settings['ISSUER'], settings['ASSET_CODE'], limit=0, source=source)


async def build_remove_manage_data_operation(builder: Builder, source: str, list_name: List):
    for name in list_name:
        builder.append_manage_data_op(name, None, source=source)


async def build_account_merge_operation(builder: Builder, source: str, destination: str):
    builder.append_account_merge_op(destination=destination, source=source)
