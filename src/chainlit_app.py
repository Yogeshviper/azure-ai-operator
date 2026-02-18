import os

import json

import chainlit as cl

from openai import AzureOpenAI

from azure.identity import DefaultAzureCredential

from azure.mgmt.resource import ResourceManagementClient

from azure.mgmt.storage import StorageManagementClient

from azure.mgmt.network import NetworkManagementClient

from azure.mgmt.compute import ComputeManagementClient


# ===============================

# Azure Setup

# ===============================


subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

credential = DefaultAzureCredential()


resource_client = ResourceManagementClient(credential, subscription_id)

storage_client = StorageManagementClient(credential, subscription_id)

network_client = NetworkManagementClient(credential, subscription_id)

compute_client = ComputeManagementClient(credential, subscription_id)


# ===============================

# OpenAI Setup

# ===============================


client = AzureOpenAI(

    api_key=os.environ["AZURE_OPENAI_API_KEY"].strip(),

    api_version=os.environ["AZURE_OPENAI_API_VERSION"].strip(),

    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"].strip()

)


deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"].strip()


# ===============================


def get_basic_vm_size(location):

    sizes = compute_client.virtual_machine_sizes.list(location)

    for size in sizes:

        if size.name.startswith("Standard_B"):

            return size.name

    return "Standard_B2s"


# ===============================

# Azure Resource Functions

# ===============================


def create_rg(name, location):

    resource_client.resource_groups.create_or_update(

        name,

        {"location": location}

    )


def create_storage(rg, location, name):

    storage_client.storage_accounts.begin_create(

        rg,

        name,

        {

            "location": location,

            "sku": {"name": "Standard_LRS"},

            "kind": "StorageV2"

        }

    ).result()


def create_vm(rg, location, vm_name, os_type):


    size = get_basic_vm_size(location)


    if os_type.lower() == "windows":

        image = {

            "publisher": "MicrosoftWindowsServer",

            "offer": "WindowsServer",

            "sku": "2019-Datacenter",

            "version": "latest"

        }

    else:

        image = {

            "publisher": "Canonical",

            "offer": "0001-com-ubuntu-server-jammy",

            "sku": "22_04-lts",

            "version": "latest"

        }


    # Create VNet + Subnet

    vnet = network_client.virtual_networks.begin_create_or_update(

        rg,

        vm_name + "-vnet",

        {

            "location": location,

            "address_space": {"address_prefixes": ["10.0.0.0/16"]},

            "subnets": [{

                "name": "default",

                "address_prefix": "10.0.0.0/24"

            }]

        }

    ).result()


    subnet_id = vnet.subnets[0].id


    # Public IP

    pip = network_client.public_ip_addresses.begin_create_or_update(

        rg,

        vm_name + "-pip",

        {

            "location": location,

            "sku": {"name": "Standard"},

            "public_ip_allocation_method": "Static"

        }

    ).result()


    # NIC

    nic = network_client.network_interfaces.begin_create_or_update(

        rg,

        vm_name + "-nic",

        {

            "location": location,

            "ip_configurations": [{

                "name": "ipconfig1",

                "subnet": {"id": subnet_id},

                "public_ip_address": {"id": pip.id}

            }]

        }

    ).result()


    compute_client.virtual_machines.begin_create_or_update(

        rg,

        vm_name,

        {

            "location": location,

            "hardware_profile": {"vm_size": size},

            "storage_profile": {"image_reference": image},

            "os_profile": {

                "computer_name": vm_name,

                "admin_username": "azureuser",

                "admin_password": "Azure@12345678"

            },

            "network_profile": {

                "network_interfaces": [{"id": nic.id}]

            }

        }

    ).result()


# ===============================

# AI Intent Parser

# ===============================


async def parse_prompt(prompt):


    system_prompt = """

You are an Azure Cloud automation parser.


Convert user request into JSON format:


{

  "action": "create_rg | create_storage | create_vm",

  "name": "",

  "resource_group": "",

  "location": "",

  "os_type": ""

}


Only return valid JSON.

"""


    response = client.chat.completions.create(

        model=deployment_name,

        messages=[

            {"role": "system", "content": system_prompt},

            {"role": "user", "content": prompt}

        ],

        temperature=0

    )


    return json.loads(response.choices[0].message.content)


# ===============================

# Chainlit

# ===============================


@cl.on_chat_start

async def start():

    await cl.Message(

        "Azure AI Operator ready. Describe what you want to create."

    ).send()


@cl.on_message

async def handle_message(message: cl.Message):


    intent = await parse_prompt(message.content)


    action = intent.get("action")

    name = intent.get("name")

    rg = intent.get("resource_group")

    location = intent.get("location")

    os_type = intent.get("os_type", "ubuntu")


    if action == "create_rg":

        create_rg(name, location)

        await cl.Message(f"Resource Group {name} created").send()


    elif action == "create_storage":

        create_storage(rg, location, name)

        await cl.Message(f"Storage account {name} created").send()


    elif action == "create_vm":

        create_vm(rg, location, name, os_type)

        await cl.Message(f"VM {name} deployed successfully").send()


    else:

        await cl.Message("I could not understand the request.").send()

