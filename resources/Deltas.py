
from sanic_restful_api import Resource
from sanic import json
from sanic.log import logger
from sanic.exceptions import SanicException
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from marshmallow import ValidationError
# from argon2 import PasswordHasher
from common.models import Stream, River, Delta, DeltaValidation
from common.errors import DBAccessError, BadRequestError
from tortoise.exceptions import OperationalError
from tortoise.transactions import atomic


def deltaNotNull(delta):
    if delta == "":
        raise SanicException(
            "Delta not specified...! Use /delta(s)/DELTA", status_code=404)


class APIDeltaRivers(Resource):
    method_decorators = [protected()]

    async def get(self, request, delta_id=""):
        deltaNotNull(delta_id)

        logger.info("GET delta rivers request for '{}'".format(delta_id))

        try:
            deltas = await River.filter(delta_id=delta_id).values()
        except ValueError:
            raise BadRequestError
        except:
            raise DBAccessError

        if deltas:
            return deltas
        raise SanicException(
            "That Delta's Rivers were not found...! :( 🔍", status_code=404)


class APIDeltas(Resource):
    method_decorators = [protected()]

    async def get(self, request, delta_id="all"):
        logger.info("GET delta request for '{}'".format(delta_id))

        try:
            if delta_id == "all":
                deltas = await Delta.all().values()
            else:
                deltas = await Delta.filter(delta_id=delta_id).get_or_none().values()
        except ValueError:
            raise BadRequestError
        except:
            raise DBAccessError

        # Return JSON of all deltas, unless one is specified
        if deltas:
            return deltas
        # Raise if not found
        raise SanicException(
            "That delta was not found...! :( 🔍", status_code=404)

    async def post(self, request):
        # Validate request
        try:
            input = DeltaValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        # Check if delta already exists - is this needed really??
        # name = input["name"]
        # try:
        #     existing = await Delta.filter(name=name).get_or_none()
        # except:
        #     raise DBAccessError()
        # if existing:
        #     raise SanicException("Delta already exists...!",
        #                          status_code=409)

        # Create delta
        try:
            await Delta.create(org_id_id=input['org_id'], name=input["name"], initiated=input["initiated"])
        except:
            raise DBAccessError

        # Log delta creation and return response
        logger.info("Delta added with name: {}".format(input["name"]))
        return json("Delta added! ✅", status=201)

    async def patch(self, request, delta_id=""):
        deltaNotNull(delta_id)
        # Validate request
        try:
            input = DeltaValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        # Update delta
        try:
            await Delta.filter(delta_id=delta_id).update(name=input["name"], initiated=input["initiated"])
        except:
            raise DBAccessError

        # Log delta update and return response
        logger.info("Delta updated")
        return json("Delta updated! ✅", status=201)

    async def delete(self, request, delta_id=""):
        deltaNotNull(delta_id)

        # Delete Delta tranasactionally

        @atomic()
        async def delete_delta():
            river_ids = await River.filter(delta_id=delta_id).values_list('river_id', flat=True)
            print(river_ids)
            for river_id in river_ids:
                await Stream.filter(river_id=river_id).all().delete()
            await River.filter(delta_id=delta_id).delete()
            await Delta.filter(delta_id=delta_id).delete()

        try:
            await delete_delta()
        except OperationalError as e:
            raise SanicException(
                "Delete failed. Error:{}".format(e), status_code=500)
        except:
            raise DBAccessError

        # Log delta deletion and return response
        logger.info("DELETE Delta request for '{}'".format(delta_id))
        return json("Delta deleted! ✅", status=201)
