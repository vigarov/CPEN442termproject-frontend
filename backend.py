import json
import random
import secrets
from flask import Flask, render_template, request, abort, redirect, url_for
import requests
from datetime import datetime
from Cryptodome.Hash import SHA256
import os

app = Flask(__name__, template_folder='./frontend/templates', static_folder='./frontend/static')

# ngrok http https://localhost:5002
domain_of_passgate_api = "https://68ef-176-100-43-178.ngrok.io" + '/'
passgate_api_reqcode_url = "requestcode"
passgate_api_reqsms = "requestsms"

passgate_api_authtoken = "5iv3TYphzQu-ZEoWgpMaGp7RRHXeEWsQzc7A9h2RKL4"
auth_header = {'Authorization': 'Bearer ' + passgate_api_authtoken}

CST_userPhoneNumber = "+33768807740"

tokenDataMap = {}


def authorize(uname, p):
    return True


def get_time():
    return datetime.now().strftime("%H:%M:%S,%f")


@app.route('/', methods=['GET'])
def homepage_login():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    got_req = get_time()
    log = {'START_user_pressed_login': got_req}
    pn = str(request.form['phone'])
    h = SHA256.new()
    h.update(pn.encode('utf-8'))
    log['hashed_phone'] = h.hexdigest()
    if authorize(pn, str(request.form['password'])):
        requestedTimeout = 50
        requestRecieve = 'Receive' in request.form.keys() and str(request.form['Receive']) == 'on'
        if not requestRecieve:
            log['call'] = 'true'
            payload = {'phone': pn, 'to': str(requestedTimeout)}
            log['sent_passgate_info_request'] = get_time()
            result = requests.get(domain_of_passgate_api + passgate_api_reqcode_url, params=payload,
                                  headers=auth_header)
            log['received_passgate_info_answer'] = get_time()
            json_answer = result.json()
            code = int(json_answer['code'])
            timeout = float(json_answer['timeout'])  # in seconds
            response_at = str(json_answer['response_at'])
            generatedToken = str(secrets.token_urlsafe(32))
            while generatedToken in tokenDataMap.keys():
                generatedToken = str(secrets.token_urlsafe(32))
            tokenDataMap.update({generatedToken: (code, timeout, response_at, log)})
            ret = render_template('2fa.html', digit1=int((code / 10) % 10), digit2=(code % 10), phone_number=pn,
                                  timeout=timeout, token=generatedToken)
            return ret
        else:
            log['call'] = 'false'
            payload = {'phone': pn}
            generatedToken = str(random.randint(0, 100))  # used only for state keeping/logging ; === request uid
            while generatedToken in tokenDataMap.keys():
                generatedToken = str(random.randint(0, 100))
            log['sent_passgate_info_request'] = get_time()
            result = requests.get(domain_of_passgate_api + passgate_api_reqsms, params=payload, headers=auth_header)
            log['received_passgate_info_answer'] = get_time()
            tokenDataMap.update({generatedToken: ('SMS->unused', -1, 'SMS->unused', log)})
            return render_template('SMS.html', response_at='auth/' + str(result.json()['token']) + '/SMS',
                                   token=generatedToken)
    else:
        return render_template(
            'index.html')  # could also change to show error, but doesn't matter for our PoC, since we don't hold actual users DB


def save_log(log):
    filename = 'logs/' + log['hashed_phone'][:6] + '/' + datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as out_file:
        out_file.write(json.dumps(log))


@app.route('/auth_check/<token>')
def verify_auth(token):
    req_time = get_time()
    val = tokenDataMap.get(token)
    if val is None:
        # return error page
        abort(404)
    (code, timeout, response_at, log) = val
    log['CALLONLY_user_page_loaded'] = req_time
    log['CALLONLY_sending_passgate_call_request'] = get_time()
    result = requests.get(domain_of_passgate_api + response_at, headers=auth_header)
    log['END_received_passgate_answer'] = get_time()
    json_answer = result.json()  # json.loads('{"authorized":true}')
    auth = json_answer['authorized']
    log['success'] = auth
    save_log(log)
    if auth:
        # success, continue with authentication
        # remove token from map
        del tokenDataMap[token]
        return render_template('success.html', success='true')
    else:
        # failed auth
        # TODO: decide if we directly remove token from map - depending if that's what our API will do
        return render_template('success.html', success='false')


@app.route('/verify_code', methods=['POST'])
def check_code():
    rec_time = get_time()
    value = tokenDataMap[request.form['token']]
    assert value is not None
    (a, b, c, log) = value
    log['received_input'] = rec_time
    input_code = request.form['code']  # crashes if 'code' not present
    response_at = request.form['response_at']
    log['SMSONLY_sending_passgate_verification_request'] = get_time()
    result = requests.get(domain_of_passgate_api + response_at + '?code=' + str(input_code), headers=auth_header)
    log['END_received_passgate_answer'] = get_time()
    json_answer = result.json()
    auth = json_answer['authorized']
    log['success'] = auth
    save_log(log)
    if auth:
        return render_template('success.html', success='true')
    else:
        # failed auth
        return render_template('success.html', success='false')


@app.route('/cancel')
def cancel_req():
    value = tokenDataMap[request.form['token']]
    assert value is not None
    (a, b, c, log) = value
    log['CANCEL_END'] = get_time()
    save_log(log)
    return redirect(url_for('homepage_login'))


if __name__ == '__main__':
    app.run(threaded=True, port=5001)
