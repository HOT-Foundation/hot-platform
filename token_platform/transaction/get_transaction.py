from aiohttp import web, web_request, web_response
from stellar_base.horizon import horizon_livenet, horizon_testnet, Horizon
from conf import settings
from typing import Dict, List, Any, NewType, Union, Mapping, Optional
import copy
JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


async def get_transaction_from_request(request: web_request.Request) ->  web_response.Response:
    """AIOHttp Request transaction hash to get transaction detail"""
    tx_hash = request.match_info.get('tx_hash', "")
    return await get_transaction(tx_hash)


async def get_transaction(tx_hash: str) -> web_response.Response:
    """Retrieve transaction detail from transaction hash

        Args:
        tx_hash: hash of transaction we are interested in.
    """

    def _format_transaction(tx_detail: Dict[str, str]) -> Dict[str, str]:
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