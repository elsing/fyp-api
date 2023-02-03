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
from common.errors import DBAccessError, BadRequestError
from tortoise.exceptions import OperationalError
from tortoise.transactions import atomic

from common.payloader import getData


def riverNotNull(river):
    if river == "":
        raise SanicException(
            "River not specified...! Use /river(s)/RIVER", status_code=404)


class APIRivers(Resource):
    method_decorators = [protected()]

    async def get(self, request, river_id=""):
        delta_id = river_id
        riverNotNull(river_id)

        logger.info("GET river request for '{}'".format(river_id))

        # temp = await River.filter(river_id=1).prefetch_related("flow_id").values()
        temp = await River.raw("SELECT * FROM river INNER JOIN flow ON river.flow_id_id = flow.flow_id WHERE river.river_id_id = 1")

        return

        try:
            river = await River.filter(river_id_id=river_id).all().values()
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
        logger.info("DELETE River request for '{}'".format(river_id))
        return json("River deleted! ✅", status=201)
