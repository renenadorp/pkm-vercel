# NextJS on Azure

## Intro
This page contains a description of an Azure Static Web App using NextJS, based on the instructions on this [page](https://learn.microsoft.com/en-us/azure/static-web-apps/deploy-nextjs-hybrid).

The repo for this setup can be found [here](https://github.com/renenadorp/nextjs-pkm). Feel free to reuse, copy, fork, etc.


## Azure Setup
Nothing special here. Simply create a static web app in Azure as described. 
Choose Github as the source code version control system. The setup process will also create a Github Actions workflow file for you. Clone the Github repo to your local machine.


## Github Actions Workflow
The Github Actions workflow that was created during the Azure Setup will look something like this:
```
name: Deploy web app to Azure Static Web Apps

on:
  push:
    branches: 
        - main
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches:
        - main

# Environment variables available to all jobs and steps in this workflow
env:
    IS_STATIC_EXPORT: false
    APP_LOCATION: "/" # location of your client code
    #API_LOCATION: "api" # location of your api source code - optional
    #APP_ARTIFACT_LOCATION: "build" # location of client code build output
    APP_ARTIFACT_LOCATION: "standalone/" # location of client code build output
    AZURE_STATIC_WEB_APPS_API_TOKEN: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN_PROUD_SEA_04A78D703 }}

permissions:
  contents: read

jobs:
  build_and_deploy_job:
    permissions:
      contents: read # for actions/checkout to fetch code
      pull-requests: write # for Azure/static-web-apps-deploy to comment on PRs
    if: github.event_name == 'push' || (github.event_name == 'pull_request' && github.event.action != 'closed')
    runs-on: ubuntu-latest
    name: Build and Deploy Job
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true
      - name: Build And Deploy
        id: builddeploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ env.AZURE_STATIC_WEB_APPS_API_TOKEN }} # secret containing api token for app
          repo_token: ${{ secrets.GITHUB_TOKEN }} # Used for Github integrations (i.e. PR comments)
          action: "upload"
          ###### Repository/Build Configurations - These values can be configured to match you app requirements. ######
          # For more information regarding Static Web App workflow configurations, please visit: https://aka.ms/swaworkflowconfig
          #output_location: ".next/standalone" # Built app content directory, relative to app_location - optional

          app_build_command: "npm run build  && cp -r public standalone/public && rm -rf standalone/cache" #RNA
        
          app_location: ${{ env.APP_LOCATION }}
          api_location: ${{ env.API_LOCATION }}
          app_artifact_location: ${{ env.APP_ARTIFACT_LOCATION }}
          ###### End of Repository/Build Configurations ######

  close_pull_request_job:
    permissions:
      contents: none
    if: github.event_name == 'pull_request' && github.event.action == 'closed'
    runs-on: ubuntu-latest
    name: Close Pull Request Job
    steps:
      - name: Close Pull Request
        id: closepullrequest
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ env.AZURE_STATIC_WEB_APPS_API_TOKEN }} # secret containing api token for app
          action: "close"
```
### Build Command
the app build command (included in the workflow) is as follows:
```npm run build  && cp -r public standalone/public && rm -rf standalone/cache``` 

This command will do the following:
1. Build the app
2. Copy the public folder to the standalone directory. This is needed, because otherwise any static assets in the public folder will not be included
3. Remove the standalone/cache directory. This is needed because otherwise the standalone directory is too large to be deployed on Azure SWA.

## NextJS Configuration
The file ```next.config.js``` contains the NextJS configuration. For this app it contains the following code:
```
const withImages = require('next-images')
const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
})
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    disableStaticImages: true,
    unoptimized: true
    },
  trailingSlash: true //https://github.com/Azure/static-web-apps/issues/1167
  ,   distDir: 'standalone',

};

// module.exports = withNextra()
// module.exports = withImages(withNextra({...nextConfig}))
// ;

// const { withExpo } = require("@expo/next-adapter");
const withPlugins = require("next-compose-plugins");
// const withFonts = require("next-fonts");
// const withTM = require("next-transpile-modules")(["react-native-web"]);



module.exports = withPlugins(
[withImages, withNextra],
nextConfig
);
```

One of the main challenges for this implementation was to ensure images were displayed correctly. By default images are note included in the build process, because they are expected to be served by CDN. In this case a CDN was not needed. 

In order to include images in the build the NextJS configuration file contains the block about images: 
```
images: {
    disableStaticImages: true,
    unoptimized: true
    },
```

Another important section is the output:
```
output: standalone
```
This will result in an output folder called ```standalone``` that can be distributed on its own.



