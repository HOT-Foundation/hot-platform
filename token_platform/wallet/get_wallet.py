from aiohttp import web
from stellar_base.address import Address as stellar_address
from stellar_base.utils import AccountNotExistError
from pprint import pprint
from functools import reduce 
from conf import settings


def format_balance(item):
    """Format wallet balances to dictionary"""
    asset = 'XLM' if item['asset_type'] is 'native' else item['asset_code']
    issuer = 'native' if item['asset_type'] is 'native' else item['asset_issuer']
    return {
        asset: {
            'balance': item['balance'],
            'issuer': issuer
        }
    }


def map_balance(account_balances):
    balanceList = list(map(format_balance, account_balances))
    balance = reduce((lambda x, y: {**x, **y}), balanceList)
    return balance


def format_signers(signers):
    return list(map(lambda signer: {'public_key': signer['public_key'], 'type': signer['type'], 'weight': signer['weight']}, signers))


async def get_wallet_from_request(request):
    wallet_address = request.match_info.get('wallet_address', "")
    return get_wallet(wallet_address)


async def get_wallet(wallet_address):
    wallet = stellar_address(address=wallet_address)
    try:
        wallet.get()
    except AccountNotExistError as ex:
        raise web.HTTPNotFound(text=str(ex))

    balances = map_balance(wallet.balances)
    signers = format_signers(wallet.signers)
    result = wallet_response(wallet_address, balances, wallet.thresholds, signers)
    return web.json_response(result)


def wallet_response(wallet_address, balances, thresholds, signers, host=settings['HOST']):
    return {
        "@url": '{}/wallet/{}'.format(host, wallet_address),
        "@id": wallet_address,
        "asset": balances,
        "thresholds": thresholds,
        "signers": signers
    }