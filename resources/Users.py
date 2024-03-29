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
from common.models import User, UserValidation
from common.errors import DBAccessError, UnauthorisedError
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist


def userNotNull(username):
    if username == "":
        raise SanicException(
            "User not specified...! Use /user(s)/USER", status_code=404)

# class AuthenticationHeaders(Schema):
#     username = fields.Str()
#     password = fields.Str()
#     session_key = fields.Str(required=True, error_messages={
#         "required": "No key included in request."})

#     class Meta:
#         unknown = EXCLUDE


class APIUsers(Resource):
    method_decorators = [protected()]

    @scoped(['admin'])
    async def get(self, request, username=""):
        # Make sure username is not empty
        userNotNull(username)
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
        raise SanicException("User not found...! :( 🔍", status_code=404)

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
                raise SanicException("Username already exists...!",
                                     status_code=409)
            elif existing[1] == input['email']:
                raise SanicException("Email already exists...!",
                                     status_code=409)
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
        except:
            raise DBAccessError
        # Log and return success
        logger.info("User added with username: {}".format(input["username"]))
        return text("User added! ✅", status=201)

    @scoped(['admin'])
    async def delete(self, request, username=""):
        userNotNull(username)
        try:
            res = await User.filter(username=username).get_or_none()
            if not res:
                raise SanicException(
                    "User does not exist...! 😕", status_code=404)
            await User.filter(username=username).delete()
        except:
            raise DBAccessError
        return text("User deleted! 🗑️")
