from sanic import Sanic
from sanic.response import text
from sanic_cors import CORS, cross_origin

app = Sanic(__name__)
cors = CORS(app, resources={"resources": r'/*', "origins": "*",
            "methods": ["GET", "POST", "HEAD", "OPTIONS"]})


@ app.route("/", methods=['GET', 'OPTIONS'])
def hello_world(request):
    return text("Hello, cross-origin-world!")


if __name__ == '__main__':
    app.run(dev=True)
