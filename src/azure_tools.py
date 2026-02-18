import os

from azure.identity import ClientSecretCredential

from azure.mgmt.resource import ResourceManagementClient

from azure.mgmt.storage import StorageManagementClient


credential = ClientSecretCredential(

    tenant_id=os.getenv("AZURE_TENANT_ID"),

    client_id=os.getenv("AZURE_CLIENT_ID"),

    client_secret=os.getenv("AZURE_CLIENT_SECRET"),

)


subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")


resource_client = ResourceManagementClient(credential, subscription_id)

storage_client = StorageManagementClient(credential, subscription_id)



def create_resource_group(name, location):

    resource_client.resource_groups.create_or_update(

        name,

        {"location": location}

    )

    return f"Resource Group '{name}' created in {location}"



def create_storage_account(name, rg, location):

    poller = storage_client.storage_accounts.begin_create(

        rg,

        name,

        {

            "location": location,

            "sku": {"name": "Standard_LRS"},

            "kind": "StorageV2",

        },

    )

    poller.result()

    return f"Storage Account '{name}' created successfully"

