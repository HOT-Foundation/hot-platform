from aiohttp import web, web_request, web_response
from stellar_base.address import Address as stellar_address
from stellar_base.utils import AccountNotExistError
from pprint import pprint
from functools import reduce 
from conf import settings
from typing import Dict, List, Any, NewType, Union, Mapping

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
STELLAR_BALANCE = Dict[str, str]
STELLAR_BALANCES = List[Dict[str, str]]
BALANCE_RESPONSE = Dict[str, Dict[str, str]]
SIGNERS = List[Dict[str, str]]
THRESHOLDS = Dict[str, int]


async def get_wallet_from_request(request: web_request.Request) ->  web_response.Response:
    """AIOHttp Request wallet address to get wallet"""
    wallet_address = request.match_info.get('wallet_address', "")
    return await get_wallet(wallet_address)


async def get_wallet(wallet_address: str) -> web_response.Response:
    """Get wallet from stellar network"""

    def _map_balance(stellar_balances: STELLAR_BALANCES) -> BALANCE_RESPONSE:
        """Map wallet balances to dictionary"""
        balanceList = list(map(_format_balance, stellar_balances))
        balance = reduce((lambda x, y: {**x, **y}), balanceList)
        return balance

    def _format_balance(stellar_balance: STELLAR_BALANCE) -> BALANCE_RESPONSE:
        """Format wallet balances to dictionary"""
        asset = 'XLM' if stellar_balance['asset_type'] == 'native' else stellar_balance['asset_code']
        issuer = 'native' if stellar_balance['asset_type'] == 'native' else stellar_balance['asset_issuer']
        return {
            asset: {
                'balance': stellar_balance['balance'],
                'issuer': issuer
            }
        }

    def _format_signers(signers: SIGNERS) -> SIGNERS:
        """Format signers's wallet to dictionary is not include field key"""
        return list(map(lambda signer: {'public_key': signer['public_key'], 'type': signer['type'], 'weight': signer['weight']}, signers))

    wallet:stellar_address = stellar_address(address=wallet_address)
    try:
        wallet.get()
    except AccountNotExistError as ex:
        raise web.HTTPNotFound(text=str(ex))

    balances = _map_balance(wallet.balances)
    signers = _format_signers(wallet.signers)
    result = wallet_response(wallet_address, balances, wallet.thresholds, signers)
    return web.json_response(result)


def wallet_response(wallet_address: str, balances: BALANCE_RESPONSE, thresholds: THRESHOLDS, signers: SIGNERS, host:str=settings['HOST']) -> JSONType:
    """Format of wallet to dictionary"""
    return {
        "@url": '{}/wallet/{}'.format(host, wallet_address),
        "@id": wallet_address,
        "asset": balances,
        "thresholds": thresholds,
        "signers": signers
    }