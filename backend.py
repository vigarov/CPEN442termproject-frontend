from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__,template_folder='./frontend/templates',static_folder='./frontend/static')

domain_of_passgate_api = "localhost:1234/"
passgate_api_reqcode_url = "requestcode"
passgate_api_authtoken= "authtoken1234"

auth_header = {'Authorization' : 'Bearer '+passgate_api_authtoken}
currentUsersAuthMap = {}

def authorize(uname,p):
    return True

@app.route('/', methods=['GET'])
def homepage_login():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    if(authorize(username,request.form['password'])):
        #result = requests.get(domain_of_passgate_api+passgate_api_reqcode_url, params=passgate_api_authtoken)
        json_answer =  json.loads('{"code":10}')#result.json()
        code = json_answer['code']
        currentUsersAuthMap.update({username:code})
        return render_template('login.html',numbers=code)
    else:
        return render_template('index.html') #could also change to show error, but doesn't matter for our PoC, since we don't hold actual users DB
