from aiohttp import web
from controller import handle
# from escrow.generate_pre_signed_tx_xdr import get_presigned_tx_xdr_from_request
# from escrow.get_escrow_wallet import get_escrow_wallet_from_request
# from escrow.post_generate_escrow_wallet import \
#     post_generate_escrow_wallet_from_request
# from joint_wallet.generate_joint_wallet import post_generate_joint_wallet
# from transaction.generate_payment import generate_payment_from_request
# from transaction.get_transaction import get_transaction_from_request, get_transaction_hash_from_request
# from transaction.get_unsigned_change_trust import \
#     get_unsigned_change_trust_from_request
# from transaction.put_transaction import put_transaction_from_request
# from wallet.get_current_tx_sequence import get_current_tx_sequence_from_request
# from wallet.get_wallet import get_wallet_from_request
# from wallet.post_generate_wallet import post_generate_wallet_from_request

# routes = [
#     web.get('/', handle),

#     web.get('/wallet/{wallet_address}', get_wallet_from_request),
#     web.post('/wallet/{wallet_address}/generate-wallet', post_generate_wallet_from_request),
#     web.post('/wallet/{wallet_address}/generate-payment', generate_payment_from_request),
#     web.post('/wallet/{wallet_address}/generate-joint-wallet', post_generate_joint_wallet),
#     web.get('/wallet/{wallet_address}/transaction/current-sequence', get_current_tx_sequence_from_request),
#     web.get('/wallet/{wallet_address}/transaction/change-trust', get_unsigned_change_trust_from_request),
#     web.get('/wallet/{wallet_address}/get-transaction-hash', get_transaction_hash_from_request),

#     web.get('/escrow/{escrow_address}', get_escrow_wallet_from_request),
#     web.post('/escrow/{escrow_address}/generate-wallet', post_generate_escrow_wallet_from_request),
#     web.post('/escrow/{escrow_address}/generate-presigned-transections', get_presigned_tx_xdr_from_request),

#     web.get('/transaction/{transaction_hash}', get_transaction_from_request),
#     web.put('/transaction/{transaction_hash}', put_transaction_from_request),
# ]

ROUTER =  {
    "root" : {
        "url" : "/",
        "GET" : "controller.handle"
    },
    "wallet-address" : {
        "url" : "/wallet/{wallet_address}",
        "GET" : "wallet.get_wallet.get_wallet_from_request"
    },
    "generate-wallet" : {
        "url" : "/wallet/{wallet_address}/generate-wallet",
        "POST" : "wallet.post_generate_wallet.post_generate_wallet_from_request"
    },
    "generate-payment" : {
        "url" : "/wallet/{wallet_address}/generate-payment",
        "POST" : "transaction.generate_payment.generate_payment_from_request"
    },
    "generate-joint-wallet" : {
        "url" : "/wallet/{wallet_address}/generate-joint-wallet",
        "POST" : "joint_wallet.generate_joint_wallet.post_generate_joint_wallet"
    },
    "current-sequence" : {
        "url" : "/wallet/{wallet_address}/transaction/current-sequence",
        "GET" : "wallet.get_current_tx_sequence.get_current_tx_sequence_from_request"
    },
    "change-trust" : {
        "url" : "/wallet/{wallet_address}/transaction/change-trust",
        "GET" : "transaction.get_unsigned_change_trust.get_unsigned_change_trust_from_request"
    },
    "get-transaction-hash" : {
        "url" : "/wallet/{wallet_address}/get-transaction-hash",
        "GET" : "transaction.get_transaction.get_transaction_hash_from_request"
    },
    "escrow-address" : {
        "url" : "/escrow/{escrow_address}",
        "GET" : "escrow.get_escrow_wallet.get_escrow_wallet_from_request"
    },
    "escrow-generate-wallet" : {
        "url" : "/escrow/{escrow_address}/generate-wallet",
        "POST" : "escrow.post_generate_escrow_wallet.post_generate_escrow_wallet_from_request"
    },
    "generate-presigned-transections" : {
        "url" : "/escrow/{escrow_address}/generate-presigned-transections",
        "POST" : "escrow.generate_pre_signed_tx_xdr.get_presigned_tx_xdr_from_request"
    },
    "transaction" : {
        "url" : "/transaction/{transaction_hash}",
        "GET" : "transaction.get_transaction.get_transaction_from_request",
        "PUT" : "transaction.put_transaction.put_transaction_from_request"
    }
}

def generate_routes() -> list:
    routes = []
    for key, value in ROUTER.items():

        if 'GET' in value:
            handler = value['GET']
            routes.append(web.get(value['url'], object_at_end_of_path(handler), name=f'get-{key}'))

        if 'PUT' in value:
            handler = value['PUT']
            routes.append(web.put(value['url'], object_at_end_of_path(handler), name=f'put-{key}'))

        if 'POST' in value:
            handler = value['POST']
            routes.append(web.post(value['url'], object_at_end_of_path(handler), name=f'post-{key}'))
    return routes


def reverse(name: str, **kwargs) -> str:
    return ROUTER[name]['url'].format(**kwargs)


def object_at_end_of_path(path):
    """Attempt to return the Python object at the end of the dotted
    path by repeated imports and attribute access.
    """
    access_path = path.split('.')
    module = None
    for index in range(1, len(access_path)):
        try:
            # import top level module
            module_name = '.'.join(access_path[:-index])
            module = __import__(module_name)
        except ImportError:
            continue
        else:
            for step in access_path[1:-1]:  # walk down it
                module = getattr(module, step)
            break
    if module:
        return getattr(module, access_path[-1])
    else:
        return globals()['__builtins__'][path]
