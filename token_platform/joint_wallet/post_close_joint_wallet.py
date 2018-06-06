from aiohttp import web
from transaction.generate_merge_transaction import generate_merge_transaction
from router import reverse

async def post_close_joint_wallet_from_request(request: web.Request) -> web.Response:
    wallet_address = request.match_info['wallet_address']
    body = await request.json()
    parties = body['parties']
    transaction_source_address = body['transaction_source_address']

    resp = await generate_merge_transaction(wallet_address, parties, transaction_source_address)
    resp['@id'] = reverse('close-joint-wallet', wallet_address=wallet_address)

    return web.json_response(resp)
