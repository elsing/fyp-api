
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
from common.models import Flow, FlowValidation
from common.errors import DBAccessError, UnauthorisedError
from common.payloader import getData
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist


def flowObjGenerator(flow):
    flowObj = {flow[0]: {}}
    values = [{'org_id': flow[1]}, {'stream_id': flow[2]}, {'name': flow[3]}, {
        'protocol': flow[4]}, {'port': flow[5]}, {'status': flow[6]}, {'to': flow[7]}]
    for value in values:
        flowObj[flow[0]].update(value)
    return flowObj


class APIFlows(Resource):
    method_decorators = [protected()]

    async def get(self, request, flow_id="all"):
        logger.info("GET flow request for '{}'".format(flow_id))

        try:
            if flow_id == "all":
                flows = await Flow.all().values("fow_id", "org_id_id", "stream_id_id", "name", "status", "description", "monitor")
            else:
                flows = await Flow.filter(flow_id=flow_id).get_or_none().values("fow_id", "org_id_id", "stream_id_id", "name", "status", "description", "monitor")
        except ValueError:
            raise SanicException("Bad request...! :( 🔍", status_code=400)
        except:
            raise DBAccessError
        # Return JSON of all flows, unless one is specified
        if flows:
            return flows
        # Raise if not found
        raise SanicException(
            "That flow was not found...! :( 🔍", status_code=404)

    async def post(self, request):
        # Get user_id from request
        user_data = await getData(request)
        user_id = user_data["user_id"]

        # Validate request
        try:
            input = FlowValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        print(input)
        # Create Flow
        try:
            # newFlow = Flow(org_id_id=input['org_id'], stream_id_id=input["stream_id"], name=input["name"],
            #    created_by_id = user_id, protocol = input["protocol"], port = input["port"], status = input["status"], to = input["to"])
            # await newFlow.save(using_db="default")
            await Flow.create(org_id_id=input['org_id'], stream_id_id=input["stream_id"], name=input["name"], created_by_id=user_id, protocol=input["protocol"], port=input["port"], status=input["status"], to=input["to"])
        except:
            raise DBAccessError

        # Log Flow creation and return response
        logger.info("Flow added with name: {} by user_id: ".format(
            input["name"], user_id))
        return text("Flow added! ✅", status=201)

    async def delete(self, request):
        pass
