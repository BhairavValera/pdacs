import globus_sdk
import sys
import json

# Loading tokens
tokens = None
with open("/export/galaxy-central/database/jobs_directory/.dev-tokens.json", 'r') as tokens_file:
    tokens = json.load(tokens_file)
TRANSFER_TOKENS = tokens[0]
AUTH_TOKENS = tokens[1]
TRANSFER_TOKEN = TRANSFER_TOKENS["access_token"]

# a GlobusAuthorizer is an auxiliary object we use to wrap the token. In
# more advanced scenarios, other types of GlobusAuthorizers give us
# expressive power
authorizer = globus_sdk.AccessTokenAuthorizer(TRANSFER_TOKEN)
tc = globus_sdk.TransferClient(authorizer=authorizer)

# high level interface; provides iterators for list responses
source_endpoint_id = 'ffb116e6-d39e-11e7-9679-22000a8cbd7d'
source_endpoint_path = '/MiraTitanU/Grid/M000/L2100/HACC000/run/run000/'

destination_endpoint_id = 'f4820a2c-ad64-11e9-821e-02b7a92d8e58'
destination_endpoint_path = 'cosmo/scratch/galaxy_ftp/'

label = "Petrel to cosmo endpoint"

tdata = globus_sdk.TransferData(tc, source_endpoint_id,
                                destination_endpoint_id,
                                label=label,
                                sync_level="checksum")
tdata.add_item(source_endpoint_path,
               destination_endpoint_path,
               recursive=True)

tc.endpoint_autoactivate(source_endpoint_id)
tc.endpoint_autoactivate(destination_endpoint_id)

transfer_result = tc.submit_transfer(tdata)

rule_data = {
    "DATA_TYPE": "access",
    "principal_type": "identity",
    "principal": destination_endpoint_id,
    "path": destination_endpoint_path,
    "permissions": "rw",
}

result = tc.add_endpoint_acl_rule(endpoint_id, rule_data)
rule_id = result["access_id"]

print("Go to the galaxy web interface and choose 'Get Data' -> 'Upload File' -> 'Choose FTP File' to visualize your data")
