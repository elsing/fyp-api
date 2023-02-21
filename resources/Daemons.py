import asyncio
import json
import async_timeout
from common.models import Stream, Flow
from sanic import json as sanic_json, Websocket
from time import sleep
import ujson


async def authorisation(request, ws):
    valid = await Flow.filter(api_key=request.headers["api_key"]).get_or_none()
    if valid:
        print("All good!")
        return True
    else:
        print("Invalid API Key")
        await ws.send("Invalid API Key")
        await ws.close()
        return False


async def DaemonWSS(request, ws: Websocket):
    print("DaemonWSS")
    data = {'foo': 'bar'}
    # while True:

    while True:
        try:
            with async_timeout.timeout(5):
                data = await ws.recv()
                print("recv data {}.".format(data))
        except:
            pass

        print("sending data {}.".format(data))
        await ws.send(ujson.dumps(data))
        # if await authorisation(request, ws):
        #     api_key = request.headers["api_key"]
        #     data = await ws.recv()
        #     data = json.loads(data)
        #     print(data)
        #     print(request)
        #     print(request.headers["api_key"])
        #     try:
        #         if data["command"] == "ping":
        #             await ws.send("pong")
        #         elif data["command"] == "get":
        #             try:
        #                 flows = await Flow.filter(api_key=api_key).get_or_none().values("flow_id", "name")
        #                 if flows:
        #                     await ws.send(ujson.dumps(flows))
        #                     # await ws.send_data("hello")
        #                 else:
        #                     await ws.send("Error: No Flows Associated with API Key")
        #             except Exception as e:
        #                 print("1", e)
        #                 await ws.send("Error: Internal Server Error 1")
        #         else:
        #             await ws.send("Error: Invalid command")
        #     except Exception as e:
        #         print(e)
        #         await ws.send("Error: Internal Server Error 2")

        # data = {'foo': 'bar'}
        # await ws.send(ujson.dumps(data))
        # await asyncio.sleep(10)
