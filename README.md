# webex-vault-samples

Python samples demonstrating how to use Vault + vault-plugin-secrets-oauthapp to manage and refresh Webex user access tokens

## Requirements

These samples were developed using:

* Ubuntu 22.04

* Docker 20.10

* Python 3.10

* Visual Studio Code 1.67

## Available Samples

* **people_me.py** - A simple run-once console application the retrieves an already full authorized access token from Vault for the configured server/credential and uses it to make a Webex REST API request.

* **people_me_flask.py** - A more complete sample web application that checks for the existence of the required credential, and if not found retrieves/launches the OAuth2 flow URL and creates the needed oauthapp credential in Vault.

## Pre-Configuration

1. Download and un-compress the [vault-plugin-secrets-oauthapp](https://github.com/puppetlabs/vault-plugin-secrets-oauthapp/releases) Vault plugin

1. Copy the plugin to the configured [plugin_directory](https://www.vaultproject.io/docs/configuration) on the Vault server.

1. Register the oauthapp plugin via the[ Vault CLI](https://www.vaultproject.io/docs/commands) - don't forget to `vault login` first (see [Vault Docs: Plugins](https://www.vaultproject.io/docs/plugins/plugin-management))

   or simply restart Vault.

1. Enable the oauthapp plugin:

   ```
   vault secrets enable oauthapp
   ```

## Configuring a Webex OAuth2 Integration Server on Vault

1. Create a new Webex Integration at Webex for Developers: https://developer.webex.com/my-apps

   Specify the **Redirect URI** as: `http://localhost/5000/auth`

   and select just the **Scope**: `spark:people_read`

   Be sure to save the displayed **Client ID** and **Client Secret** for the Integration.

1. From the Vault CLI, create a new custom oauthapp server (here named `webex-myapp`) for your Webex Integration.  Substitute your Cliend ID/Client Secret:

   ```
   vault write oauthapp/servers/webex-myapp provider=custom client_id=<client_id> client_secret=<client_secret> provider_options=auth_code_url="https://webexapis.com/v1/authorize" provider_options=token_url="https://webexapis.com/v1/access_token"
   ```

## Testing the Webex OAuth2 Grant Flow

1. Request an authorization code flow URL:

   ```
   vault write oauthapp/auth-code-url server=webex-myapp redirect_url="http://localhost:5000/auth" scopes="spark:people_read" state="12345"
   ```

   You should receive a response containing the generated URL:

   ```
   Key    Value
   ---    -----
   url    https://webexapis.com/v1/authorize?client_id=C34e443dd5a9redactedd7e29ec25cff9&redirect_uri=http%3A%2F%2Flocalhost%3A5000&response_type=code&scope=spark%3Apeople_read&state=12345
   ```
      
1. Open the URL in a browser and complete the Webex authentication sequence.

   As there (should be) no web browser listening at localhost:5000, the browser will display an error.  However, the URL in the address bar will now include a the returned `?code=` parameter.

   Copy this code for the next step (be sure not to grab the `&state=12345` part at the end of the URL.)

1. Exchange the authorization code and store the actual access token in a new credential named `testauth`:

   ```
   vault write oauthapp/creds/testauth server=webex-myapp code=NGFhMjJmMjYtNGY1MCredactedad72cae0e10f redirect_url="http://localhost:5000/auth"
   ```

1. Test retrieving an access token for this credential:

   ```
   vault read oauthapp/creds/testauth
   ```

   You should see the access token in the response:

   ```
   Key             Value
   ---             -----
   access_token    MGJkZjYyMTAtYjkcwLTgwOTItOTQredactedd-048f151d8d6b
   expire_time     2022-06-04T01:53:26.839079729Z
   server          webex-myapp
   type            Bearer
   ```

1. You can delete the credential from Vault via:

   ```
   vault delete oauthapp/creds/testauth
   ```

   > **Note:** This does not revoke the actual Webex access token

## Running the Sample Application

1. Clone this repository and navigate into the directory:

   ```
   get clone https://github.com/CiscoDevNet/webex-vault-samples.git
   cd webex-vault-samples
   ```

1. (Optional) Create and activate a Python virtual environment:

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

1. Install needed Python dependencies:

   ```
   pip install -r requirements.txt
   ```

1. Rename `.env.example` to `.env` and configure the needed information:

   * **VAULT_TOKEN** - The Vault token created for this application's use (or the root token in a dev environment).

   * **VAULT_ADDR** - The URL of the Vault server API

   > **Hint:** If running Vault in a container, you can get the container's IP via: `ocker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <name_of_container>`

   (The other config keys can be left as is for this sample)

1. If this project was opened in Visual Studio Code, the application can be launched via the **Run and Debug** tab, or simply:

   **people_me.py**
   ```
   python people_me.py
   ```

   **people_me_flask.py**
   ```
   FLASK_APP=people_me_flask flask run
   ```

1. For `people_me_flask.py`, open a browser and navigate to: `http://127.0.0.1:5000`

   If the credential has not been created/authorized in Vault, an 'Unauthorized!' message will display.  Click the **Authorize** button to start the OAuth2 login sequence.

   Once the credential has been created, the application will display 'Authorized!' along with the API-retrieved Webex display name of the authorized user.

## Hints

* When testing `people_me_flask.py`, you may want to delete the credential from Vault to force the sample to re-authorize and create it:

  ```
  vault delete oauthapp/creds/testauth
  ```

* Also when testing `people_me_flask.py`, you may need to use a new incognito/private browser instance to make sure no pre-existing Webex SSO cookies are presented.