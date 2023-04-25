from apscheduler.schedulers.asyncio import AsyncIOScheduler
from common.models import Stream, Flow
from sanic import json as sanic_json, Websocket
from sanic.exceptions import WebsocketClosed
from eventlet.timeout import Timeout
from time import sleep
import ujson
import json


async def authorisation(ws, api_key, scheduler, firstLoad=False):
    valid = await Flow.filter(api_key=api_key).get_or_none().values()
    if valid:
        print("Valid API Key")
        if firstLoad:
            if valid["status"] == "online":
                print("Already Online")
                await sendInfo(ws, "API Key already in use")
                await ws.close()
                return False
        return True
    else:
        scheduler.remove_all_jobs()
        await sendInfo(ws, "Invalid API Key")
        await ws.close()
        return False


async def internalError(ws, e):
    print("Error: {}".format(e))
    await ws.send("Error: Internal Server Error")


async def sendInfo(ws, message):
    await ws.send(ujson.dumps(["info", message]))


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
            await sendInfo(ws, "No Streams defined yet.")
    except Exception as e:
        print("Internal Error:", e)


async def updateDaemonStatus(api_key, status):
    try:
        await Flow.filter(api_key=api_key).update(status=status)
    except Exception as e:
        print("DEBUG: Internal Error:", e)
        # await internalError(ws, e)


async def confirmStatus(ws, firstLoad=False):
    confirm = None
    await ws.send(ujson.dumps(["confirm"]))
    confirm = await ws.recv()
    confirm = json.loads(confirm)
    print("Confirm: ", confirm)
    return confirm


async def DaemonWSS(request, ws: Websocket):
    confirmed = False

    print("Websocket Connected")
    api_key = request.headers["api_key"]
    print("API Key: {}".format(api_key))
    scheduler = AsyncIOScheduler()
    flowDetails = await getFlow(ws, api_key, scheduler)
    if not flowDetails:
        return
    print("Flow Details: {}".format(flowDetails))
    scheduler.add_job(getStream, 'interval', seconds=30,
                      args=[ws, api_key, scheduler, flowDetails], )
    # scheduler.add_job(confirmStatus, 'interval', seconds=30, args=[ws])
    try:
        # Confirm response from the daemon
        confirm = await confirmStatus(ws, firstLoad=True)
        if confirm["cmd"] == "confirm":
            print("Confirmed")
            confirmed = True
            await sendInfo(ws, "Hello Flow {}".format(flowDetails["name"]))
            await updateDaemonStatus(api_key, "online")
            # Once confirmed, start the scheduler
            scheduler.start()
        # Start the loop
        while True:
            # api_key = request.headers["api_key"]
            data = await ws.recv()
            data = json.loads(data)
            if data["cmd"] == "patch":
                try:
                    if data["field"] == "status":
                        await Stream.filter(stream_id=data["id"]).update(status=data["value"])
                    elif data["field"] == "error":
                        await Stream.filter(stream_id=data["id"]).update(error=data["value"])

                except:
                    await sendInfo(ws, "Error: Internal Server Error - Failed to update information.")
            elif data["cmd"] == "delete":
                try:
                    await Stream.filter(stream_id=data["id"]).delete()
                except:
                    await sendInfo(ws, "Error: Internal Server Error - Failed to delete stream.")
            else:
                await sendInfo(ws, "Error: Unknown Command")

    except Exception as e:
        print("Something", e)
    except:
        print("Disconnected")
        if confirmed:
            scheduler.shutdown()
        await updateDaemonStatus(api_key, "offline")

    # data = {'foo': 'bar'}
    # await ws.send(ujson.dumps(data))
    # await asyncio.sleep(10)
