
import bcrypt
import json
from sanic_restful_api import Resource
from sanic import text
from sanic.log import logger
from sanic.exceptions import SanicException
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from marshmallow import ValidationError
# from argon2 import PasswordHasher
from common.models import Stream, StreamValidation
from common.errors import DBAccessError, UnauthorisedError
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist


class APIStreams(Resource):
    method_decorators = [protected()]

    async def get(self, request, stream_id="all"):
        logger.info("GET stream request for '{}'".format(stream_id))

        try:
            if stream_id == "all":
                streams = await Stream.all().values("stream_id", "org_id_id", "name")
            else:
                streams = await Stream.filter(stream_id=stream_id).get_or_none().values("stream_id", "org_id_id", "name")
        except ValueError:
            raise SanicException("Bad request...! :( 🔍", status_code=400)
        except:
            raise DBAccessError

        # Return JSON of all streams, unless one is specified
        if streams:
            return streams
        # Raise if not found
        raise SanicException(
            "That stream was not found...! :( 🔍", status_code=404)

    async def post(self, request):
        # Validate request
        try:
            input = StreamValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        # Check if stream already exists
        name = input["name"]
        try:
            existing = await Stream.filter(name=name).get_or_none()

        except:
            raise DBAccessError()
        if existing:
            raise SanicException("Stream already exists...!",
                                 status_code=409)

        # Create stream
        try:
            await Stream.create(org_id_id=input['org_id'], name=input["name"])
        except:
            raise DBAccessError

        # Log stream creation and return response
        logger.info("Stream added with name: {}".format(input["name"]))
        return text("Stream added! ✅", status=201)

    async def delete(self, request):
        pass
