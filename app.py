import bcrypt
from sanic import Sanic, Websocket
from sanic.response import text, json, empty
from sanic.exceptions import SanicException
from sanic_restful_api import Api
from sanic_ext import Extend, cors
from common.responses import successResponse
from resources.Users import APIUsers
from resources.Deltas import APIDeltas, APIDeltaRivers
from resources.Rivers import APIRivers, APIRiversStreams
from resources.Streams import APIStreams
from resources.Flows import APIFlows
from tortoise.contrib.sanic import register_tortoise
from sanic_jwt import Initialize
from common.models import User
from sanic.log import logger
from resources.Daemons import DaemonWSS


class AuthError(SanicException):
    message = "Either your password or username are wrong."
    status_code = 401
    quiet = True


app = Sanic(__name__)
api = Api(app)

# Set CORS options
app.config.KEEP_ALIVE_TIMEOUT = 30
app.config.FALLBACK_ERROR_FORMAT = "json"
# Cors settings
app.config.CORS_ORIGINS = "https://watershed.singer.systems"
# app.config.CORS_ORIGINS = "*"
app.config.CORS_SUPPORTS_CREDENTIALS = True
app.config.CORS_METHODS = ["GET", "POST", "OPTIONS", "PATCH"]
app.config.CORS_HEADERS = "content-type"
app.config.CORS_EXPOSE_HEADERS = "content-type"
Extend(app)

register_tortoise(
    app, db_url="mysql://root:root@10.100.22.1:3307/fyp_v2", modules={"models": ["common.models"]}, generate_schemas=True
)

# Auth function


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


# Add the users scopes to the payload
async def scope_extender(user):
    return user['permission']


# Loads the users details into the payload
def load_details(payload, user):
    payload.update(
        {"first_name": user['first_name'], "last_name": user["last_name"], "username": user["username"]})
    return payload


# WorkerManager.THRESHOLD = 600
# Sanic.start_method = "fork"


Initialize(
    app,
    authenticate=authenticate,
    # This should to changed in production to ENV variable
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
    cookie_samesite=None,
    cookie_max_age=3600,
    expiration_delta=60*5*12)

api.add_resource(APIUsers, '/users', '/users/<username>',
                 '/user', '/user/<username>')

api.add_resource(APIDeltas, '/deltas', '/deltas/<delta_id>',
                 '/delta', '/delta/<delta_id>')

api.add_resource(APIDeltaRivers, '/delta/<delta_id>/rivers',
                 '/deltas/<delta_id>/rivers')

api.add_resource(APIRivers, '/rivers', '/rivers/<river_id>',
                 '/river', '/river/<river_id>',)

api.add_resource(APIRiversStreams, '/river/<river_id>/streams/<stream_id>', '/river/<river_id>/streams',
                 '/rivers/<river_id>/streams/<stream_id>', '/rivers/<river_id>/streams')

api.add_resource(APIFlows, '/flows', '/flows/<flow_id>',
                 '/flow', '/flow/<flow_id>')

api.add_resource(APIStreams, '/streams', '/streams/<stream_id>',
                 '/stream', '/stream/<stream_id>')


@app.websocket("/websocket")
async def websocket_handler(request, ws: Websocket):
    await DaemonWSS(request, ws)


@app.route("/auth/logout")
async def test(request):
    print(request)
    response = successResponse(
        "The cookie monster will be satisfied. Thank you...!")
    toDelete = ["auth_token", "auth_token_signature"]
    for cookie in toDelete:
        response.cookies[cookie] = ""
        response.cookies[cookie]["max-age"] = 0
        response.cookies[cookie]["domain"] = "singer.systems"
        response.cookies[cookie]["path"] = "/"
    return response

if __name__ == '__main__':
    # app.run(dev=True, host="0.0.0.0", port=8000, workers=1)
    app.run(host="0.0.0.0", port=8000, workers=1)
