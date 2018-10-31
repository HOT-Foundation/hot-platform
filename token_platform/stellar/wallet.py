from urllib.parse import urlencode

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


async def get_stellar_wallet(wallet_address: str) -> Wallet:
    """Get wallet detail from Stellar network"""

    url = f'{HORIZON_URL}/accounts/{wallet_address}'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return Wallet(
                body['account_id'],
                body['balances'],
                body['sequence'],
                body['data'],
                body['signers'],
                body['thresholds'],
                body['flags'],
            )  # type: ignore


async def get_transaction(transaction_hash: str) -> dict:
    url = f'{HORIZON_URL}/transactions/{transaction_hash}'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return body


async def get_transaction_by_wallet(wallet_address: str, **kwargs) -> dict:
    '''
        Get all transactions of the wallet

        Args:
            wallet_address: wallet's address.
            limit: number of transactions which want to retreive.
            sort[asc, desc]: order of result (default asc).
            offset: starting transaction for searching.
    '''
    url = f'{HORIZON_URL}/accounts/{wallet_address}/transactions?'

    sort = kwargs.get('sort', 'asc')
    if not sort.lower() in {'asc', 'desc'}:
        raise ValueError('sort parameter is wrong.')

    limit = kwargs.get('limit')
    offset = kwargs.get('offset')

    query = {'order': sort}
    if limit:
        query['limit'] = limit

    if sort:
        query['order'] = sort

    if offset:
        query['cursor'] = offset

    completed_url = url + urlencode(query)
    async with ClientSession() as session:
        async with session.get(completed_url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return body.get('_embedded').get('records')


async def get_wallet_effect(wallet_address: str, sort: str = 'asc', limit: int = None, offset: str = None) -> dict:
    """Get effect occured on certain wallet"""

    if not sort.lower() in {'asc', 'desc'}:
        raise ValueError('sort parameter is wrong.')

    url = f'{HORIZON_URL}/accounts/{wallet_address}/effects?'
    query = {'order': sort}

    if limit:
        query['limit'] = limit

    if offset:
        query['cursor'] = offset

    completed_url = url + urlencode(query)

    async with ClientSession() as session:
        async with session.get(completed_url) as resp:
            body = await resp.json()
            if resp.status == 400:
                raise web.HTTPBadRequest(reason=body.get('detail'))
            if resp.status == 404:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return body


async def get_operations_of_transaction(transaction_hash: str, **kwargs) -> dict:
    '''
        Get operations of a transaction by transaction hash

        Args:
            transaction hash: transaction hash.
            limit: number of transactions which want to retreive.
            sort[asc, desc]: order of result (default asc).
            offset: starting transaction for searching.
    '''

    url = f'{HORIZON_URL}/transactions/{transaction_hash}/operations?'

    sort = kwargs.get('sort', 'asc')
    if not sort.lower() in {'asc', 'desc'}:
        raise ValueError('sort parameter is wrong.')

    limit = kwargs.get('limit')
    offset = kwargs.get('offset')

    query = {'order': sort}
    if limit:
        query['limit'] = limit

    if sort:
        query['order'] = sort

    if offset:
        query['cursor'] = offset

    completed_url = url + urlencode(query)
    async with ClientSession() as session:
        async with session.get(completed_url) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise web.HTTPNotFound(reason=body.get('detail'))
            return body.get('_embedded').get('records')
