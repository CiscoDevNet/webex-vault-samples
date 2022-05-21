from dotenv import load_dotenv
load_dotenv(override=True)

import os
appOAuthServer=os.getenv('OAUTH_SERVER')
appOAuthCredential=os.getenv('OAUTH_CRED')
appOAuthRedirectUrl=os.getenv('OAUTH_REDIRECT_URL')

import hvac
vault=hvac.Client(
    url=os.getenv('VAULT_ADDR'),
    token=os.getenv('VAULT_TOKEN')
    )

import uuid
from flask import Flask,redirect,request,session
app = Flask(__name__)
app.secret_key=str(uuid.uuid4())

from flask_session import Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

import requests

@app.route('/')
def index():
    creds=vault.read(f'oauthapp/creds/{appOAuthCredential}')
    if creds is None:
        state=str(uuid.uuid4())
        session['state']=state
        response=vault.write(f'oauthapp/auth-code-url', server=appOAuthServer,
            redirect_url=appOAuthRedirectUrl,
            scopes='spark:people_read',
            state=state)
        url=response['data']['url']
        href=f"location.href='{url}'"
        return f'<p>Unauthorized! <button onclick="{href}">Authorize</button></p>'
    access_token=creds['data']['access_token']
    response=requests.get('https://webexapis.com/v1/people/me', headers={'Authorization': f'Bearer {access_token}'})
    displayName=response.json()['displayName']
    return f'<p>Authorized!  User display name: {displayName}</p>'

@app.route('/auth')
def auth():
    code=request.args.get('code')
    state=request.args.get('state')
    if not state == session.get('state'):
        return 'Mismatched state'
    response=vault.write(f'oauthapp/creds/{appOAuthCredential}',
        server=appOAuthServer,
        redirect_url=appOAuthRedirectUrl,
        code=code)
    return redirect('/')