from aiohttp import web
from account.get_account import get_account 
from controller import handle

routes = [
    web.get('/', handle),
    web.get('/account/{account_address}', get_account),
]