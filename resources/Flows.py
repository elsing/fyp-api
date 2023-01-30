
import uuid
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
from common.models import Flow, FlowCreateValidation, FlowModifyValidation
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
                flows = await Flow.all().values("flow_id", "org_id_id", "name", "status", "description", "monitor", "api_key")
            else:
                flows = await Flow.filter(flow_id=flow_id).get_or_none().values("flow_id", "org_id_id", "name", "status", "description", "monitor", "api_key")
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

        print(request.json)

        # Validate request
        try:
            input = FlowCreateValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        print(input)
        # Create Flow
        try:
            # newFlow = Flow(org_id_id=input['org_id'], stream_id_id=input["stream_id"], name=input["name"],
            #    created_by_id = user_id, protocol = input["protocol"], port = input["port"], status = input["status"], to = input["to"])
            # await newFlow.save(using_db="default")
            await Flow.create(org_id_id=input['org_id'], name=input["name"], created_by_id=user_id, status=input["status"], description=input["description"], monitor=input["monitor"], api_key=uuid.uuid4())
        except:
            raise DBAccessError

        # Log Flow creation and return response
        logger.info("Flow added with name: {} by user_id: ".format(
            input["name"], user_id))
        return json("Flow added! ✅", status=201)

    async def patch(self, request, flow_id):
        # Get user_id from request
        print(request.json)

        # Validate request
        try:
            input = FlowModifyValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        print(input)
        # Create Flow
        try:
            # newFlow = Flow(org_id_id=input['org_id'], stream_id_id=input["stream_id"], name=input["name"],
            #    created_by_id = user_id, protocol = input["protocol"], port = input["port"], status = input["status"], to = input["to"])
            # await newFlow.save(using_db="default")
            await Flow.filter(flow_id=flow_id).update(name=input["name"], description=input["description"], monitor=input["monitor"])
        except:
            raise DBAccessError

        # Log Flow creation and return response
        logger.info("Flow updated ")
        return json("Flow updated! ✅", status=201)

    async def delete(self, request, flow_id):
        # Delete Flow

        try:
            await Flow.filter(flow_id=flow_id).delete()
        except:
            raise DBAccessError

        # Log Flow deletion and return response
        logger.info("DELETE flow request for '{}'".format(flow_id))
        return json("Flow deleted! ✅", status=201)
