echo
echo "This script needs git, Docker and Docker compose."
echo

# Create initial files
mkdir /opt/watershed-combined
cd /opt/watershed-combined

# Create folder
mkdir panel
mkdir api
mkdir -p db/data

# Get source code
git clone https://github.com/elsing/fyp-panel.git panel
git clone https://github.com/elsing/fyp-api.git api

# Move need files
mv api/docker/traefik ./
mv api/docker/docker-compose.yml ./
mv api/docker/db/* ./db

#Notify
echo "Please change the CHANGEME settings found in:"
echo
echo "/opt/watershed-combined/api/app.py" - Domain Name
echo "/opt/watershed-combined/panel/.env" - API URL
echo "/opt/watershed-combined/docker-compose.yml" - password
echo "/opt/watershed-combined/traefik/config.yml - Traefik Host SNIs & CORS settings"
echo
echo "Finally, run:"
echo "docker compose up -d"
echo
echo "User: admin Password: admin"