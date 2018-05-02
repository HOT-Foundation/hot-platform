from typing import Dict, List

from aiohttp import web
from conf import settings
from transaction.get_unsigned_transfer import build_unsigned_transfer
from transaction.transaction import (get_current_sequence_number, get_signers,
                                     get_threshold_weight)


async def get_presigned_tx_xdr_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request create account xdr and presigned transaction xdr"""
    body = await request.json()
    stellar_escrow_address = body.get('stellar_escrow_address', None)
    stellar_merchant_address = body.get('stellar_merchant_address', None)
    stellar_hotnow_address = body.get('stellar_hotnow_address', None)
    starting_balance = body.get('starting_balance', None)
    exp_date = body.get('expriring_date', None)
    cost_per_tx = body.get('cost_per_tx', None)

    result = await get_presigned_tx_xdr(
            stellar_escrow_address,
            stellar_merchant_address,
            stellar_hotnow_address,
            starting_balance,
            exp_date,
            cost_per_tx
        )

    return web.json_response(result)


async def get_presigned_tx_xdr(
    stellar_escrow_address:str,
    stellar_merchant_address:str,
    stellar_hotnow_address:str,
    starting_balance:int,
    exp_date:str,
    cost_per_tx:int
) -> Dict:
    """Get XDR presigned transaction of promote deal"""

    tx_count = int(starting_balance/cost_per_tx)
    sequence_number = await get_current_sequence_number(stellar_escrow_address)

    async def _get_unsigned_transfer(source_address: str, destination: str, amount: int, sequence:int = None) -> Dict:
        """Get unsigned transfer transaction and signers

            Args:
                source_address: Owner of operation
                destination_address: address of receiveing wallet
                amount: amount of money that would be transferred
                sequence: sequence number of escrow account
        """
        unsigned_xdr, tx_hash = build_unsigned_transfer(source_address, destination, amount, sequence=sequence)
        host: str = settings['HOST']
        result = {
            '@id': source_address,
            '@url': '{}/wallet/{}/transaction/transfer'.format(host, source_address),
            '@transaction_url': '{}/transaction/{}'.format(host, tx_hash),
            'unsigned_xdr': unsigned_xdr
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
