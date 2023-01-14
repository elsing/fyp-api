import bcrypt
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from functools import wraps
from sanic.exceptions import SanicException
from sanic_restful_api import Resource
from marshmallow import Schema, fields, ValidationError, EXCLUDE
from argon2 import PasswordHasher
from sanic import text
from sanic.log import logger
from common.models import User


class UnauthorisedError(SanicException):
    message = "Unauthorised access...!"
    status_code = 401
    quiet = True


class DBAccessError(SanicException):
    message = "DB access error...!"
    status_code = 500
    quiet = False


class UserValidation(Schema):
    org_id = fields.Int(load_default=1)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(load_default="")
    permission = fields.Str(load_default="default")


class AuthenticationHeaders(Schema):
    username = fields.Str()
    password = fields.Str()
    session_key = fields.Str(required=True, error_messages={
        "required": "No key included in request."})

    class Meta:
        unknown = EXCLUDE


class APIUsers(Resource):
    # method_decorators = [protected()]

    async def get(self, request, username, local=False):
        # Make sure username is not empty
        if username == "":
            raise SanicException("User not specified...!",
                                 status_code=404, quiet=True)
        # Log GET username request
        logger.info("GET username request for '{}'".format(username))
        # Attempt to find user
        try:
            user = await User.filter(username=username).values_list("username", "password", "first_name", "last_name")
        except:
            raise DBAccessError
        # If found, return JSON of user data
        if user:
            for details in user:
                return {"username": details[0], "password": details[1], "first_name": details[2], "last_name": details[3]}
        # Raise if not found
        if local != True:
            raise SanicException("User not found...",
                                 status_code=404, quiet=True)

    # @scoped(['admin'])
    async def post(self, request, username=""):
        # Attempt to validate data first - this will be removed soon, as tortoise has validation
        try:

            input = UserValidation().load(request.json)
        except ValidationError as err:
            logger.info("Error")
            logger.info(request.json)
            logger.info(err.messages)
            raise SanicException("Error: {}".format(
                err.messages), status_code=400, quiet=True)
        # Log request
        logger.info("POST user request for '{}'".format(input["username"]))
        # Test if user already exists
        try:
            res = await self.get(request, input['username'], local=True)
        except:
            raise SanicException(status_code=500, quiet=True)
        if res:
            raise SanicException("Username already exists...",
                                 status_code=409, quiet=True)
        # Encrypt Password

        # Argon verification is not working
        # ph = PasswordHasher()
        # hash = ph.hash(input['password'])
        hash = bcrypt.hashpw(
            input['password'].encode("utf-8"), bcrypt.gensalt())

        # Try create user
        try:
            await User.create(org_id_id=input['org_id'], username=input['username'], email=input['email'], password=hash.decode("utf-8"),
                              first_name=input['first_name'], last_name=input['last_name'], permission=input['permission'])
            pass
        except:
            raise DBAccessError
        # Log and return success
        logger.info("User added with username: {}".format(input["username"]))
        return text("User added! ✅", status=201)

    async def delete(self, request, username):
        # if username == "":
        #     raise SanicException("User not specified...!",
        #                          status_code=404, quiet=True)
        # try:
        #     input = UserValidation(only="username").load(request.json)
        # except ValidationError as err:
        #     logger.info("Error")
        #     logger.info(err.messages)
        #     raise SanicException("Error: {}".format(
        #         err.messages), status_code=400, quiet=True)
        try:
            res = await self.get(request, username, local=True)
        except:
            raise SanicException(status_code=500, quiet=True)
        if not res:
            raise SanicException("User does not exist...",
                                 status_code=404, quiet=True)
        try:
            await User.filter(username=username).delete()
        except:
            raise DBAccessError
        return text("User deleted! 🗑️")
