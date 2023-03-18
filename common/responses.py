from sanic import json


def successResponse(data, status=200):
    return json({"description": "Success Message", "message": data}, status=status)
