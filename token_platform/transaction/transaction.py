from typing import Dict

from aiohttp import web, web_request, web_response
from stellar_base.horizon import horizon_livenet, horizon_testnet, Horizon
from stellar_base.transaction import Transaction
from stellar_base.transaction_envelope import TransactionEnvelope as Te
from conf import settings
from typing import Dict, List, Any, NewType, Union, Mapping, Optional
import copy

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


async def is_duplicate_transaction(transaction_hash: str) -> bool:
    """Check transaction is duplicate or not"""

    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    transaction = horizon.transaction(transaction_hash)
    id = transaction.get('id')
    return True if id else False

async def submit_transaction(xdr: bytes) -> Dict[str, str]:
    """Submit transaction into Stellar network"""
    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()

    try:
        response = horizon.submit(xdr)
    except Exception as e:
        msg = str(e)
        raise web.HTTPInternalServerError
    if response.get('status') == 400:
        msg = response.get('extras', {}).get('result_codes', {}).get('transaction', None)
        raise web.HTTPBadRequest(reason=msg)
    return response

async def get_next_sequence_number(wallet_address:str) -> int:
    """Get next sequence number of the wallet"""
    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    sequence = horizon.account(wallet_address).get('sequence')
    return sequence

async def get_transaction(tx_hash: str) -> web_response.Response:
    """Retrieve transaction detail from transaction hash

        Args:
        tx_hash: hash of transaction we are interested in.
    """

    def _format_transaction(tx_detail: Dict[str, str]) -> Dict[str, Union[str, int, List[Dict[str, str]]]]:
        """Format transaction detail in pattern dict"""
        return {
            "@id": tx_detail.get("id", None),
            "@url": "{}/transaction/{}".format(settings.get('HOST', None), tx_detail.get("id")),
            "paging_token": tx_detail.get("paging_token"),
            "ledger": tx_detail.get("ledger"),
            "created_at": tx_detail.get("created_at", None),
            "source_account": tx_detail.get("source_account", None),
            "source_account_sequence": tx_detail.get("source_account_sequence", None),
            "fee_paid": tx_detail.get("fee_paid", None),
            "signatures": tx_detail.get("signatures", None)
        }

    def _get_operation_data_of_transaction(tx_hash: str, horizon: Horizon) -> List[Dict[str, str]]:
        """Get operation list of transaction"""

        operations = copy.deepcopy(horizon.transaction_operations(tx_hash).get("_embedded").get("records"))

        for operation in operations:
            operation.pop("_links")

        return operations


    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    transaction = horizon.transaction(tx_hash)

    if transaction.get('status', None) == 404:
        raise web.HTTPNotFound(text=str(transaction.get('title', 'Resource not found')))

    tx_detail = _format_transaction(transaction)
    tx_detail["operations"] = _get_operation_data_of_transaction(tx_hash, horizon)

    return web.json_response(tx_detail)