echo "This script needs git, Docker and Docker compose."

# Create initial files
mkdir /opt/fyp-combined
cd /opt/fyp-combined

# Create folder
mkdir panel
mkdir api
mkdir db

# Get source code
git clone https://github.com/elsing/fyp-panel.git panel
git clone https://github.com/elsing/fyp-api.git api

# Move need files
mv api/docker/traefik ./
mv api/docker/docker-compose.yml ./

#Notify
echo "Please change the CHANGEME settings found in:"
echo "/opt/fyp-combined/api/app.py"
echo "/opt/fyp-combined/docker-compose.yml"
echo
echo "Finally, run:"
echo "docker compose up -d"