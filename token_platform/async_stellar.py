from aiohttp import ClientSession, web
from conf import settings
from dataclasses import dataclass

HORIZON_URL = settings['HORIZON_URL']

@dataclass
class Wallet:
    address: str
    balances: list
    sequence: str
    data: dict
    signers: list
    thresholds: dict
    flags: dict

async def get_wallet(address: str) -> Wallet:
    """Get wallet detail from Stellar network"""

    url = f'{HORIZON_URL}/accounts/{address}'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return Wallet(body['account_id'], body['balances'], body['sequence'], body['data'], body['signers'], body['thresholds'], body['flags']) # type: ignore

async def get_transaction(transaction_hash: str) -> dict:
    url = f'{HORIZON_URL}/transactions/{transaction_hash}'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return body

async def get_wallet_effect(address: str, sort: str='asc', limit: int=None, offset: str=None) -> dict:
    """Get effect occured on certain wallet"""

    if not sort.lower() in {'asc', 'desc'}:
        raise ValueError('sort parameter is wrong.')

    url = f'{HORIZON_URL}/accounts/{address}/effects?order={sort}'

    if limit:
        url += f'&limit={limit}'

    if offset:
        url += f'&cursor={offset}'

    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status == 400:
                raise web.HTTPBadRequest(reason=body.get('detail'))
            if resp.status == 404:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return body