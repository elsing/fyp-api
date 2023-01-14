import bcrypt
import json as jsonmod
from sanic_restful_api import Resource
from sanic import text, json
from sanic.log import logger
from sanic.exceptions import SanicException
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from marshmallow import Schema, fields, ValidationError, EXCLUDE
# from argon2 import PasswordHasher
from common.models import User
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist


class UnauthorisedError(SanicException):
    message = "Unauthorised access...!"
    status_code = 401
    quiet = False


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
    method_decorators = [protected()]

    @scoped(['admin'])
    async def get(self, request, username=""):
        # Make sure username is not empty
        if username == "":
            raise SanicException("User not specified...! Use /user(s)/USER",
                                 status_code=404)
        # Log GET username request
        logger.info("GET username request for '{}'".format(username))
        # Attempt to find user
        try:
            user = await User.filter(username=username).get_or_none().values_list("username", "password", "first_name", "last_name")
            print(user)
        except:
            raise DBAccessError
        # If found, return JSON of user data
        if user:
            return {"username": user[0], "password": user[1], "first_name": user[2], "last_name": user[3]}
        # Raise if not found
        return json({"message": "User not found...! 🔍", "error": "not_found"}, status=404)

    @scoped(['admin'])
    async def post(self, request, username="", existing=False):
        # Attempt to validate data first - this will be removed soon, as tortoise has validation
        try:

            input = UserValidation().load(request.json)
        except ValidationError as err:
            logger.info("Error")
            logger.info(request.json)
            logger.info(err.messages)
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        # Test if user already exists
        try:
            existing = await User.filter(
                Q(username=input['username']) | Q(email=input['email'])).get_or_none().values_list("username", "email")
            print(existing)
        except:
            raise DBAccessError()

        # What is duplicated? This needs to bundle the errors at some point...!
        if existing:
            if existing[0] == input['username']:
                return json({"message": "Username already exists...!",
                             "error": "username"}, status=409)
            elif existing[1] == input['email']:
                return json({"message": "Email already exists...!",
                             "error": "email"}, status=409)
        # Encrypt Password

        # Argon verification is not working
        # ph = PasswordHasher()
        # hash = ph.hash(input['password'])
        logger.info("POST user request for '{}'".format(input["username"]))
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

    @scoped(['admin'])
    async def delete(self, request, username):
        try:
            res = await User.filter(username=username).get_or_none()
            if not res:
                return json({"message": "User does not exist...! 😕", "error": "empty"}, status=404)
            await User.filter(username=username).delete()
        except:
            raise DBAccessError
        return text("User deleted! 🗑️")
