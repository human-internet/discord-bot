from flask import Flask, jsonify, render_template, request, json
import jwt
from cryptography.hazmat.primitives import serialization
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request
import os
from flask_mysqldb import MySQL
import mysql.connector



app = Flask(__name__)



#SQL Config 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
 
mysql = MySQL(app)
#cursor = mysql.connection.cursor()
#end sql
#open database sql
#with app.app_context():
#        cursor = mysql.connection.cursor()
#cursor.execute(''' CREATE TABLE Users(ID NOT NULL PRIMARY KEY, Name VARCHAR(50) ''')

app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_BLACKLIST_ENABLED'] = True

jwt = JWTManager(app)
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/success")
def success_bot():
    url = request.url
    sliced = str(url).split('=')
    print(sliced[1])
    private_key = open('id_rsa', 'r').read()
    key = serialization.load_ssh_private_key(private_key.encode(), password=b'')

    #jwt.decode(jwt=sliced[1],key=key, algorithms=['HS256',])
    #try:
    #    verify_jwt_in_request()
    #except(ValueError, TypeError):
    #    return {'error': 'access token error'}, 401

    #verify exchange token --> get requestID, appUserID, country -- get request --
    #query requestID for sqllite 
    #adding role with requestID ( sqllite) - get username
    #add role to person discord library (prolly)
    return render_template("success.html")

@app.route("/failure" )
def failure_bot():
   return  render_template("failure.html")

@app.route("/homepage")
def homepage():
   return render_template("homepage.html")
#
if __name__ == "__main__":
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=22)
    app.run(host='0.0.0.0', port=6000)
    #app.run(host='18.225.5.208', port=5000)
    #app.run(debug=True)
    #host=18.225.5.208
