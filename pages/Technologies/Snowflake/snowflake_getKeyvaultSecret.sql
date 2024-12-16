
--##################################################################
--      GET KEYVAULT SECRET
--##################################################################


USE SCHEMA DWH_DEV_POC.MA;

CREATE OR REPLACE SECRET KV_CLIENT_SECRET_DEV    
TYPE = password    
USERNAME = '***'; -- Client ID of App registration in Entra ID    
PASSWORD = '***'; -- Client Secret of App registration in Entra ID

CREATE OR REPLACE NETWORK RULE DWH_DEV_POC.MA.KV_NETWORK_RULE_DEV  
MODE = EGRESS  
TYPE = HOST_PORT  
VALUE_LIST = ('coapt-dev.vault.azure.net');  -- Key vault url
  
CREATE OR REPLACE NETWORK RULE DWH_DEV_POC.MA.KV_AUTH_NETWORK_RULE_DEV 
MODE = EGRESS  
TYPE = HOST_PORT  
VALUE_LIST = ('login.microsoftonline.com');


show secrets like 'KV%' in DWH_DEV_POC.MA;

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION KV_ACCESS_INTEGRATION_DEV
ALLOWED_NETWORK_RULES = (KV_NETWORK_RULE,KV_AUTH_NETWORK_RULE_DEV)  
ALLOWED_AUTHENTICATION_SECRETS = (KV_CLIENT_SECRET_DEV)  
ENABLED = true;



CREATE OR REPLACE FUNCTION DWH_DEV_POC.MA.GET_KV_SECRET()  
RETURNS VARCHAR  
LANGUAGE PYTHON  
runtime_version = '3.9'
packages = ('azure-core==1.27.1', 'azure-keyvault-secrets==4.7.0', 'snowflake', 'cryptography', 'msal', 'portalocker', 'typing-extensions', 'requests')
imports=( '@MSSTG_PYTHON/azure_identity.zip')
handler = 'get_kv_secret'
EXTERNAL_ACCESS_INTEGRATIONS = (KV_ACCESS_INTEGRATION_DEV)
SECRETS = ('cred' = DWH_DEV_POC.MA.KV_CLIENT_SECRET_DEV )  
AS  
$$  
import _snowflake  
    
from azure.identity         import ClientSecretCredential  
from azure.keyvault.secrets import SecretClient  
  
def get_kv_secret():  
    ######secret_val = _snowflake.get_generic_secret_string('cred')  
    secret_val = _snowflake.get_username_password('cred');
    client_secret=secret_val.password
  
    credential = ClientSecretCredential(  
        tenant_id  = '2a916b80-031c-46f9-8f14-884c576496ca', #replace with actual value  
        client_id  = '5109e839-8fa5-451c-95c1-96aa7a323ae1', #replace with actual value 
        client_secret='~52qYB8tD.~961Z~jsGtDvWUMt.6s8Kp5I'   #client_secret
     )
    try:
      client = SecretClient(vault_url="https://coapt-dev.vault.azure.net/",  credential=credential) 
      secret = client.get_secret("ace-ba-load")  
    except Exception as e:
      return (['Error:', e, credential])
    
    return secret.value
    
def get_azure_credentials_object():
    credentials_object = _snowflake.get_username_password('cred');
    credentials_dictionary = {}
    credentials_dictionary["TENANT_ID"]     = '***' -- tenant id
    credentials_dictionary["CLIENT_ID"]     =  credentials_object.username
    credentials_dictionary["CLIENT_SECRET"] =  credentials_object.password
    return [credentials_dictionary, credentials_object]
#credential=get_azure_credentials_object

 
  

$$;
select dwh_dev_poc.ma.get_kv_secret();
