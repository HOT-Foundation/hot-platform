import copy
from typing import Any, Dict, List, Mapping, NewType, Optional, Union

import aiohttp
import stellar
from conf import settings
from router import reverse
from wallet.wallet import get_wallet

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
HORIZON_URL = settings['HORIZON_URL']


async def is_duplicate_transaction(transaction_hash: str) -> bool:
    """Check transaction is duplicate or not"""
    url = f'{HORIZON_URL}/transactions/{transaction_hash}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.json()
            id = response.get('id')
            return True if id else False


async def submit_transaction(xdr: bytes) -> Dict[str, str]:
    """Submit transaction into Stellar network"""
    url = f'{HORIZON_URL}/transactions'
    async with aiohttp.ClientSession() as session:
        data = {'tx': xdr}
        async with session.post(url, data=data) as resp:
            response = await resp.json()
            if resp.status == 400:
                msg = response.get('extras', {}).get('result_codes', {}).get('transaction', None)
                if msg:
                    reasons = get_reason_transaction(response)
                    if reasons:
                        msg += f' {reasons}'
                raise aiohttp.web.HTTPBadRequest(reason=msg)
            if resp.status == 404:
                msg = response.get('extras', {}).get('result_codes', {}).get('transaction', None)
                if msg:
                    reasons = get_reason_transaction(response)
                    if reasons:
                        msg += f' {reasons}'
                raise aiohttp.web.HTTPNotFound(reason=msg)
            if resp.status == 200 or resp.status == 202:
                return response
            raise aiohttp.web.HTTPInternalServerError()


def get_reason_transaction(response: Dict) -> Union[str, None]:
    reasons = response.get('extras', {}).get('result_codes', {}).get('operations', None)
    if not reasons:
        return None
    result = reasons[0]
    for i in range(1, len(reasons)):
        result += f'/{reasons[i]}'
    return result


async def get_current_sequence_number(wallet_address: str) -> int:
    """Get current sequence number of the wallet"""
    wallet = await stellar.wallet.get_stellar_wallet(wallet_address)
    return wallet.sequence


async def get_transaction_hash(address: str, memo: str) -> Union[str, None]:
    """Retrieve transaction detail from wallet address and memo."""
    transaction = await get_transaction_by_memo(address, memo)

    if isinstance(transaction, Dict) and 'transaction_hash' in transaction:
        return transaction['transaction_hash']
    else:
        return None


async def get_transaction(tx_hash: str) -> Dict[str, Union[str, int, List[Dict[str, str]]]]:
    """Retrieve transaction detail from transaction hash

        Args:
        tx_hash: hash of transaction we are interested in.
    """

    def _format_transaction(tx_detail: Dict[str, str]) -> Dict[str, Any]:
        """Format transaction detail in pattern dict"""
        return {
            "@id": reverse('transaction', transaction_hash=tx_detail.get('id')),
            "transaction_id": tx_detail.get("id", None),
            "paging_token": tx_detail.get("paging_token"),
            "ledger": tx_detail.get("ledger"),
            "created_at": tx_detail.get("created_at", None),
            "source_account": tx_detail.get("source_account", None),
            "source_account_sequence": tx_detail.get("source_account_sequence", None),
            "fee_paid": tx_detail.get("fee_paid", None),
            "signatures": tx_detail.get("signatures", None),
            "memo": tx_detail.get("memo", None),
        }

    async def _get_operation_data_of_transaction(tx_hash: str) -> List[Dict[str, str]]:
        """Get operation list of transaction"""
        operations = await stellar.wallet.get_operations_of_transaction(tx_hash)
        for operation in operations:
            operation.pop("_links")
        return operations

    transaction = await stellar.wallet.get_transaction(tx_hash)

    tx_detail = _format_transaction(transaction)

    tx_detail["operations"] = await _get_operation_data_of_transaction(tx_hash)

    return tx_detail


async def get_signers(wallet_address: str) -> List[Dict[str, str]]:
    """Get signers list of wallet address"""
    wallet = await get_wallet(wallet_address)
    signers = list(filter(lambda signer: signer['weight'] > 0, wallet.signers))
    formated = list(map(lambda signer: {'public_key': signer['public_key'], 'weight': signer['weight']}, signers))
    return formated


async def get_threshold_weight(wallet_address: str, operation_type: str) -> int:
    """Get threshold weight for operation type of wallet address"""

    def _get_threshould_level(operation_type):
        """Get threshould level from operation type"""
        low = ['allow_trust']
        high = ['set_signer', 'set_threshold']

        if operation_type in low:
            return 'low_threshold'
        elif operation_type in high:
            return 'high_threshold'
        else:
            return 'med_threshold'

    wallet = await get_wallet(wallet_address)

    level = _get_threshould_level(operation_type)
    return wallet.thresholds[level]


async def get_transaction_by_memo(source_account: str, memo: str, cursor: int = None) -> Dict:

    # Get transactions data within key 'records'
    transactions = await stellar.wallet.get_transaction_by_wallet(
        wallet_address=source_account, limit=200, sort='desc', offset=cursor
    )

    # Filter result data on above by 'memo_type' == text
    transactions_filter = list([transaction for transaction in transactions if transaction['memo_type'] == 'text'])

    for transaction in transactions_filter:

        if transaction['memo'] == memo:
            return {
                'error': 'Transaction is already submited',
                'url': '/transaction/{}'.format(transaction['hash']),
                'transaction_hash': transaction['hash'],
            }

    if len(transactions) > 0:
        transaction_paging_token = transactions[-1]['paging_token']
        return await get_transaction_by_memo(source_account, memo, transaction_paging_token)
    return {}
