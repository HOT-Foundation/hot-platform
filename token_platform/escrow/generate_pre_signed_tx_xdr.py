from typing import Dict, List

from aiohttp import web
from conf import settings
from transaction.get_unsigned_transfer import build_unsigned_transfer
from transaction.transaction import (get_current_sequence_number, get_signers,
                                     get_threshold_weight)


async def get_presigned_tx_xdr_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request create account xdr and presigned transaction xdr"""
    body = await request.json()
    try:
        stellar_escrow_address = body['stellar_escrow_address']
        stellar_hotnow_address = body['stellar_hotnow_address']
        starting_balance = body['starting_balance']
        cost_per_tx = body['cost_per_tx']
    except KeyError as context:
        msg = "Parameter {} not found. Please ensure parameters is valid.".format(str(context))
        raise web.HTTPBadRequest(reason=str(msg))

    result = await get_presigned_tx_xdr(
            stellar_escrow_address,
            stellar_hotnow_address,
            starting_balance,
            cost_per_tx
        )

    return web.json_response(result)


async def get_presigned_tx_xdr(
    stellar_escrow_address:str,
    stellar_hotnow_address:str,
    starting_balance:int,
    cost_per_tx:int
) -> Dict:
    """Get XDR presigned transaction of promote deal"""

    tx_count = int(starting_balance/cost_per_tx)
    sequence_number = await get_current_sequence_number(stellar_escrow_address)

    async def _get_unsigned_transfer(
        source_address: str,
        destination: str,
        amount: int,
        sequence:int = None
    ) -> Dict:
        """Get unsigned transfer transaction and signers

            Args:
                source_address: Owner of operation
                destination_address: address of receiveing wallet
                amount: amount of money that would be transferred
                sequence: sequence number of escrow account
        """
        unsigned_xdr, tx_hash = build_unsigned_transfer(
            source_address, destination, amount, sequence=sequence
        )
        host: str = settings['HOST']
        result = {
            '@id': source_address,
            '@url': '{}/wallet/{}/transaction/transfer'.format(host, source_address),
            '@transaction_url': '{}/transaction/{}'.format(host, tx_hash),
            'unsigned_xdr': unsigned_xdr,
            'sequence': sequence + 1
        }
        return result

    presigneds = []
    for i in range(0, tx_count):
        presigneds.append(await _get_unsigned_transfer(
            stellar_escrow_address,
            stellar_hotnow_address,
            cost_per_tx,
            sequence=int(sequence_number)+i))

    result = {
        'min_signer': await get_threshold_weight(stellar_escrow_address, 'payment'),
        'signers': await get_signers(stellar_escrow_address),
        'xdr': presigneds
    }
    return result
