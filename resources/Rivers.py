
from sanic_restful_api import Resource
from sanic import json
from sanic.log import logger
from sanic.exceptions import SanicException
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from marshmallow import ValidationError
# from argon2 import PasswordHasher
from common.models import River, RiverValidation
from common.errors import DBAccessError, BadRequestError
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist


def riverNotNull(river):
    if river == "":
        raise SanicException(
            "River not specified...! Use /river(s)/RIVER", status_code=404)


class APIRiverFlow(Resource):
    method_decorators = [protected()]

    async def get(self, request, river_id=""):
        riverNotNull(river_id)

        logger.info("GET river request for '{}'".format(river_id))

        try:
            rivers = await River.filter(river_id=river_id).get_or_none().annotate()

        except ValueError:
            raise BadRequestError
        except:
            raise DBAccessError

        print("Rivers: {}".format(rivers))

        if rivers:
            return rivers


class APIRivers(Resource):
    method_decorators = [protected()]

    async def get(self, request, river_id="all"):
        logger.info("GET river request for '{}'".format(river_id))

        try:
            if river_id == "all":
                rivers = await River.all().values("river_id", "org_id_id", "name", "initiated")
            else:
                rivers = await River.filter(river_id=river_id).get_or_none().values("river_id", "org_id_id", "name", "initiated")
        except ValueError:
            raise BadRequestError
        except:
            raise DBAccessError

        # Return JSON of all rivers, unless one is specified
        if rivers:
            return rivers
        # Raise if not found
        raise SanicException(
            "That river was not found...! :( 🔍", status_code=404)

    async def post(self, request):
        # Validate request
        try:
            input = RiverValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        # Check if river already exists - is this needed really??
        # name = input["name"]
        # try:
        #     existing = await River.filter(name=name).get_or_none()
        # except:
        #     raise DBAccessError()
        # if existing:
        #     raise SanicException("River already exists...!",
        #                          status_code=409)

        # Create river
        try:
            await River.create(org_id_id=input['org_id'], name=input["name"], initiated=input["initiated"])
        except:
            raise DBAccessError

        # Log river creation and return response
        logger.info("River added with name: {}".format(input["name"]))
        return json("River added! ✅", status=201)

    async def patch(self, request, river_id=""):
        riverNotNull(river_id)
        # Validate request
        try:
            input = RiverValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        # Update river
        try:
            await River.filter(river_id=river_id).update(name=input["name"], initiated=input["initiated"])
        except:
            raise DBAccessError

        # Log river update and return response
        logger.info("River updated")
        return json("River updated! ✅", status=201)

    async def delete(self, request, river_id=""):
        riverNotNull(river_id)
        # Delete river
        try:
            await River.filter(river_id=river_id).delete()
        except:
            raise DBAccessError

        # Log river deletion and return response
        logger.info("DELETE river request for '{}'".format(river_id))
        return json("River deleted! ✅", status=201)
