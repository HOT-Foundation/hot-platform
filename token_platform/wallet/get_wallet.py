from aiohttp import web, web_request, web_response
from stellar_base.address import Address as StellarAddress
from stellar_base.utils import AccountNotExistError
from functools import reduce
from conf import settings
from typing import Dict, List, Any, NewType, Union, Mapping, Optional

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
STELLAR_BALANCE = Dict[str, str]
STELLAR_BALANCES = List[STELLAR_BALANCE]
BALANCE_RESPONSE = Union[Dict[str, str], Dict]
SIGNERS = List[Dict[str, str]]
THRESHOLDS = Dict[str, int]


async def get_wallet_from_request(request: web_request.Request) ->  web_response.Response:
    """AIOHttp Request wallet address to get wallet"""
    wallet_address = request.match_info.get('wallet_address', "")
    return await get_wallet(wallet_address)


async def get_wallet(wallet_address: str) -> web_response.Response:
    """Get wallet balances from stellar network"""

    def _format_balance(balance: STELLAR_BALANCE) -> BALANCE_RESPONSE:
        """Format balance in pattern dict {asset_code: balance}"""
        if balance['asset_type'] == 'native':
            return {'XLM': balance['balance']}
        elif balance['asset_code'] == settings['ASSET_CODE'] and balance['asset_issuer'] == settings['ISSUER']:
            return {settings['ASSET_CODE']: balance['balance']}
        return {}

    def _merge_balance(balances: STELLAR_BALANCES) -> Dict[str, str]:
        """Merge all balances to one Dict"""
        asset:Union[Dict, Dict[str, str]] = {}
        for balance in balances:
            asset.update(_format_balance(balance))
        return asset

    def _trusted_htkn(balances: STELLAR_BALANCES) -> Union[Dict, Dict[str, str]]:
        """Return URL for making trust HTKN"""
        if len(list(filter(lambda b: b.get('asset_code', None) == settings['ASSET_CODE'] and b.get('asset_issuer', None) == settings['ISSUER'], balances))) == 0:
            return {'trust': '{}/wallet/{}/transaction/change-trust'.format(settings['HOST'], wallet_address)}
        return {}


    wallet = StellarAddress(address=wallet_address)
    try:
        wallet.get()
    except AccountNotExistError as ex:
        raise web.HTTPNotFound(text=str(ex))

    result:Dict[str, Any] = {
        '@id':wallet.address,
        '@url': '{}/wallet/{}'.format(settings['HOST'], wallet_address),
        'asset': _merge_balance(wallet.balances)
    }

    result.update(_trusted_htkn(wallet.balances))

    return web.json_response(result)


