import bcrypt
import json as jsonmod
import base64
import wgconfig
import wgconfig.wgexec as wgexec
import wireguard
from sanic_restful_api import Resource
from sanic import text, json
from sanic.log import logger
from sanic.exceptions import SanicException
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from marshmallow import ValidationError
# from argon2 import PasswordHasher
from common.models import Stream, StreamValidation, River
from common.errors import DBAccessError, BadRequestError
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist


from common.payloader import getData


def getServerConfig(server):
    with open(".configs/wg-temp.conf", "w") as config_file:
        config_file.write(server["config"])
    wc = wgconfig.WGConfig(".configs/wg-temp.conf")
    wc.read_file()
    return wc


def streamNotNull(stream):
    if stream == "":
        raise SanicException(
            "Stream or stream not specified...!", status_code=404)


class APIStreams(Resource):
    method_decorators = [protected()]

    async def get(self, request, stream_id=""):
        river_id = stream_id
        streamNotNull(stream_id)

        logger.info("GET stream request for '{}'".format(river_id))

        # temp = await Stream.filter(stream_id=1).values("stream_id", flow="flow__name")

        # temp = await Stream.raw("SELECT * FROM stream INNER JOIN flow ON stream.flow_id_id = flow.flow_id WHERE stream.stream_id_id = 1")

        temp = await Stream.filter(river_id=river_id).values()

        print(temp)
        # temp = await Org.filter(org_id=1).prefetch_related("flows").values()

        return temp

        try:
            stream = await Stream.filter(stream_id_id=stream_id).all().values()
        except ValueError:
            raise BadRequestError
        except:
            raise DBAccessError

        # Return JSON of specified stream
        if stream:
            return stream

        raise SanicException("Stream not found...! :( 🔍", status_code=404)

    async def post(self, request, stream_id=""):
        # Get user_id from request
        user_data = await getData(request)
        user_id = user_data["user_id"]

        # Validate the data
        try:
            input = StreamValidation().load(request.json)
        except ValidationError as err:
            raise SanicException("Error: {}".format(
                err.messages), status_code=400)

        # Pre checks
        try:
            existing_server = await Stream.filter(river_id=input["river_id"]).filter(role="server").get_or_none()
            if existing_server:
                if input["role"] == "server":
                    raise SanicException(
                        "Error: A server already exists for this river", status_code=400)
            else:
                if input["role"] == "client":
                    raise SanicException(
                        "Error: A server must be created first", status_code=400)
            protocol = await River.filter(river_id=input["river_id"]).get().values_list("protocol", flat=True)
        except SanicException as err:
            raise err
        except:
            raise DBAccessError

        # Generate VPN config
        if protocol == "wireguard":
            # Set Interface options
            private_key, public_key = wgexec.generate_keypair()
            wc = wgconfig.WGConfig(
                ".configs/wg-generating.conf")
            wc.add_attr(None, "Address", input["ip"])
            if input["role"] == "client":
                # or input["role"] != "client":
                if input["port"] != 51820:
                    wc.add_attr(None, 'ListenPort', input["port"])
            else:
                wc.add_attr(None, 'ListenPort', input["port"])
            wc.add_attr(None, "PrivateKey", private_key)
            # Generate client config
            if input["role"] == "client":
                psk = wgexec.generate_presharedkey()
                try:
                    server = await Stream.filter(river_id=input["river_id"]).filter(role="server").get().values()

                except:
                    raise DBAccessError
                wc.add_peer(server["public_key"])
                wc.add_attr(
                    server["public_key"], "PresharedKey", psk)
                endpoint = server["endpoint"]+":"+str(server["port"])
                wc.add_attr(server["public_key"],
                            "Endpoint", endpoint)
                wc.add_attr(server["public_key"],
                            "AllowedIPs", input["tunnel"])
                wc.add_attr(server["public_key"],
                            "PersistentKeepalive", 25)

                # Add peer to server config
                server_file = getServerConfig(server)
                server_file.add_peer(public_key)
                server_file.add_attr(public_key, "PresharedKey", psk)
                server_file.add_attr(
                    public_key, "AllowedIPs", input["tunnel"])
                server_file.write_file()
                server_file = wgconfig.WGConfig(".configs/wg_srv.conf")
                with open(".configs/wg-temp.conf", "r") as server_file:
                    server_config = server_file.read()
                    # Update DB with new config
                    try:
                        await Stream.filter(river_id=input["river_id"]).filter(role="server").update(config=server_config)
                    except:
                        raise DBAccessError
            # Write file
            wc.write_file()

            # Read the file to get the config
            with open(".configs/wg-generating.conf", "r") as config_file:
                config = config_file.read()

        else:
            raise SanicException(
                "Error: Protocol not supported yet", status_code=400)
        try:
            await Stream.create(flow_id=input["flow_id"], river_id=input["river_id"], name=input["name"], role=input["role"], port=input["port"], config=config, public_key=public_key, ip=input["ip"], endpoint=input["endpoint"], tunnel=input["tunnel"], error=input["error"])
            pass
        except:
            raise DBAccessError

        logger.info("Stream created")
        return json("Stream created ✅", status=201)

    async def patch(self, request, stream_id=""):
        streamNotNull(stream_id)

    async def delete(self, request, stream_id=""):
        streamNotNull(stream_id)
