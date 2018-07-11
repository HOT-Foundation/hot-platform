import prometheus_client
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram

from aiohttp import web

metric = dict()

metric['GET_WALLET_ADDRESS'] = Gauge(
    'get_wallet_address_htkn_platform_api', 'tracking get wallet api')

metric['GET_WALLET_HISTORY'] = Gauge(
    'get_wallet_history_htkn_platform_api', 'tracking get wallet history api')

metric['POST_GENERATE_WALLET'] = Gauge(
    'post_generate_wallet_htkn_platform_api', 'tracking post generate wallet api') 

metric['POST_GENERATE_TRUST_WALLET'] = Gauge(
    'post_generate_trust_wallet_htkn_platform_api', 'tracking post generate trust wallet api')

metric['POST_GENERATE_PAYMENT'] = Gauge(
    'post_generate_payment_htkn_platform_api', 'tracking post generate payment api')

metric['POST_GENERATE_JOINT_WALLET'] = Gauge(
    'post_generate_joint_wallet_htkn_platform_api', 'tracking post generate joint wallet api')

metric['GET_CURRENT_SEQUENCE'] = Gauge(
    'get_current_sequence_htkn_platform_api', 'tracking get current sequence api')

metric['GET_CHANGE_TRUST'] = Gauge(
    'get_change_trust_htkn_platform_api', 'tracking get change trust api')

metric['GET_TRANSACTION_HASH'] = Gauge(
    'get_transaction_hash_htkn_platform_api', 'tracking get transaction hash api')

metric['GET_TRANSACTION_HASH_MEMO'] = Gauge(
    'get_transaction_hash_memo_htkn_platform_api', 'tracking get transaction hash memo api')

metric['GET_ESCROW_ADDRESS'] = Gauge(
    'get_escrow_address_htkn_platform_api', 'tracking get escrow address api')

metric['POST_ESCROW_GENERATE_WALLET'] = Gauge(
    'post_escrow_generate_wallet_htkn_platform_api', 'tracking post escrow generate wallet api')

metric['POST_GENERATE_PRESIGNED_TRANSACTION'] = Gauge(
    'post_generate_presigned_transaction_htkn_platform_api', 'tracking post generate prosigned transaction api')

metric['GET_TRANSACTION'] = Gauge(
    'get_transaction_htkn_platform_api', 'tracking get transaction api')

metric['PUT_TRANSACTION'] = Gauge(
    'put_transaction_htkn_platform_api', 'tracking put transaction api')

metric['POST_CLOSE_ESCROW_WALLET'] = Gauge(
    'post_close_escrow_wallet_htkn_platform_api', 'tracking post close escrow wallet api')

metric['POST_CLOSE_JOINT_WALLET'] = Gauge(
    'post_close_joint_wallet_htkn_platform_api', 'tracking post close joint wallet api')


async def get_metrics(request: web.Request) -> web.Response:
    response = web.Response(body=prometheus_client.generate_latest())
    response.content_type = CONTENT_TYPE_LATEST
    return response


@web.middleware
async def metrics_mapping(request, handler):
    print(request.method)
    print(request.remote)
    print(request.path_qs)
    response = await handler(request)
    return response
