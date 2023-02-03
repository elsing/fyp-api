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
from common.models import Stream, StreamValidation, Org
from common.errors import DBAccessError, BadRequestError
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist

from common.payloader import getData


def streamNotNull(stream):
    if stream == "":
        raise SanicException(
            "Stream or stream not specified...!", status_code=404)


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

        print(input)

        try:
            await Stream.create(org_id_id=input["org_id"], stream_id_id=input["stream_id"], flow_id_id=input["flow_id"], role=input["role"], protocol=input["protocol"], port=input["port"], config=input["config"], tunnel=input["tunnel"], error=input["error"])
        except:
            raise DBAccessError

        logger.info("Stream created")
        return json("Stream created ✅", status=201)

    async def patch(self, request, stream_id=""):
        streamNotNull(stream_id)

    async def delete(self, request, stream_id=""):
        streamNotNull(stream_id)
