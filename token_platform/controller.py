from aiohttp import web


async def handle(request):
    app = request.app
    response: dict = {}

    for name, resource in app.router.items():
        if 'formatter' in resource.get_info():
            path = resource.get_info()['formatter']
            n = name.replace('get-', '').replace('put-', '').replace('post-', '').replace('delete-', '')
            if n not in response:
                response[n] = f'{path}'
    return web.json_response(response)
