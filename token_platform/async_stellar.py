from aiohttp import ClientSession, web
from dataclasses import dataclass
from conf import settings

HORIZON_URL = settings['HORIZON_URL']


# class Stellar:
#     def __init__(self, address: str, horizon: str=None, timeout: int=20):
#         self.address = address
#         horizon_url = horizon or HORIZON_URL
@dataclass
class Wallet:
    address: str
    balances: list
    sequence: str
    data: dict

async def get_wallet(address: str) -> dict:
    url = f'{HORIZON_URL}/accounts/{address}'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return Wallet(address=body['account_id'], balances=body['balances'], sequence=body['sequence'], data=body['data'])

async def get_transaction(transaction_hash: str) -> dict:
    url = f'{HORIZON_URL}/transactions/{transaction_hash}'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return body
