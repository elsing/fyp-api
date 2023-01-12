import asyncio
import json
import aiomysql
import uvloop

from functools import wraps
from sanic.exceptions import SanicException
from sanic_restful_api import Resource, reqparse, abort
from marshmallow import Schema, fields, ValidationError, INCLUDE
# import email_validator

from sanic import text, json
from sanic.log import logger


class UnauthorisedError(SanicException):
    message = "Unauthorised access...!"
    status_code = 401
    quiet = True


class DBAccessError(SanicException):
    message = "DB access error...!"
    status_code = 500
    quiet = False


class User(Schema):
    org_id = fields.Int(load_default=1)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, )
    first_name = fields.Str(required=True)
    last_name = fields.Str(load_default="")
    permission = fields.Str(load_default="")


def authorised(f):
    @wraps(f)
    async def wrapper(request, username):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('api_key', location='headers', type=str,
                            required=True, help='Please provide an API access key.')
        args = parser.parse_args(request)
        logger.info(args['api_key'])

        if args['api_key']:
            # MySQL
            try:
                loop = asyncio.get_event_loop()
                conn = await aiomysql.connect(host='10.100.22.1', port=3307,
                                              user='root', password='root',
                                              db='fyp', loop=loop)
                async with conn.cursor() as cur:
                    res = await cur.execute('SELECT API_key from panel WHERE API_key = "{}"'.format(args['api_key']))
                res = await cur.fetchall()
                await cur.close()
            except:
                raise DBAccessError
            for ans in res:
                if res[0][0] == args['api_key']:
                    logger.info("Authorised!")
                    return await f(request, username)
            raise UnauthorisedError
    return wrapper


# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Users(Resource):
    method_decorators = [authorised]

    async def get(self, request, username, *args):
        if not args:
            local = False
        else:
            local = True
        logger.info("GET username request for '{}'".format(username))
        parser = reqparse.RequestParser()
        try:
            loop = asyncio.get_event_loop()
            conn = await aiomysql.connect(host='10.100.22.1', port=3307,
                                          user='root', password='root',
                                          db='fyp', loop=loop)
            async with conn.cursor() as cur:
                res = await cur.execute('SELECT username,password,first_name,last_name from user WHERE username = "{}"'.format(username))
            res = await cur.fetchall()
            await cur.close()
        except:
            raise DBAccessError
        logger.info("GetUser res")
        logger.info(res)
        for ans in res:
            return {"username": ans[0], "password": ans[1], "first_name": ans[2], "second_name": ans[3]}
        if local != True:
            raise SanicException("User not found...",
                                 status_code=404, quiet=True)

    async def post(self, request, *username):
        try:
            input = User().load(request.json)
        except ValidationError as err:
            logger.info("Error")
            logger.info(err.messages)
            raise SanicException("Error: {}".format(
                err.messages), status_code=400, quiet=True)
        logger.info("POST user request for '{}'".format(input["username"]))
        try:
            res = await self.get(request, input['username'], 1)
        except:
            raise DBAccessError
        if res:
            raise SanicException("Username already exists...",
                                 status_code=409, quiet=True)

        try:
            loop = asyncio.get_event_loop()
            conn = await aiomysql.connect(host='10.100.22.1', port=3307,
                                          user='root', password='root',
                                          db='fyp', loop=loop)
            async with conn.cursor() as cur:
                res = await cur.execute('INSERT into user (org_id, username, email, password, first_name, last_name, permission) VALUES ({0}, "{1}", "{2}", "{3}", "{4}", "{5}", "{6}")'.format(input["org_id"], input["username"], input["email"], input["password"], input["first_name"], input["last_name"], input["permission"]))
            await conn.commit()
            await cur.close()
        except:
            raise DBAccessError
        logger.info("User added with username: {}".format(input["username"]))
        raise SanicException("User added!", status_code=201, quiet=True)

    async def delete(self, request, username):
        try:
            input = User(only="username").load(request.json)
        except ValidationError as err:
            logger.info("Error")
            logger.info(err.messages)
            raise SanicException("Error: {}".format(
                err.messages), status_code=400, quiet=True)
        logger.info(input)
        # try:
        #     res = await self.get(request, input['username'], 1)
        # except: raise DBAccessError
