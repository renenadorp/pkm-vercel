# Introduction
In 2024 a Data Platform Upgrade subproject was executed. The main idea of this work was to replace the following components:
- Pentaho, a Java based ETL tool used for orchestration
- SCD, a Java based Inergy component used for data historization


The goal of this story is to send log messages from within Snowflake directly to Log Analytics Workspace in a custom log table. This page describes the progress of this investigation. 

# Azure Setup

## Relevant documentation pages
- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview?source=recommendations
- https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal?source=recommendations

## Microsoft Entra ID
The Logs Ingestion API needs to be authenticated. This is done by creating an App Registration in Microsoft Entra ID, and then generating the following:
- CLIENT_ID
- CLIENT_SECRET

## Create Custom Log Table + DCR
- Go to the Log Analytics Workspace and create a new custom log table (DCR based). 

- Within this process create a new data collection rule (DCR). This tells Azure to which logging table the messages need to be sent. The Log Ingestion API call always contains the DCR.

- The next step in this process is to define the structure of the logging table. This can be done by using a sample json file with log messages. 


- Get DCR Id
The Log Ingestion API needs the DCR Id. This ID can be retrieved by selecting the JSON view of the DCR that was created.

- Authorise DCR
Go to IAM blade of the DCR, and add role assignment. Select Role `Monitoring Metrics Publisher` and then "Add Members", then add the DCR as a member.

# Snowflake Setup 
## Create Snowflake Stage
In Snowsight create an internal stage with the following commands
```
USE SCHEMA <D>.<S>; -- database and schema of your choice
CREATE STAGE PYTHON_PACKAGES;
```

## Create Network Rules
```
CREATE OR REPLACE NETWORK RULE law_api_network_rule  
TYPE = HOST_PORT  
VALUE_LIST = ('<dce>.<region>.ingest.monitor.azure.com:443', 'login.microsoftonline.com:443')   
MODE= EGRESS; 
```
## Create Secrets
CREATE OR REPLACE SECRET law_client_secret    
TYPE = password    
USERNAME = '...'  --CLIENT_ID    
PASSWORD = '...'; --CLIENT_SECRET

## Create External Access Integration
An ACCOUNTADMIN needs to create an external access integration to Azure with the following command: 
```
USE ROLE ACCOUNTADMIN;
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION law_ext_int  
ALLOWED_NETWORK_RULES = (MA.LAW_API_NETWORK_RULE)  
ALLOWED_AUTHENTICATION_SECRETS = (MA.law_client_secret)  
ENABLED = true;

```
Refer to https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration for details.
# Local Setup

## Reguired Information
We create a Snowflake UDF that will send log messages to Azure. This is done by calling the Log Ingestion API. For this to work the following information is needed
- Log Ingestion Data Collection Endpoint Uri (DCE): `https://<dce-name>.<region>.ingest.monitor.azure.com` 
- Log Ingestion Data Collection Rule Id (DCR): `dcr-<immutable id>`
- Log Ingestion Customer Log Table Stream Name (Log Table Stream):`Custom-<custom log table name>`

## Local Development: only for testing locally
To test using the Log Ingestion Api we need to setup a local Python development environment. 

1. Install python 3.9
The code that we develop is based on Python 3.9. The first step is to install this version on the local machine. Please consult the internet on how to do this, because it is OS dependent. 

2. Create virtual environment
We use the python module venv for virtual environments, but conda is also possible. 
- Start a terminal on your local machine
- Navigate to your project folder
- Create a virtual environment: `python3 -m venv .env`

3. Start the virtual environment: `source .env/bin/activate`

4. Install packages
```
pip install azure-identity azure-monitor-ingestion 
```
5. Create Python script
Create a python file `log_to_azure.py` with the following code:
```
endpoint_uri = "https://<dce>.<region>.ingest.monitor.azure.com" # logs ingestion endpoint of the DCR

dcr_immutableid = "dcr-<id>" # immutableId property of the Data Collection Rule

stream_name = "Custom-<log_table_name>_CL" #name of the stream in the DCR that represents the destination table

# Import required modules

import os

from azure.identity import DefaultAzureCredential , ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError

# Using DefaultAzureCredential # ONLY FOR DEVELOPMENT!!!!!!

credential = DefaultAzureCredential()

clientDefault = LogsIngestionClient(endpoint=endpoint_uri, credential=credential, logging_enable=True)

# Using ClientSecretCredential
credentialClientSecret = ClientSecretCredential(
tenant_id="<tenant_id",
client_id="<client-id",
client_secret='client-secret',
)

clientClientSecret = LogsIngestionClient(endpoint=endpoint_uri, credential=credentialClientSecret, logging_enable=True)

# Sample log data
data = [{
"customer": "Klantnaam",
"component": "/ETL/job_naam/sub_job2/validate",
"eventclass": "/Task/Data",
"summary": "Invalid message content",
"severity": "4",
"runid": "00420",
"description": "Content of message test.xml invalid. XML parser failed."
}]

try:
clientClientSecret.upload(rule_id=dcr_immutableid, stream_name=stream_name, logs=data)
except HttpResponseError as e:
print(f"Upload failed: {e}")
```

## Prepare External Packages
We require Python packages that are not in the Snowflake channel of the Anaconda package list. This list can be found here (#TODO). This list can also be obtained in SnowSight using the following sql statement:

`
SELECT * FROM INFORMATION_SCHEMA.PACKAGES where language = 'Python'
`
The main Python packages not available in Snowflake are `azure-identity` (needed for authentication), and `azure-monitor-ingestion` (needed for log ingestion).

1. Install Snowflake CLI
Preparing the required packages not available in Snowflake is done locally with the Snowflake CLI, which we need to install first. Please refer to https://docs.snowflake.com/en/developer-guide/snowflake-cli/installation/installation on how to do this. 

2. Create Package
To create a package enter the following command in a Terminal window:
`snow snowpark package create azure-monitor-ingestion`
`snow snowpark package create azure-identity==1.17.0`

This will create the following zipfiles in the current directory:
`azure_monitor_ingestion.zip`
`azure_identity.zip`

Note that version 1.17.0 is selected for azure-identity. The most recent version 1.19.0 resulted in an error similar to `Cannot import name 'AccessTokenInfo' from 'azure.core.credentials' ` caused by a dependency on azure.core.credentials that does not exist for version 1.17.0.

3. Upload Package to Snowflake Stage
The local zip files need to be uploaded to a Snowflake stage:
`snow snowpark package upload -f azure_monitor_ingestion.zip -s PYTHON PACKAGES`

The Snowflake CLI will (re)use Snowflake connections defined in `.snowflake/connections.toml` or `.snowsql/config`. Make sure that these connections are setup correctly.


# Snowflake 
## Create UDF
In Snowsight run the following code to create the UDF.
```
use schema <D>.<S>;

create or replace function log_to_azure()
returns string
language python
--volatile
runtime_version = '3.9'
packages = ('azure-core', 'azure-keyvault-secrets', 'snowflake', 'cryptography', #Required package
'msal', 'portalocker', 'typing-extensions')
imports=( '@MSSTG_PYTHON/azure_identity.zip', '@MSSTG_PYTHON/azure_monitor_ingestion.zip')
handler = 'log_to_azure'
EXTERNAL_ACCESS_INTEGRATIONS = (law_ext_int)

SECRETS = ('LAW_CLIENT_SECRET' = LAW_CLIENT_SECRET )
as
$$

# information needed to send data to the DCR endpoint
endpoint_uri = "https://<dce>.westeurope-1.ingest.monitor.azure.com" # logs ingestion endpoint of the DCR
dcr_immutableid = "dcr-<dcr-id>" # immutableId property of the Data Collection Rule
stream_name = "Custom-<LogTable>" #name of the stream in the DCR that represents the destination table

# Import required modules
import os
import _snowflake
from azure.identity             import DefaultAzureCredential
from azure.monitor.ingestion    import LogsIngestionClient
from azure.core.exceptions      import HttpResponseError

def get_azure_credentials():
    credentials_object = _snowflake.get_username_password('LAW_CLIENT_SECRET');
    credentials_dictionary = {}
    credentials_dictionary["TENANT_ID"]     = '<tenant_id>'
    credentials_dictionary["CLIENT_ID"]     = credentials_object.username
    credentials_dictionary["CLIENT_SECRET"] = credentials_object.password
    return credentials_dictionary
    
azure_credentials = get_azure_credentials() 

from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
       tenant_id="<TENANT_ID>",
       client_id="<CLIENT_ID>",
       client_secret='<CLIENT_SECRET>',
   )
   
client = LogsIngestionClient(endpoint=endpoint_uri, credential=credential, logging_enable=True)


data = [{
    "customer": "Klantnaam",
    "component": "/ETL/job_naam/sub_job2/validate",
    "eventclass": "/Task/Data",
    "summary": "Invalid message content",
    "severity": "4",
    "runid": "00420",
    "description": "Content of message test.xml invalid. XML parser failed."
}]

def log_to_azure():
    try:
        client.upload(rule_id=dcr_immutableid, stream_name=stream_name, logs=data)
    except HttpResponseError as e:
        print(f"Upload failed: {e}")
    return ['Log entry added to Azure Monitor Custom Log Table', azure_credentials]
$$;

```

## Test UDF
In Snowsight call the UDF:
`SELECT LOG_TO_AZURE();`

If all went well, this should result in a new log message in the Log Analytics Workspace custom log table!!!




