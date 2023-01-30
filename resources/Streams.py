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


def streamNotNull(stream):
    if stream == "":
        raise SanicException(
            "Stream not specified...! Use /stream(s)/STREAM", status_code=404)


class APIStreams(Resource):
    method_decorators = [protected()]

    async def get(self, request, stream_id=""):
        streamNotNull(stream_id)

    async def post(self, request):
        pass

    async def patch(self, request, stream_id=""):
        streamNotNull(stream_id)

    async def delete(self, request, stream_id=""):
        streamNotNull(stream_id)
