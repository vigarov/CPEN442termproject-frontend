import secrets

from flask import Flask, render_template, request, abort
import requests
import json
import time

app = Flask(__name__,template_folder='./frontend/templates',static_folder='./frontend/static')

domain_of_passgate_api = "localhost:1234/"
passgate_api_reqcode_url = "requestcode"

passgate_api_authtoken= "authtoken1234"
auth_header = {'Authorization' : 'Bearer '+passgate_api_authtoken}
s = requests.Session()
s.headers.update(auth_header)

CST_userPhoneNumber = "+15875906624"

tokenDataMap = {}

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
        pn = getUserPhoneNumber(username)
        #result = s.get(domain_of_passgate_api+passgate_api_reqcode_url, params={'username':username,'phone'=pn})
        json_answer = json.loads('{"code":10,"timeout":60,"response_at":"abcd"}')#result.json()
        code = int(json_answer['code'])
        timeout = float(json_answer['timeout']) # in seconds
        response_at = str(json_answer['response_at'])
        generatedToken = str(secrets.token_urlsafe(32))
        tokenDataMap.update({generatedToken:(username,code,timeout,response_at)})
        ret = render_template('2fa.html',digit1=int((code/10)%10),digit2=(code%10),phone_number=pn,timeout=timeout,token=generatedToken)
        return ret
    else:
        return render_template('index.html') #could also change to show error, but doesn't matter for our PoC, since we don't hold actual users DB


@app.route('/auth_check/<token>')
def verify_auth(token):
    val = tokenDataMap.get(token)
    if val is None:
        # return error page
        abort(404)
    (username, code, timeout, response_at) = val
    #result = s.get(domain_of_passgate_api+response_at)
    json_answer = json.loads('{"authorized":true}') #result.json()
    time.sleep(20) # remove once API implemented
    auth = json_answer['authorized']
    if(auth):
        #success, continue with authentication
        # remove token from map
        del tokenDataMap[token]
        return render_template('success.html')
    else:
        #failed auth
        # TODO: decide if we directly remove token from map - depending if that's what our API will do
        abort(403)
