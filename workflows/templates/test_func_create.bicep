param  name  string = 'jahnavistoragesceoo'
param  location  string = 'EastUS'
resource  storageAccount 'Microsoft.Storage/storageAccounts@2021-09-01' = {
name: name
location: location
sku: {
    name: 'Standard_LRS'
}
kind: 'StorageV2'
}
resource  applicationInsights  'Microsoft.Insights/components@2020-02-02' = {
name: 'nameapplication-insights'
location: location
kind: 'web'
properties: {
   Application_Type: 'web'
   Request_Source: 'rest'
   }
}
resource  hostingPlan  'Microsoft.Web/serverfarms@2021-03-01' = {
name: name
location: location
kind: 'Linux'
sku: {
   name: 'Y1'
   tier: 'Dynamic'
}
properties: {
   reserved: true
  } 
}
resource  functionApp  'Microsoft.Web/sites@2021-03-01' = {
name: name
location: location
kind: 'functionapp'
identity: {
   type: 'SystemAssigned'
}
properties: {
serverFarmId: hostingPlan.id
siteConfig: {
  pythonVersion: '3.11'
  linuxFxVersion: 'python|3.11'
  appSettings: [
    {
      name: 'AzureWebJobsStorage'
      value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
    }
    {
      name: 'SCM_DO_BUILD_DURING_DEPLOYMENT' 
      value: 'true'
    }
    {
      name: 'ENABLE_ORYX_BUILD'  
      value: 'true'
    }
    {
      name: 'FUNCTIONS_EXTENSION_VERSION'
      value: '~4'
    }
    {
      name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
      value: applicationInsights.properties.InstrumentationKey
    }
    {
      name: 'FUNCTIONS_WORKER_RUNTIME'
      value: 'python'
    }
  ]
}
    httpsOnly: true
   }
}