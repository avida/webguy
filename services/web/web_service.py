#!/usr/bin/env python3
import aiohttp
from aiohttp import web

async def main_handle(request):
    return web.HTTPFound(location="/index.html")
    
async def handle(request):
    return web.Response(text="gtfo")

app = web.Application()
app.router.add_get('/', main_handle)
app.router.add_get('/h', handle)
app.router.add_static("/", "./static/", show_index=True)
web.run_app(app, port=8088)

