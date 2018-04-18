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
    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    transaction = horizon.transaction(transaction_hash)
    id = transaction.get('id')
    return True if id else False

async def submit_transaction(xdr: bytes) -> Dict[str, str]:
    horizon = horizon_livenet() if settings['STELLAR_NETWORK'] == 'PUBLIC' else horizon_testnet()
    try:
        response = horizon.submit(xdr)
    except Exception:
        raise web.HTTPInternalServerError
    if response['status'] == 400:
        raise web.HTTPBadRequest
    if response['status'] != 200:
        raise web.HTTPInternalServerError
    return response


async def put_transaction_from_request(request: web.Request) -> web.Response:
    signed_xdr = await request.text()
    tx_hash = request.match_info['transaction_hash']

    if not signed_xdr or not tx_hash:
        raise web.HTTPBadRequest(reason='transaction fail, please check your parameter.')

    result = {'message': 'transaction success.'}

    if await is_duplicate_transaction(tx_hash):
        raise web.HTTPBadRequest(reason='Duplicate transaction.')

    response = await submit_transaction(signed_xdr)
    return web.json_response(result)


async def get_transaction(tx_hash: str) -> web_response.Response:
    """Retrieve transaction detail from transaction hash

        Args:
        tx_hash: hash of transaction we are interested in.
    """

    def _format_transaction(tx_detail: Dict[str, str]) -> Dict[str, Union[str, int]]:
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