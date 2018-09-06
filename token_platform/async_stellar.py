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

async def get_wallet(address: str) -> Wallet:
    url = f'{HORIZON_URL}/accounts/{address}'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return Wallet(body['account_id'], body['balances'], body['sequence'], body['data'], body['signers']) # type: ignore

async def get_transaction(transaction_hash: str) -> dict:
    url = f'{HORIZON_URL}/transactions/{transaction_hash}'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return body
