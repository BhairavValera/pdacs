import globus_sdk
import json

CLIENT_ID = 'cc141ad0-7b43-40e4-9d12-6652bb13646b'

client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
client.oauth2_start_flow()

authorize_url = client.oauth2_get_authorize_url()
print('Please go to this URL and login: {0}'.format(authorize_url))

# this is to work on Python2 and Python3 -- you can just use raw_input() or
# input() for your specific version
get_input = getattr(__builtins__, 'raw_input', input)
auth_code = get_input(
    'Please enter the code you get after login here: ').strip()
token_response = client.oauth2_exchange_code_for_tokens(auth_code)
globus_auth_data = token_response.by_resource_server['auth.globus.org']
globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']

with open("/export/galaxy-central/database/jobs_directory/.dev-tokens.json", "w") as write_file:
    json.dump([globus_transfer_data, globus_auth_data], write_file, indent=2)
