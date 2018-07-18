import prometheus_client
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram

from aiohttp import web

metric = dict()

metric['GET_WALLET_ADDRESS'] = Gauge(
    'get_wallet_address_token_platform_api', 'tracking get wallet api')

metric['GET_WALLET_HISTORY'] = Gauge(
    'get_wallet_history_token_platform_api', 'tracking get wallet history api')

metric['POST_GENERATE_WALLET'] = Gauge(
    'post_generate_wallet_token_platform_api', 'tracking post generate wallet api')

metric['POST_GENERATE_TRUST_WALLET'] = Gauge(
    'post_generate_trust_wallet_token_platform_api', 'tracking post generate trust wallet api')

metric['POST_GENERATE_PAYMENT'] = Gauge(
    'post_generate_payment_token_platform_api', 'tracking post generate payment api')

metric['POST_GENERATE_JOINT_WALLET'] = Gauge(
    'post_generate_joint_wallet_token_platform_api', 'tracking post generate joint wallet api')

metric['GET_CURRENT_SEQUENCE'] = Gauge(
    'get_current_sequence_token_platform_api', 'tracking get current sequence api')

metric['GET_CHANGE_TRUST'] = Gauge(
    'get_change_trust_token_platform_api', 'tracking get change trust api')

metric['GET_GET_TRANSACTION_HASH'] = Gauge(
    'get_transaction_hash_token_platform_api', 'tracking get transaction hash api')

metric['GET_GET_TRANSACTION_HASH_MEMO'] = Gauge(
    'get_transaction_hash_memo_token_platform_api', 'tracking get transaction hash memo api')

metric['GET_ESCROW_ADDRESS'] = Gauge(
    'get_escrow_address_token_platform_api', 'tracking get escrow address api')

metric['POST_ESCROW_GENERATE_WALLET'] = Gauge(
    'post_escrow_generate_wallet_token_platform_api', 'tracking post escrow generate wallet api')

metric['POST_GENERATE_PRESIGNED_TRANSACTIONS'] = Gauge(
    'post_generate_presigned_transactions_token_platform_api', 'tracking post generate prosigned transaction api')

metric['GET_TRANSACTION'] = Gauge(
    'get_transaction_token_platform_api', 'tracking get transaction api')

metric['PUT_TRANSACTION'] = Gauge(
    'put_transaction_token_platform_api', 'tracking put transaction api')

metric['POST_CLOSE_ESCROW_WALLET'] = Gauge(
    'post_close_escrow_wallet_token_platform_api', 'tracking post close escrow wallet api')

metric['POST_CLOSE_JOINT_WALLET'] = Gauge(
    'post_close_joint_wallet_token_platform_api', 'tracking post close joint wallet api')

metric['GET_CHANGE_TRUST_ADD_TOKEN'] = Gauge(
    'get_change_trust_add_token_api', 'tracking get change trust and add HTKN')

async def get_metrics(request: web.Request) -> web.Response:
    response = web.Response(body=prometheus_client.generate_latest())
    response.content_type = CONTENT_TYPE_LATEST
    return response


@web.middleware
async def metrics_increasing(request, handler):
    response = await handler(request)

    if (response.status == 200 or response.status == 202):
        resource_name = request.match_info.route.resource.name
        resource_name = str(resource_name).upper()
        resource_name = resource_name.replace('-', '_')

        # GET_METRICS is request from prometheus, we will not tracking.
        if resource_name != 'GET_METRICS' and resource_name != 'GET_ROOT':
            metric[resource_name].inc()

    return response
