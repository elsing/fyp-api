from apscheduler.schedulers.asyncio import AsyncIOScheduler
from common.models import Stream, Flow
from sanic import json as sanic_json, Websocket
from sanic.exceptions import WebsocketClosed
from time import sleep
import ujson


async def authorisation(ws, api_key, scheduler, firstLoad=False):
    valid = await Flow.filter(api_key=api_key).get_or_none().values()
    if valid:
        print("Valid API Key")
        if firstLoad:
            if valid["status"] == "online":
                print("Already Online")
                await ws.send("Flow already connected.")
                await ws.close()
                return False
        return True
    else:
        print("Invalid API Key")
        scheduler.remove_all_jobs()
        await ws.send("Invalid API Key")
        await ws.close()
        return False


async def internalError(ws, e):
    print("Error: {}".format(e))
    await ws.send("Error: Internal Server Error")


async def getFlow(ws, api_key, scheduler):
    if not await authorisation(ws, api_key, scheduler, True):
        return False
    try:
        flows = await Flow.filter(api_key=api_key).get_or_none().values("flow_id", "name")
        if flows:
            return flows
        else:
            await ws.send("Unknown Error")
            await ws.close()
    except WebsocketClosed as e:
        print("Websocket closed.", e)
    except Exception as e:
        print("DEBUG: Internal Error", e)
        await internalError(ws, e)


async def getStream(ws, api_key, scheduler, flow):
    await authorisation(ws, api_key, scheduler)
    try:
        streams = await Stream.filter(flow_id=flow["flow_id"]).values()
        print("streams", streams)
        if streams:
            response = ["streams", streams]
            await ws.send(ujson.dumps(response))
        else:
            await ws.send("No Streams defined yet.")
    except Exception as e:
        print("Internal Error:", e)


async def updateDaemonStatus(api_key, status):
    try:
        await Flow.filter(api_key=api_key).update(status=status)
    except Exception as e:
        print("DEBUG: Internal Error:", e)
        # await internalError(ws, e)


async def DaemonWSS(request, ws: Websocket):
    print("Websocket Connected")
    api_key = request.headers["api_key"]
    scheduler = AsyncIOScheduler()
    flowDetails = await getFlow(ws, api_key, scheduler)
    if not flowDetails:
        return
    await updateDaemonStatus(api_key, "online")
    print("Flow Details: {}".format(flowDetails))
    scheduler.add_job(getStream, 'interval', seconds=10,
                      args=[ws, api_key, scheduler, flowDetails])

    try:
        scheduler.start()
        try:
            await ws.send(ujson.dumps(["welcome", "Hello Flow... {}".format(flowDetails["name"])]))
        except Exception as e:
            print("Error: ", e)
            await ws.send("Hello Flow...")
        while True:
            # api_key = request.headers["api_key"]
            data = await ws.recv()
            await ws.send("Recieved: {}".format(data))

    except Exception as e:
        print("Something", e)
    except:
        print("Disconnected")
        scheduler.shutdown()
        await updateDaemonStatus(api_key, "offline")

    # data = {'foo': 'bar'}
    # await ws.send(ujson.dumps(data))
    # await asyncio.sleep(10)
