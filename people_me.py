from dotenv import load_dotenv
load_dotenv(override=True)

import os
import hvac
vault=hvac.Client(
    url=os.getenv('VAULT_URL'),
    token=os.getenv('VAULT_TOKEN')
    )
creds=vault.read('oauthapp/creds/testauth')
access_token=creds['data']['access_token']


print(access_token)

