from aiohttp import web
from stellar_base.builder import Builder
from conf import settings
from typing import Tuple, Any, Dict
from decimal import Decimal
from router import reverse
from transaction.generate_merge_transaction import generate_merge_transaction

import binascii

async def post_close_escrow_wallet_from_request(request: web.Request) -> web.Response:
    """ AIOHTTP Request create close escrow wallet xdr """
    escrow_address = request.match_info['escrow_address']
    body = await request.json()
    transaction_source_address = body['transaction_source_address']

    result = await generate_merge_transaction(transaction_source_address, escrow_address)
    result['@id'] = reverse('close-escrow-wallet', escrow_address=escrow_address)

    return web.json_response(result)


