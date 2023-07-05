import subprocess

# Set the path to your local Git repository
local_git_repository = "https://github.com/AidanxCannon/DebbiesRecords"

# Set the URL of your Azure App Service Git repository
azure_git_repository = "https://github.com/AidanxCannon/DebbiesRecords"

# Change directory to your local Git repository
subprocess.call(["cd", local_git_repository], shell=True)

# Initialize the Git repository
subprocess.call(["git", "init"], shell=True)

# Add all files to the repository
subprocess.call(["git", "add", "."], shell=True)

# Commit the changes
subprocess.call(["git", "commit", "-m", "Initial commit"], shell=True)

# Set the remote repository URL
subprocess.call(["git", "remote", "add", "azure", azure_git_repository], shell=True)

# Push the code to Azure App Service
subprocess.call(["git", "push", "azure", "master"], shell=True)
