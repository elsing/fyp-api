from sanic_restful_api import Resource
from sanic import text, json
from sanic.log import logger
from sanic.exceptions import SanicException
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from marshmallow import ValidationError
# from argon2 import PasswordHasher
from common.models import Stream, StreamValidation
from common.errors import DBAccessError, BadRequestError, streamNotNull
from common.vpn.configs import generateConfig, regenerateConfig
from tortoise.expressions import Q

from common.payloader import getData

def checkName(servers, clients, input):
    for client in clients:
        if client["name"] == input["name"]:
            raise SanicException(
                "Error: A client with this name already exists", status_code=400)
    for server in servers:
        if server["name"] == input["name"]:
            raise SanicException(
                "Error: A server with this name already exists", status_code=400)

class APIStreams(Resource):
    method_decorators = [protected()]

    async def get(self, request, stream_id=""):
        river_id = stream_id
        streamNotNull(stream_id)

        logger.info("GET stream request for '{}'".format(river_id))

        # temp = await Stream.filter(stream_id=1).values("stream_id", flow="flow__name")

        # temp = await Stream.raw("SELECT * FROM stream INNER JOIN flow ON stream.flow_id_id = flow.flow_id WHERE stream.stream_id_id = 1")

        temp = await Stream.filter(river_id=river_id).values()

        print(temp)
        # temp = await Org.filter(org_id=1).prefetch_related("flows").values()

        return temp

        try:
            stream = await Stream.filter(stream_id_id=stream_id).all().values()
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
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

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
                            "Error: Remove all clients to define multiple servers", status_code=400)
                else:
                    if input["role"] == "server":
                        config, public_key = await generateConfig(servers, input)

            # If server does not exist, check the role, if it a server, generate a config, if it is a client, raise an error.
            else:
                if input["role"] == "client":
                    raise SanicException(
                        "Error: A server must be created first", status_code=400)
                else:
                    config, public_key = await generateConfig(servers, input)

        

        except SanicException as err:
            raise err
        except:
            raise DBAccessError

        try:
            await Stream.create(flow_id=input["flow_id"], river_id=input["river_id"], name=input["name"], role=input["role"], port=input["port"], config=config, public_key=public_key, ip=input["ip"], endpoint=input["endpoint"], tunnel=input["tunnel"])
            pass
        except:
            raise DBAccessError

        logger.info("Stream created")
        return json("Stream created ✅", status=201)

    async def patch(self, request, stream_id=""):
        streamNotNull(stream_id)

    

