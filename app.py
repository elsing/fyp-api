import bcrypt
from sanic import Sanic
from sanic.response import text, json, empty
from sanic.exceptions import SanicException
from sanic_restful_api import Resource, Api
from sanic_ext import Extend, cors
from sanic_cors import CORS
from resources.Users import APIUsers
from resources.Flows import APIFlows
from resources.Streams import APIStreams
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
api = Api(app)

app.config.KEEP_ALIVE_TIMEOUT = 30
app.config.FALLBACK_ERROR_FORMAT = "json"
# Cors settings
app.config.CORS_ORIGINS = "https://watershed.singer.systems,https://api.singer.systems"
app.config.CORS_SUPPORTS_CREDENTIALS = True
app.config.CORS_METHODS = ["GET", "POST", "OPTIONS"]
app.config.CORS_HEADERS = "content-type"
app.config.CORS_EXPOSE_HEADERS = "content-type"
Extend(app)

register_tortoise(
    app, db_url="mysql://root:root@10.100.22.1:3307/fyp_v2", modules={"models": ["common.models"]}, generate_schemas=True
)


async def authenticate(request):
    # Get the username and password from the JSON request
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        print(request.json)
    except:
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
        raise AuthError

    # Return details if successful
    return user


async def scope_extender(user):
    return user['permission']


def load_details(payload, user):
    payload.update(
        {"first_name": user['first_name'], "last_name": user["last_name"], "username": user["username"]})
    return payload


Initialize(
    app,
    authenticate=authenticate,
    secret="7N3%WZrjj$eDYC7czPyP",
    add_scopes_to_payload=scope_extender,
    extend_payload=load_details,
    access_token_name="auth_token",
    cookie_set=True,
    cookie_secure=True,
    cookie_domain="singer.systems",
    cookie_path="/",
    cookie_token_name="auth_token",
    cookie_split_signature_name="auth_token_signature",
    cookie_split=True,
    cookie_strict=False,
    cookie_samesite=None)

api.add_resource(APIUsers, '/users', '/users/<username>',
                 '/user', '/user/<username>')

api.add_resource(APIFlows, '/flows', '/flows/<flow>',
                 '/flow', '/flow/<flow>')

api.add_resource(APIStreams, '/streams', '/streams/<stream>',
                 '/stream', '/stream/<stream>')


@app.route("/auth/logout")
async def test(request):
    print(request)
    response = text("The cookie monster will be satisfied. Thank you...!")
    toDelete = ["auth_token", "auth_token_signature"]
    for cookie in toDelete:
        response.cookies[cookie] = ""
        response.cookies[cookie]["max-age"] = 0
        response.cookies[cookie]["domain"] = "singer.systems"
        response.cookies[cookie]["path"] = "/"
    return response

if __name__ == '__main__':
    app.run(dev=True, host="0.0.0.0", port=8000, workers=1)
