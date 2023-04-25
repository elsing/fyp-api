from sanic_restful_api import Resource
from sanic import text, json
import json as jsonmod
from sanic.log import logger
from sanic.exceptions import SanicException
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from marshmallow import ValidationError
# from argon2 import PasswordHasher
from common.models import Stream, StreamValidation
from common.errors import DBAccessError, BadRequestError, streamNotNull
from common.responses import successResponse
from common.vpn.configs import generateConfig, regenerateConfig
from tortoise.expressions import Q
import tortoise.exceptions

from common.payloader import getData


def checkName(servers, clients, input):
    for client in clients:
        if client["name"] == input["name"]:
            raise SanicException(
                "A client with this name already exists", status_code=400)
    for server in servers:
        if server["name"] == input["name"]:
            raise SanicException(
                "A server with this name already exists", status_code=400)


async def regenStream(river_id, stream):
    try:
        clients = await Stream.filter(river_id=river_id).filter(role="client").values()
        servers = await Stream.filter(river_id=river_id).filter(role="server").values()
    except:
        raise DBAccessError

    # Make sure there are no clients before deleting a server
    if clients:
        if stream["role"] == "server":
            raise SanicException(
                "Remove all clients before deleting a server", status_code=400)

    # Loop through all servers and regenerate their configs
    try:
        # First regenerate the config for all other servers - removes access as soon as daemon sees the update
        for server in servers:
            # Don't regenerate config if the server is the one being deleted
            if server["name"] != stream["name"]:
                config = await regenerateConfig(server, stream)
                if server["status"] == "init":
                    status = "init"
                else:
                    status = "pendingUpdate"
                await Stream.filter(stream_id=server["stream_id"]).update(config=config, status=status)
    except:
        raise DBAccessError


class APIStreams(Resource):
    method_decorators = [protected()]

    async def get(self, request, stream_id=""):
        river_id = stream_id
        streamNotNull(stream_id)

        logger.info("GET stream request for '{}'".format(river_id))

        # temp = await Stream.filter(stream_id=1).values("stream_id", flow="flow__name")

        # temp = await Stream.raw("SELECT * FROM stream INNER JOIN flow ON stream.flow_id_id = flow.flow_id WHERE stream.stream_id_id = 1")

        # temp = await Stream.filter(river_id=river_id).values()

        # temp = await Org.filter(org_id=1).prefetch_related("flows").values()

        try:
            stream = await Stream.filter(stream_id=stream_id).get_or_none().values()
        except ValueError:
            raise BadRequestError
        except:
            raise DBAccessError

        # Return JSON of specified stream
        if stream:
            return stream

        raise SanicException("Stream not found...! :( 🔍", status_code=404)

    async def post(self, request, stream_id=""):
        # Get user_id from request
        user_data = await getData(request)
        user_id = user_data["user_id"]

        # Validate the data
        try:
            input = StreamValidation().load(request.json)
        except ValidationError as err:
            raise SanicException(err.messages, status_code=400)

        # Pre checks and selection of what to generate
        try:
            servers = await Stream.filter(river_id=input["river_id"]).filter(role="server").values()
            clients = await Stream.filter(river_id=input["river_id"]).filter(role="client").values()
            if servers:
                # If a server exists, check if clients exist, if they do, then another server cannot be added. Unless no clients exist.
                # This allows for a pool of just servers.
                checkName(servers, clients, input)
                if len(servers) > 1:
                    if input["role"] == "client":
                        raise SanicException(
                            "This is a server only river. Remove all but one server to add a client", status_code=400)
                else:
                    if input["role"] == "client":
                        config, public_key = await generateConfig(servers, input)

                if clients:
                    if input["role"] == "server":
                        raise SanicException(
                            "Remove all clients to define multiple servers", status_code=400)
                else:
                    if input["role"] == "server":
                        config, public_key = await generateConfig(servers, input)

            # If server does not exist, check the role, if it a server, generate a config, if it is a client, raise an error.
            else:
                if input["role"] == "client":
                    raise SanicException(
                        "A server must be created first", status_code=400)
                else:
                    config, public_key = await generateConfig(servers, input)

        except SanicException as err:
            raise err
        except:
            raise DBAccessError

        try:
            await Stream.create(flow_id=input["flow_id"], river_id=input["river_id"], name=input["name"], role=input["role"], port=input["port"], config=config, public_key=public_key, ip=input["ip"], endpoint=input["endpoint"], tunnel=input["tunnel"])
        except tortoise.exceptions.ValidationError as err:
            raise SanicException(err, status_code=400)
        except:
            raise DBAccessError

        logger.info("Stream created")
        return successResponse("Stream created ✅", status=201)

    async def patch(self, request, stream_id=""):
        streamNotNull(stream_id)

        logger.info("PATCH stream request for '{}'".format(stream_id))

        try:
            servers = await Stream.filter(river_id=request.json["river_id"]).filter(role="server").values()
        except:
            raise DBAccessError

        await regenStream(request.json["river_id"], request.json)
        config, public_key = await generateConfig(servers, request.json)

        # If the stream exists, update it, if not, raise an error
        try:
            stream = await Stream.filter(stream_id=stream_id).get_or_none()
            if stream:
                stream.update_from_dict(request.json)
                stream.config = config
                stream.public_key = public_key
                stream.status = "pendingUpdate"
                # await Stream.filter(stream_id=stream_id).update_from_dict(jsonmod.dumps(request.json))
                await stream.save()
            else:
                raise SanicException(
                    "That Stream was not found...! :( 🔍", status_code=404)

        except tortoise.exceptions.ValidationError as err:
            raise SanicException(err, status_code=400)
        except:
            raise DBAccessError

        return successResponse("Stream updated ✅")

    async def delete(self, request, stream_id=""):
        streamNotNull(stream_id)
        logger.info("DELETE stream request for '{}'".format(stream_id))

        try:
            stream = await Stream.filter(stream_id=stream_id).get_or_none().values()
        except:
            raise DBAccessError

        # Check if stream exists first
        if not stream:
            raise SanicException(
                "That Stream was not found...! :( 🔍", status_code=404)
        else:
            river_id = stream["river_id"]

        # Initate regneration of config(s) for river
        await regenStream(river_id, stream)

        # If stream is init, delete it, else set status to pendingDelete
        # So the Flow can confirm it is safe to delete
        try:
            if stream["status"] == "init":
                await Stream.filter(stream_id=stream_id).delete()
            else:
                await Stream.filter(stream_id=stream_id).update(status="pendingDelete")
        except Exception:
            raise DBAccessError

        # Return JSON response
        return successResponse("Stream pending removal / deleted ✅")
