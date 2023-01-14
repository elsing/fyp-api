import bcrypt
from sanic import Sanic
from sanic.response import text, json
from sanic.exceptions import SanicException
from sanic_restful_api import Resource, Api
from resources.Users import APIUsers
from tortoise.contrib.sanic import register_tortoise
from sanic_jwt import Initialize
from common.models import User
from argon2 import PasswordHasher
from sanic.log import logger


class AuthError(SanicException):
    message = "Either your password or username are wrong."
    status_code = 401
    quiet = True


app = Sanic(__name__)
app.config.KEEP_ALIVE_TIMEOUT = 30
api = Api(app)

register_tortoise(
    app, db_url="mysql://root:root@10.100.22.1:3307/fyp_v2", modules={"models": ["common.models"]}, generate_schemas=True
)


async def authenticate(request):
    # Get the username and password from the JSON request
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    # If there is no password or username, raise
    if not username or not password:
        raise SanicException("Missing information...!",
                             status_code=400, quiet=True)

    # Get the user object from DB and verifiy their password
    user = await User.filter(username=username).get_or_none().values()

    # Check user exists and then check their password
    if not user:
        print("not user")
        raise AuthError

    print(password)
    password = password.encode("utf-8")
    if bcrypt.checkpw(password, user['password'].encode("utf-8")):
        print("success")
    else:
        raise Exception
        raise AuthError

    # Return details if successful
    return user


async def scope_extender(user):
    return user['permission']


def load_details(payload, user):
    payload.update(
        {"first_name": user['first_name'], "last_name": user["last_name"]})
    return payload


Initialize(
    app,
    authenticate=authenticate,
    secret="7N3%WZrjj$eDYC7czPyP",
    add_scopes_to_payload=scope_extender,
    extend_payload=load_details,
    access_token_name="auth_token",
    cookie_set=True,
    cookie_secure=False,
    cookie_domain="",
    cookie_token_name="auth_token",
    cookie_split_signature_name="auth_token_signature",
    cookie_split=True,
    cookie_strict=False)

api.add_resource(APIUsers, '/users', '/users/<username>',
                 '/user', '/user/<username>')

if __name__ == '__main__':
    app.run(debug=True)
