from decimal import Decimal
from json import JSONDecodeError
from typing import Dict, List

from aiohttp import web
from conf import settings
from escrow.get_escrow_wallet import get_escrow_wallet_detail
from router import reverse
from transaction.generate_payment import build_unsigned_transfer
from transaction.transaction import (get_current_sequence_number, get_signers,
                                     get_threshold_weight)


async def get_presigned_tx_xdr_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request create account xdr and presigned transaction xdr"""

    try:
        json_response = await request.json()
    except JSONDecodeError:
        raise web.HTTPBadRequest(reason='Bad request, JSON data missing.')

    escrow_address = request.match_info.get("escrow_address")
    transaction_source_address = json_response.get('transaction_source_address', escrow_address)
    escrow = await get_escrow_wallet_detail(escrow_address)

    destination_address = escrow["data"]["destination_address"]
    cost_per_tx = escrow["data"]["cost_per_transaction"]
    balance = escrow['asset'][settings['ASSET_CODE']]

    result = await get_presigned_tx_xdr(
        escrow_address,
        transaction_source_address,
        destination_address,
        Decimal(balance),
        Decimal(cost_per_tx)
    )

    return web.json_response(result)


async def get_presigned_tx_xdr(
    escrow_address:str,
    transaction_source_address:str,
    destination_address:str,
    starting_balance:Decimal,
    cost_per_tx:Decimal
) -> Dict:
    """Get XDR presigned transaction of promote deal"""

    tx_count = int(starting_balance/cost_per_tx)
    sequence_number = await get_current_sequence_number(escrow_address)

    async def _get_unsigned_transfer(
        source_address: str,
        transaction_source_address,
        destination: str,
        amount: Decimal,
        sequence:int
    ) -> Dict:
        """Get unsigned transfer transaction and signers

            Args:
                source_address: Owner of operation
                destination: address of receiving wallet
                amount: amount of money that would be transferred
                sequence: sequence number of escrow account
        """

        unsigned_xdr, tx_hash = await build_unsigned_transfer(
            transaction_source_address, source_address, destination, amount, Decimal(0), None, sequence=sequence
        )
        host: str = settings['HOST']
        result = {
            '@id': reverse('transaction', transaction_hash=tx_hash),
            'xdr': unsigned_xdr,
            'sequence_number': sequence + 1,
            'transaction_hash': tx_hash
        }
        return result

    presigneds = []
    for i in range(0, tx_count):
        presigneds.append(await _get_unsigned_transfer(
            escrow_address,
            transaction_source_address,
            destination_address,
            cost_per_tx,
            sequence=int(sequence_number)+i))

    result = {
        'min_signer': await get_threshold_weight(escrow_address, 'payment'),
        'signers': await get_signers(escrow_address),
        'xdr': presigneds
    }
    return result
