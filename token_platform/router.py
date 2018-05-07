from aiohttp import web

from controller import handle
from escrow.generate_pre_signed_tx_xdr import get_presigned_tx_xdr_from_request
from escrow.get_create_escrow_wallet import create_escrow_wallet_from_request
from transaction.get_transaction import get_transaction_from_request
from transaction.get_unsigned_change_trust import \
    get_unsigned_change_trust_from_request
from transaction.get_unsigned_transfer import \
    get_unsigned_transfer_from_request
from transaction.put_transaction import put_transaction_from_request
from wallet.post_generate_wallet import post_generate_wallet_from_request
from wallet.get_current_tx_sequence import get_current_tx_sequence_from_request
from wallet.get_wallet import get_wallet_from_request
from escrow.get_escrow_wallet import get_escrow_wallet_from_request


routes = [
    web.get('/', handle),
    web.post('/create-escrow', create_escrow_wallet_from_request),
    web.post('/escrow/{escrow_address}/genarate-presigned-transections', get_presigned_tx_xdr_from_request),
    web.get('/wallet/{wallet_address}', get_wallet_from_request),
    web.post('/wallet/{wallet_address}/generate-wallet', post_generate_wallet_from_request),
    web.get('/wallet/{wallet_address}/transaction/current-sequence', get_current_tx_sequence_from_request),
    web.get('/wallet/{wallet_address}/transaction/transfer', get_unsigned_transfer_from_request),
    web.get('/wallet/{wallet_address}/transaction/change-trust', get_unsigned_change_trust_from_request),
    web.get('/transaction/{transaction_hash}', get_transaction_from_request),
    web.put('/transaction/{transaction_hash}', put_transaction_from_request),
    web.get('/escrow/{escrow_address}', get_escrow_wallet_from_request),
]
