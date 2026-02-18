🚀 Azure AI Cloud Operator

An AI-assisted Azure Infrastructure Automation project that deploys Azure resources from structured prompts using Azure SDK and Azure OpenAI.

This project allows users to provision Azure resources like Virtual Machines, Resource Groups, and Storage Accounts through a conversational interface powered by Chainlit.

📌 Project Overview

This project combines:

🧠 Azure OpenAI (for prompt parsing)

🐍 Azure SDK for Python (for infrastructure provisioning)

💬 Chainlit (chat interface)

🐳 Docker (containerization)

☸ AKS (deployment platform)

Users provide structured prompts such as:

Create VM  
Name: bot-win-server  
Resource Group: demo-rg  
Location: centralindia  
OS: Windows


The system parses the input and deploys the requested resource in Azure automatically.

🏗 Supported Resources

Currently supported:

✅ Resource Group

✅ Storage Account

✅ Virtual Machine

Windows

Ubuntu

✅ Automatic creation (during VM creation):

Virtual Network

Subnet

Public IP

Network Interface

🧠 Architecture Flow

User Prompt
→ Chainlit UI
→ Azure OpenAI (parses intent)
→ Python Action Mapping
→ Azure SDK
→ Azure Resource Deployment

📂 Project Structure
azure-ai-operator/
│
├── src/
│   └── chainlit_app.py
│
├── requirements.txt
├── Dockerfile
├── .env
└── k8s/
    ├── deployment.yaml
    ├── service.yaml

⚙️ Prerequisites

Before starting, ensure:

Azure Subscription

Azure OpenAI deployed

AKS Cluster created

Azure Container Registry (ACR)

Service Principal or Managed Identity configured

🔐 Environment Variables (.env)

Create a .env file:

AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_openai_key
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

🛠 Implementation Steps
1️⃣ Clone Repository
git clone <your-repo-url>
cd azure-ai-operator

2️⃣ Install Dependencies (Local Testing)
pip install -r requirements.txt
chainlit run src/chainlit_app.py

3️⃣ Build Docker Image
az acr build \
  --registry <your-acr-name> \
  --image azure-operator:v1 \
  .

4️⃣ Create Kubernetes Secret
kubectl create secret generic azure-env \
  --from-env-file=.env

5️⃣ Deploy to AKS
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

6️⃣ Access Application
kubectl get svc


Use LoadBalancer IP to access Chainlit UI.

💬 Supported Commands (Structured Format)
Create Resource Group
Create Resource Group
Name: demo-rg
Location: centralindia
