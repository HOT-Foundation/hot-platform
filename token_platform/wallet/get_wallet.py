from aiohttp import web, web_request
from stellar_base.address import Address as stellar_address
from stellar_base.utils import AccountNotExistError
from pprint import pprint
from functools import reduce 
from conf import settings
from typing import Dict, List, Any, overload


def format_balance(stellar_balance: object) -> object:
    """Format wallet balances to dictionary"""
    asset = 'XLM' if stellar_balance['asset_type'] == 'native' else stellar_balance['asset_code']
    issuer = 'native' if stellar_balance['asset_type'] == 'native' else stellar_balance['asset_issuer']
    return {
        asset: {
            'balance': stellar_balance['balance'],
            'issuer': issuer
        }
    }


def map_balance(stellar_balances: List[object]) -> object:
    """Map wallet balances to dictionary"""
    balanceList = list(map(format_balance, stellar_balances))
    balance = reduce((lambda x, y: {**x, **y}), balanceList)
    return balance


def format_signers(signers: List[object]) -> List[object]:
    """Format signers's wallet to dictionary is not include field key"""
    return list(map(lambda signer: {'public_key': signer['public_key'], 'type': signer['type'], 'weight': signer['weight']}, signers))


async def get_wallet_from_request(request: web_request.Request) -> object:
    """AIOHttp Request wallet address to get wallet"""
    wallet_address = request.match_info.get('wallet_address', "")
    return await get_wallet(wallet_address)


async def get_wallet(wallet_address: str) -> object:
    """Get wallet from stellar network"""
    wallet = stellar_address(address=wallet_address)
    try:
        wallet.get()
    except AccountNotExistError as ex:
        raise web.HTTPNotFound(text=str(ex))

    balances = map_balance(wallet.balances)
    signers = format_signers(wallet.signers)
    result = wallet_response(wallet_address, balances, wallet.thresholds, signers)
    return web.json_response(result)


def wallet_response(wallet_address: str, balances: object, thresholds: object, signers: object, host:str=settings['HOST']):
    """Format of wallet to dictionary"""
    return {
        "@url": '{}/wallet/{}'.format(host, wallet_address),
        "@id": wallet_address,
        "asset": balances,
        "thresholds": thresholds,
        "signers": signers
    }