from aiohttp import web
from transaction.generate_merge_transaction import generate_merge_transaction
from router import reverse

async def post_close_joint_wallet_from_request(request: web.Request) -> web.Response:
    wallet_address = request.match_info['wallet_address']
    body = await request.json()

    resp = await generate_merge_transaction(wallet_address, body['parties'])
    resp['@id'] = reverse('close-joint-wallet', wallet_address=wallet_address)

    return web.json_response(resp)
