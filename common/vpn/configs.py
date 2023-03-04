import os
from sanic.exceptions import SanicException
from .protocols.wireguard import wgConfig
from common.models import River
import logging

async def Selector(servers, input, regen=False):
    # Match the protocol to the River's protocol
    protocol = await River.filter(river_id=input["river_id"]).get().values_list("protocol", flat=True)
    if protocol == "wireguard":

        public_key = await wgConfig(servers, input, regen)
    else:
        raise SanicException(
            "Error: Protocol not supported yet", status_code=400)
    return public_key

def getConfigFromFile(fileLocation):
    try:
        with open(fileLocation, "r") as config_file:
            config = config_file.read()
        # os.remove(fileLocation)
        return config
    except Exception as error:
        raise error

async def generateConfig(servers, input):
    # Match the protocol to the River's protocol
    public_key = await Selector(servers, input)
    config  =  getConfigFromFile("vpn.conf")

    return config, public_key

async def regenerateConfig(server, stream):
    logging.debug("Regenerating config for '{}'".format(server["name"]))
    await Selector(server, stream, regen=True)
    config = getConfigFromFile("vpnpeering.conf")
    return config
