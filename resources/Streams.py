
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
from common.errors import DBAccessError, BadRequestError
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist


def streamNotNull(stream):
    if stream == "":
        raise SanicException(
            "Stream not specified...! Use /stream(s)/STREAM", status_code=404)


class APIStreams(Resource):
    method_decorators = [protected()]

    async def get(self, request, stream_id="all"):
        logger.info("GET stream request for '{}'".format(stream_id))

        try:
            if stream_id == "all":
                streams = await Stream.all().values("stream_id", "org_id_id", "name", "initiated")
            else:
                streams = await Stream.filter(stream_id=stream_id).get_or_none().values("stream_id", "org_id_id", "name", "initiated")
        except ValueError:
            raise BadRequestError
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

        # Check if stream already exists - is this needed really??
        # name = input["name"]
        # try:
        #     existing = await Stream.filter(name=name).get_or_none()
        # except:
        #     raise DBAccessError()
        # if existing:
        #     raise SanicException("Stream already exists...!",
        #                          status_code=409)

        # Create stream
        try:
            await Stream.create(org_id_id=input['org_id'], name=input["name"], initiated=input["initiated"])
        except:
            raise DBAccessError

        # Log stream creation and return response
        logger.info("Stream added with name: {}".format(input["name"]))
        return text("Stream added! ✅", status=201)

    async def patch(self, request, stream_id=""):
        streamNotNull(stream_id)
        # Validate request
        try:
            input = StreamValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        # Update stream
        try:
            await Stream.filter(stream_id=stream_id).update(name=input["name"],
                                                            initiated=input["initiated"])
        except:
            raise DBAccessError

        # Log stream update and return response
        logger.info("Stream updated")
        return text("Stream updated! ✅", status=201)

    async def delete(self, request, stream_id=""):
        streamNotNull(stream_id)
        # Delete stream
        try:
            await Stream.filter(stream_id=stream_id).delete()
        except:
            raise DBAccessError

        # Log stream deletion and return response
        logger.info("DELETE stream request for '{}'".format(stream_id))
        return text("Stream deleted! ✅", status=201)
