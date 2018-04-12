from aiohttp import web
from wallet.get_wallet import get_wallet_from_request, build_create_wallet_transaction_from_request
from controller import handle

routes = [
    web.get('/', handle),
    web.get('/wallet/{wallet_address}', get_wallet_from_request),
    web.get('/wallet/{wallet_address}/create_wallet', build_create_wallet_transaction_from_request)
]