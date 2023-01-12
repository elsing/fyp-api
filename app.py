from sanic import Sanic
from sanic.response import text
from sanic_restful_api import Resource, Api
#from sanic_mysql import ExtendMySQL
from resources.Users import Users

#from auth import procted



app = Sanic(__name__)
#app.config.update(dict(MYSQL=dict(host='10.100.22.1', port=3307, user='root', password='root',db='fyp')))
#ExtendMySQL(app, auto=True, user='root', host=hostname, port="3307", password='root', db='fyp', autocommit=True)

app.config.KEEP_ALIVE_TIMEOUT=30
#app.config.SECRET = "1234"

api = Api(app)


#ExtendMySQL(app, user="root", host=10.100.22.1, port="3307", password="root", autocommit=True)

class HelloWorld(Resource):
    async def get(self, request):
        args = parser.parse_args(request)
        return 
        #print(request)

#api.add_resource(HelloWorld, '/')

# class GetUser(Resource):
#     async def get(self, request):
#         val = await request.app.mysql.query("SELECT user_id,username,password from user WHERE username = 'test'")
#         return text(val)

#@app.get("/secret")
#@protected
#@authorised()
#api.add_resource(GetUser, '/user')
api.add_resource(Users, '/users', '/users/<username>')

if __name__ == '__main__':
    app.run(debug=True)