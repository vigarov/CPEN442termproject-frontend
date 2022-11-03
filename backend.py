from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__,template_folder='./frontend/templates',static_folder='./frontend/static')

domain_of_passgate_api = "localhost:1234/"
passgate_api_reqcode_url = "requestcode"
passgate_api_authtoken= "authtoken1234"

CST_userPhoneNumber = "+15875906624"

auth_header = {'Authorization' : 'Bearer '+passgate_api_authtoken}
currentUsersAuthMap = {}

def authorize(uname,p):
    return True

def getUserPhoneNumber(uname):
    return CST_userPhoneNumber

@app.route('/', methods=['GET'])
def homepage_login():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    if(authorize(username,request.form['password'])):
        #result = requests.get(domain_of_passgate_api+passgate_api_reqcode_url, params=passgate_api_authtoken)
        json_answer =  json.loads('{"code":10,"timeout":0.2}')#result.json()
        code = int(json_answer['code'])
        pn = getUserPhoneNumber(username)
        timeout = float(json_answer['timeout'])
        currentUsersAuthMap.update({username:(code,timeout)})
        return render_template('2fa.html',digit1=int((code/10)%10),digit2=(code%10),phone_number=pn,timeout=timeout)
    else:
        return render_template('index.html') #could also change to show error, but doesn't matter for our PoC, since we don't hold actual users DB
