from aiohttp import web
from wallet.get_wallet import get_wallet_from_request
from controller import handle

routes = [
    web.get('/', handle),
    web.get('/wallet/{wallet_address}', get_wallet_from_request),
]