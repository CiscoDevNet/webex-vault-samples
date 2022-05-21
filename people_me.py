from dotenv import load_dotenv
load_dotenv(override=True)

import os
import hvac
vault=hvac.Client(
    url=os.getenv('VAULT_ADDR'),
    token=os.getenv('VAULT_TOKEN')
    )

creds=vault.read('oauthapp/creds/testauth')
access_token=creds['data']['access_token']

import requests
response=requests.get('https://webexapis.com/v1/people/me', headers={'Authorization': f'Bearer {access_token}'})
print('User displayName: ' + response.json()['displayName'])

