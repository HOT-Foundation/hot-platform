from aiohttp import web
from stellar_base.address import Address
from stellar_base.utils import AccountNotExistError
from pprint import pprint
from functools import reduce 
from conf import settings

def format_balance(item):
    balance = {}
    if item['asset_type'] == 'native':
        result = {
            'XLM': { 
                'balance': item['balance'],
                'issuer': 'native'
            }
        }
        return result
    balance[item['asset_code']] = {
        'balance': item['balance'],
        'issuer': item['asset_issuer']
    }
    return balance


def map_balance(balances):
    balanceList = list(map(format_balance, balances))
    balance = reduce((lambda x, y: {**x, **y}), balanceList)
    return balance


def format_signers(signer):
    signer.pop('key', None)
    return signer


async def get_account(request):
    account_address = request.match_info.get('account_address', "")
    account = Address(address=account_address)
    account.get()

    balances = map_balance(account.balances)
    signers = list(map(format_signers, account.signers))
    result = {
        "@url": '{}/account/{}'.format(settings['HOST'], account_address),
        "@id": account_address,
        "asset": balances,
        "thresholds": account.thresholds,
        "signers": signers
    }

    return web.json_response(result)