from aiohttp import web
from stellar_base.address import Address as stellar_address
from stellar_base.utils import AccountNotExistError
from pprint import pprint
from functools import reduce 
from conf import settings

def format_balance(item):
    """Format wallet balances to dictionary"""
    if item['asset_type'] == 'native':
        return {
            'XLM': { 
                'balance': item['balance'],
                'issuer': 'native'
            }
        }
    return {
        item['asset_code']: {
            'balance': item['balance'],
            'issuer': item['asset_issuer']
        }
    }
    
# balances -> account_balances
def map_balance(balances):
    """
     sould have comment every function and class
     doc_string
    """
    balanceList = list(map(format_balance, balances))
    balance = reduce((lambda x, y: {**x, **y}), balanceList)
    return balance

# don't destroy parameter
# copy or construct new
def format_signers(signers):
    # return map(lambda y: {''})
    signer.pop('key', None)
    return signer

async def get_wallet_from_request(request):
    wallet_address = request.match_info.get('wallet_address', "")
    return get_wallet(wallet_address)


async def get_wallet(wallet_address):
    # wallet_address = request.match_info.get('wallet_address', "")
    # stellar.Address
    wallet = stellar_address(address=wallet_address)
    try:
        wallet.get()
    except AccountNotExistError as ex:
        raise web.HTTPNotFound(text=str(ex))

    balances = map_balance(wallet.balances)
    signers = format_signers(wallet.signers)
    result = wallet_response(wallet_address, balances, thresholds, signers)
    return web.json_response(result)


def wallet_response(wallet_address, balances, thresholds, signers, host=settings['HOST']):
    return {
        "@url": '{}/wallet/{}'.format(host, wallet_address),
        "@id": wallet_address,
        "asset": balances,
        "thresholds": thresholds,
        "signers": signers
    }