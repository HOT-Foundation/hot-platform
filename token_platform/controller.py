from aiohttp import web


async def handle(request):
    response = {
      "wallet": "http://localhost/wallet/:wallet_address",
      "escrow": "http://localhost/escrow/:escrow_address"
    }
    return web.json_response(response)
