from functools import reduce
from typing import Any, Dict, List, Union

import requests
from aiohttp import web
from stellar_base.builder import Builder
from stellar_base.utils import AccountNotExistError

from conf import settings
from wallet.wallet import get_wallet
from base64 import b64decode
from router import reverse

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
STELLAR_BALANCE = Dict[str, str]
STELLAR_BALANCES = List[STELLAR_BALANCE]
BALANCE_RESPONSE = Union[Dict[str, str], Dict]
SIGNERS = List[Dict[str, str]]
THRESHOLDS = Dict[str, int]


async def get_escrow_wallet_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request escrow wallet address to get escrow wallet"""
    escrow_address = request.match_info.get('escrow_address', "")
    escrow_wallet = await get_escrow_wallet_detail(escrow_address)
    return web.json_response(escrow_wallet)


async def get_escrow_wallet_detail(escrow_address: str) -> web.Response:
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
        return reduce(lambda asset, balance: {**asset, **_format_balance(balance)}, balances, {})

    def _format_data(data: Dict[str, str]) -> Dict:
        """ Decode base64 data """
        return {k: b64decode(v).decode('utf-8') for k, v in data.items()}

    wallet = await get_wallet(escrow_address)

    result: Dict[str, Any] = {
        '@id': escrow_address,
        '@url': f"{settings['HOST']}{reverse('escrow-address', escrow_address=escrow_address)}",
        'asset': _merge_balance(wallet.balances),
        'generate-wallet': f"{settings['HOST']}{reverse('escrow-generate-wallet', escrow_address=escrow_address)}",
        'data': _format_data(wallet.data)
    }

    return result
