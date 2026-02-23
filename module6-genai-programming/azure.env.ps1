# ================================
# Azure AI Foundry – Mini Model Setup
# Tested for Windows PowerShell / pwsh
# ================================

# --------- VARIABLES (EDIT THESE) ----------
$SubscriptionId = "<YOUR_SUBSCRIPTION_ID>"
$Location       = "uaenorth"  # Choose a supported region (e.g., "eastus", "westeurope", "uaenorth")
$ResourceGroup  = "rg-ai-foundry-mini"
$FoundryName    = "aifoundrymini$((Get-Random -Maximum 9999))"
$DeploymentName = "phi3-mini"

# Phi-3 Mini model identifiers (Microsoft catalog)
$ModelName      = "Phi-3-mini-4k-instruct"
$ModelVersion   = "1"
$SkuName        = "GlobalStandard"
$SkuCapacity    = 1
# ------------------------------------------

Write-Host "🔐 Logging into Azure..."
az login | Out-Null
az account set --subscription $SubscriptionId

Write-Host "📦 Installing Azure CLI extension (cognitiveservices)..."
az extension add -n cognitiveservices --upgrade | Out-Null

Write-Host "📁 Creating resource group..."
az group create `
  --name $ResourceGroup `
  --location $Location | Out-Null

Write-Host "🧠 Creating Azure AI Foundry resource..."
az cognitiveservices account create `
  --name $FoundryName `
  --resource-group $ResourceGroup `
  --location $Location `
  --kind AIServices `
  --sku S0 `
  --yes | Out-Null

Write-Host "🚀 Deploying Phi-3 Mini model..."
az cognitiveservices account deployment create `
  --name $FoundryName `
  --resource-group $ResourceGroup `
  --deployment-name $DeploymentName `
  --model-name $ModelName `
  --model-version $ModelVersion `
  --model-format Microsoft `
  --sku-name $SkuName `
  --sku-capacity $SkuCapacity | Out-Null

Write-Host "✅ Deployment complete"

Write-Host "`n🔑 Retrieving API Key..."
$ApiKey = az cognitiveservices account keys list `
  --name $FoundryName `
  --resource-group $ResourceGroup `
  --query "key1" -o tsv

Write-Host "🌐 Retrieving Inference Endpoint..."
$Endpoint = az cognitiveservices account show `
  --name $FoundryName `
  --resource-group $ResourceGroup `
  --query "properties.endpoints.'Azure AI Model Inference API'" -o tsv

Write-Host "`n==================== RESULT ===================="
Write-Host "Foundry Resource : $FoundryName"
Write-Host "Deployment Name  : $DeploymentName"
Write-Host "Endpoint         : $Endpoint"
Write-Host "API Key          : $ApiKey"
Write-Host "================================================"

Write-Host "`n✅ Ready to call the model using OpenAI‑compatible APIs"