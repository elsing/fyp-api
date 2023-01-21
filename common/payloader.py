import base64
import json


async def getData(request):
    cookies = request.cookies
    auth_token = cookies.get("auth_token")
    b64_payload = auth_token.split(".")[1]
    b64_padding = len(b64_payload) % 4
    b64_payload += "="*b64_padding
    return json.loads(base64.b64decode(b64_payload).decode("utf-8"))
