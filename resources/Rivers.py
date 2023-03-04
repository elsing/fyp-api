import bcrypt
import json as jsonmod
from sanic_restful_api import Resource
from sanic import text, json
from sanic.log import logger
from sanic.exceptions import SanicException
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from marshmallow import ValidationError
# from argon2 import PasswordHasher
from common.models import Stream, River, RiverValidation
from common.errors import DBAccessError, BadRequestError, streamNotNull, riverNotNull
from tortoise.exceptions import OperationalError
from tortoise.transactions import atomic

from common.payloader import getData
from common.vpn.configs import regenerateConfig


class APIRiversStreams(Resource):
    method_decorators = [protected()]

    async def get(self, request, river_id=""):
        riverNotNull(river_id)

        logger.info("GET river streams request for '{}'".format(river_id))

        try:
            streams = await Stream.filter(river_id=river_id).values()
        except ValueError:
            raise BadRequestError
        except:
            raise DBAccessError

        if streams:
            return streams
        raise SanicException(
            "That River's Streams were not found...! :( 🔍", status_code=404)

    async def delete(self, request, river_id="", stream_id=""):
        riverNotNull(river_id)
        streamNotNull(stream_id)

        logger.info("DELETE stream request for '{}'".format(stream_id))

        try:
            clients = await Stream.filter(river_id=river_id).filter(role="client").values()
            servers = await Stream.filter(river_id=river_id).filter(role="server").values()
            stream = await Stream.filter(stream_id=stream_id).get_or_none().values()
        except:
            raise DBAccessError

        # Check if stream exists first
        if not stream:
            raise SanicException(
                "That Stream was not found...! :( 🔍", status_code=404)

        # Make sure there are no clients before deleting a server
        if clients:
            if stream["role"] == "server":
                raise SanicException(
                    "Error: Remove all clients before deleting a server", status_code=400)

        # Delete stream
        try:
            # First regenerate the config for all other servers - removes access as soon as daemon sees the update
            for server in servers:
                # Don't regenerate config if the server is the one being deleted
                print("Regen server", server)
                if server["name"] != stream["name"]:
                    config = await regenerateConfig(server, stream)
                    await Stream.filter(stream_id=server["stream_id"]).update(config=config, status="pendingUpdate")
            # If stream is init, delete it, else set status to pendingDelete
            # So the Flow can confirm it is safe to delete
            if stream["status"] == "init":
                await Stream.filter(stream_id=stream_id).delete()
            else:
                await Stream.filter(stream_id=stream_id).update(status="pendingDelete")
        except Exception:
            raise DBAccessError

        # Return JSON response
        return json("Stream removed / pending removal! ✅", status=201)


class APIRivers(Resource):
    method_decorators = [protected()]

    async def get(self, request, river_id=""):
        delta_id = river_id
        riverNotNull(river_id)

        logger.info("GET river request for '{}'".format(river_id))

        # temp = await River.filter(river_id=1).prefetch_related("flow_id").values()
        # temp = await River.raw("SELECT * FROM river INNER JOIN flow ON river.flow_id_id = flow.flow_id WHERE river.river_id_id = 1")

        try:
            river = await River.filter(river_id=river_id).all().values()
        except ValueError:
            raise BadRequestError
        except:
            raise DBAccessError

        # Return JSON of specified river
        if river:
            return river

        raise SanicException("River not found...! :( 🔍", status_code=404)

    async def post(self, request, river_id=""):
        # Get user_id from request
        user_data = await getData(request)
        user_id = user_data["user_id"]

        # Validate the data
        try:
            input = RiverValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        print(input)

        try:
            # org_id=input["org_id"],
            await River.create(delta_id=input["delta_id"], name=input["name"], protocol=input["protocol"])
        except:
            raise DBAccessError

        logger.info("River created")
        return json("River created ✅", status=201)

    async def patch(self, request, river_id=""):
        riverNotNull(river_id)

    async def delete(self, request, river_id=""):
        riverNotNull(river_id)

        # Log request
        logger.info("DELETE River request for '{}'".format(river_id))

        # Delete River tranasactionally

        @atomic()
        async def delete_delta():
            await Stream.filter(river_id=river_id).all().delete()
            await River.filter(river_id=river_id).delete()

        try:
            await delete_delta()
        except OperationalError as e:
            raise SanicException(
                "Delete failed. Error:{}".format(e), status_code=500)
        except:
            raise DBAccessError

        # Log delta deletion and return response
        return json("River deleted! ✅", status=201)
