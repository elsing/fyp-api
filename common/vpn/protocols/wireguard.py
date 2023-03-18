from common.models import Stream
from common.errors import DBAccessError
import wgconfig
import wgconfig.wgexec as wgexec
import os


def cleanUp():
    #  Delete the temporary files
    try:
        os.remove("./vpnpeering.conf")
    except FileNotFoundError:
        pass
    except Exception as error:
        raise error


async def generateClient(wc, servers, input):
    psk = wgexec.generate_presharedkey()  # Generate PSK

    # Add relevant information to client config
    for server in servers:
        print("serverssss", server)
        wc.add_peer(server["public_key"])
        wc.add_attr(
            server["public_key"], "PresharedKey", psk)
        endpoint = server["endpoint"]+":"+str(server["port"])
        wc.add_attr(server["public_key"],
                    "Endpoint", endpoint)
        wc.add_attr(server["public_key"],
                    "AllowedIPs", server["tunnel"])
        wc.add_attr(server["public_key"],
                    "PersistentKeepalive", 25)
        # Write to file
        wc.write_file()
    return psk


def addPeerToFile(wc, public_key, psk, input, server):
    # Add new peer
    print("addPeerToFile", server)
    wc.add_peer(public_key)
    wc.add_attr(public_key, "PresharedKey", psk)
    wc.add_attr(
        public_key, "AllowedIPs", input["tunnel"])


async def addPeerToDB(server, public_key, psk, input):
    # Open existing server config
    with open("./vpnpeering.conf", "w") as config_file:
        config_file.write(server["config"])
    wc = wgconfig.WGConfig("./vpnpeering.conf")
    wc.read_file()

    # Add new peer to temp file
    addPeerToFile(wc, public_key, psk, input, server)
    wc.write_file()  # Adds to existing config

    # Update server config in DB
    # wc = wgconfig.WGConfig(".configs/wg_srv.conf")
    with open("./vpnpeering.conf", "r") as server_file:
        server_config = server_file.read()
        try:
            if server["status"] == "init":
                status = "init"
            else:
                status = "pendingUpdate"
            await Stream.filter(river_id=input["river_id"]).filter(role="server").update(config=server_config, status=status)
        except:
            raise DBAccessError


async def newConfig(servers, input):
    # Generate keys + set file
    private_key, public_key = wgexec.generate_keypair()
    wc = wgconfig.WGConfig("./vpn.conf")

    # Set Interface options
    wc.add_attr(None, "Address", input["ip"])
    if input["role"] == "client":
        # or input["role"] != "client":
        if input["port"] != 51820:
            wc.add_attr(None, 'ListenPort', input["port"])
    else:
        wc.add_attr(None, 'ListenPort', input["port"])
    wc.add_attr(None, "PrivateKey", private_key)

    # Add revelant information to file
    if input["role"] == "client":
        # Generate client config
        # Get existing server values from DB
        try:
            server = await Stream.filter(river_id=input["river_id"]).filter(role="server").get().values()

        except:
            raise DBAccessError

        # Add the server to the client config
        psk = await generateClient(wc, servers, input)

        # Add peer to server config
        await addPeerToDB(server, public_key, psk, input)

    # If just server network, add server to other servers and vice versa
    if input["role"] == "server":
        for server in servers:
            print("Server {}".format(server))
            psk = wgexec.generate_presharedkey()  # Generate PSK
            await addPeerToDB(server, public_key, psk, input)
            addPeerToFile(wc, server["public_key"], psk, input, server)

    # Write file
    cleanUp()
    wc.write_file()
    print("Config generated")

    return public_key


async def removePeer(server, stream):
    # Open existing server config
    with open("./vpnpeering.conf", "w") as config_file:
        config_file.write(server["config"])
    wc = wgconfig.WGConfig("./vpnpeering.conf")
    wc.read_file()

    # Remove peer
    wc.del_peer(stream["public_key"])
    wc.write_file()


async def wgConfig(servers, input, regenerate):
    if regenerate:
        return await removePeer(servers, input)
    else:
        return await newConfig(servers, input)
