from aiohttp import web
from account.get_account import get_account 
from controller import handle

routes = [
    web.get('/', get_account),
    web.get('/account/{account_address}', get_account),
]