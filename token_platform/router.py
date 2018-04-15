from aiohttp import web
from wallet.get_wallet import get_wallet_from_request
from wallet.get_create_wallet import get_create_wallet_from_request
from controller import handle

routes = [
    web.get('/', handle),
    web.get('/wallet/{wallet_address}', get_wallet_from_request),
    web.get('/wallet/{wallet_address}/create-wallet', get_create_wallet_from_request)
]