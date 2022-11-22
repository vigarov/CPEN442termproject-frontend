import secrets

from flask import Flask, render_template, request, abort
import requests
import json
import time

app = Flask(__name__,template_folder='./frontend/templates',static_folder='./frontend/static')

#ngrok http https://localhost:5000
domain_of_passgate_api = "https://ac33-128-189-144-134.ngrok.io"+'/'
passgate_api_reqcode_url = "requestcode"

passgate_api_authtoken= "5iv3TYphzQu-ZEoWgpMaGp7RRHXeEWsQzc7A9h2RKL4"
auth_header = {'Authorization' : 'Bearer '+passgate_api_authtoken}

CST_userPhoneNumber = "+33768807740"

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
    username = str(request.form['username'])
    if(authorize(username,str(request.form['password']))):
        pn = str(getUserPhoneNumber(username))
        requestedTimeout = 50
        payload = {'username':username,'phone':pn,'to':str(requestedTimeout)}
        result = requests.get(domain_of_passgate_api+passgate_api_reqcode_url,params=payload,headers=auth_header)

        json_answer = result.json()
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
    result = requests.get(domain_of_passgate_api+response_at,headers=auth_header)
    json_answer = result.json()#json.loads('{"authorized":true}')
    auth = json_answer['authorized']
    if(auth):
        #success, continue with authentication
        # remove token from map
        del tokenDataMap[token]
        return render_template('success.html',success='true')
    else:
        #failed auth
        # TODO: decide if we directly remove token from map - depending if that's what our API will do
        return render_template('success.html',success='false')


if __name__ == '__main__':
    app.run(threaded=True, port=5001)
