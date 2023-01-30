
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


def riverNotNull(river):
    if river == "":
        raise SanicException(
            "River not specified...! Use /river(s)/RIVER", status_code=404)


class APIRivers(Resource):
    method_decorators = [protected()]

    async def get(self, request, stream_id="all"):
        pass

    async def post(self, request):
        pass

    async def patch(self, request, river_id=""):
        riverNotNull(river_id)

    async def delete(self, request, river_id=""):
        riverNotNull(river_id)
