from aiohttp import web


async def handle(request):
    response = {
      'root': '/',
      'wallet': '/wallet/{wallet_address}',
      'generate-wallet': '/wallet/{wallet_address}/generate-wallet',
      'wallet-sequence-number': '/wallet/{wallet_address}/transaction/current-sequence',
      'wallet-generate-payment': '/wallet/{wallet_address}/generate-payment',
      'wallet-change-trust': '/wallet/{wallet_address}/transaction/change-trust',
      'escrow': '/escrow/{escrow_address}',
      'escrow-generate-wallet': '/escrow/{escrow_address}/generate-wallet',
      'escrow-generate-presigned-transactions': '/escrow/{escrow_address}/generate-presigned-transections',
      'transaction': '/transaction/{transaction_hash}',
    }
    return web.json_response(response)
