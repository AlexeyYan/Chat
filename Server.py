import asyncio
import os
import websockets

async def echo(websocket, path):
    name=await websocket.recv()
    print("{"+name+"}")
    await websocket.send(name.upper())

asyncio.get_event_loop().run_until_complete(websockets.serve(echo,'',os.environ.get('PORT')))
asyncio.get_event_loop().run_forever()
