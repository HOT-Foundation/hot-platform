from decimal import Decimal
from typing import Dict, List

from aiohttp import web
from conf import settings
from transaction.get_unsigned_transfer import build_unsigned_transfer
from transaction.transaction import (get_current_sequence_number, get_signers,
                                     get_threshold_weight)
from wallet.wallet import get_wallet


async def get_presigned_tx_xdr_from_request(request: web.Request) -> web.Response:
    """AIOHttp Request create account xdr and presigned transaction xdr"""
    escrow_address = request.match_info.get("escrow_address")
    escrow = await get_wallet(escrow_address)
    try:
        destination_address = escrow.data["stellar_destination_address"]
        starting_balance = escrow.data["starting_balance"]
        cost_per_tx = escrow.data["cost_per_tx"]
    except KeyError as e:
        msg = "Parameter {} not found. Please ensure parameters is valid.".format(str(e))
        raise web.HTTPBadRequest(reason=str(msg))

    balance = list(filter(lambda balance: balance['asset_type'] != 'native' and balance['asset_code'] == settings['ASSET_CODE'] and balance['asset_issuer'] == settings['ISSUER'], escrow.balances))[0]['balance']

    result = await get_presigned_tx_xdr(
        escrow_address,
        destination_address,
        Decimal(balance),
        Decimal(cost_per_tx)
    )

    return web.json_response(result)


async def get_presigned_tx_xdr(
    stellar_escrow_address:str,
    stellar_destination_address:str,
    starting_balance:Decimal,
    cost_per_tx:Decimal
) -> Dict:
    """Get XDR presigned transaction of promote deal"""

    tx_count = int(starting_balance/cost_per_tx)
    sequence_number = await get_current_sequence_number(stellar_escrow_address)

    async def _get_unsigned_transfer(
        source_address: str,
        destination: str,
        amount: Decimal,
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
            'xdr': unsigned_xdr,
            'sequence_number': sequence + 1
        }
        return result

    presigneds = []
    for i in range(0, tx_count):
        presigneds.append(await _get_unsigned_transfer(
            stellar_escrow_address,
            stellar_destination_address,
            cost_per_tx,
            sequence=int(sequence_number)+i))

    result = {
        'min_signer': await get_threshold_weight(stellar_escrow_address, 'payment'),
        'signers': await get_signers(stellar_escrow_address),
        'xdr': presigneds
    }
    return result
