## Contains a bunch of database manulation tools...

import mysql.connector

"""
Connection to MySQL server.
"""

db=mysql.connector.connect(user="root",passwd="root",host="10.100.22.1",port="3307",database="fyp")
cursor=db.cursor()

def getUser(username):
    query="SELECT user_id,username,password from user WHERE username = '{}'".format(username)
    cursor.execute(query)
    res = cursor.fetchall()
    print(res)
    print(res[0][0])


getUser("elliot")

#print(db)