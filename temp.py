from python_wireguard import Key
import wgconfig

test = ""

private, public = Key.key_pair()

wc = wgconfig.WGConfig(test)

wc.add_attr(None, 'PrivateKey', private)

print(wc)

# wc.write
# print(test)
