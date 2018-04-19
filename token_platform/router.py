from aiohttp import web
from wallet.get_wallet import get_wallet_from_request
from wallet.get_create_wallet import get_create_wallet_from_request
from wallet.get_next_tx_sequence import get_next_tx_sequence_from_request
from transaction.get_transaction import get_transaction_from_request
from transaction.put_transaction import put_transaction_from_request
from controller import handle

routes = [
    web.get('/', handle),
    web.get('/wallet/{wallet_address}', get_wallet_from_request),
    web.get('/wallet/{wallet_address}/create-wallet', get_create_wallet_from_request),
    web.get('/wallet/{wallet_address}/transaction/next-sequence', get_next_tx_sequence_from_request),
    web.get('/transaction/{transaction_hash}', get_transaction_from_request),
    web.put('/transaction/{transaction_hash}', put_transaction_from_request),
]