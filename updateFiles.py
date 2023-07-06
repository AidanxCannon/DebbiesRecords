import subprocess

# Replace with the path to your local repository (if applicable)
local_repository = "https://github.com/AidanxCannon/DebbiesRecords"

# Replace with the URL of your Azure App Service (if needed)
azure_app_service_url = "https://debbiesrecords.azurewebsites.net/"

# Push changes to the GitHub repository
subprocess.call(["git", "push", "origin", "master"])

# Print a message to indicate successful deployment
print("Deployment to Azure App Service completed.")
