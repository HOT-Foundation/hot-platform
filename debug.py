from escrow.post_close_escrow_wallet import build_generate_close_escrow_wallet_transaction
from escrow.get_escrow_wallet import get_escrow_wallet_detail

async def debug():
    address = 'GCUMOLZSG2ITHHDAHAO45OVDJXP47FNAW2ZTDOTZK7KPFESFQ7B3CLWJ'
    escrow_wallet = await get_escrow_wallet_detail(address)
    res = await build_generate_close_escrow_wallet_transaction(escrow_wallet)
    print(res)

import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(debug())
