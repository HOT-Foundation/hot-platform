from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "World!")
    text = "Hello " + name
    print('received request, replying with "{}".'.format(text))
    return web.Response(text=text)