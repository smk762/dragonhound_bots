#!/bin/bash

mkdir -p ~/logs
mkdir atomicdex
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx curl libcurl4-openssl-dev libssl-dev jq
pip3 install -r requirements.txt

echo "Configuring environment..."
./configure.py env_vars

echo "Setting up AtomicDEX-API..."
./configure.py atomicdex
./stop_atomicdex.sh
./update_atomicdex.sh
SCRIPT_PATH=$(pwd)


echo "Setting up FastAPI..."
./configure.py nginx
subdomain=$(python3 ./const.py get_subdomain)
sudo certbot certonly -d ${subdomain}
./configure.py ssl_env
sudo cp nginx/fastapi-faucet.serverblock /etc/nginx/sites-available/${subdomain}
sudo ln -s /etc/nginx/sites-available/${subdomain} /etc/nginx/sites-enabled/${subdomain}
sudo systemctl restart nginx

echo "Creating service files..."
cp service/TEMPLATE-atomicdex.service service/atomicdex-api.service
cp service/TEMPLATE-discord-bot.service service/discord-bot-faucet.service
cp service/TEMPLATE-fastapi.service service/fastapi-faucet.service

sed "s|SCRIPT_PATH|${SCRIPT_PATH}|g" -i "service/atomicdex-api.service"
sed "s|SCRIPT_PATH|${SCRIPT_PATH}|g" -i "service/discord-bot-faucet.service"
sed "s|SCRIPT_PATH|${SCRIPT_PATH}|g" -i "service/fastapi-faucet.service"

sed "s/USERNAME/${USER}/g" -i "service/atomicdex-api.service"
sed "s/USERNAME/${USER}/g" -i "service/discord-bot-faucet.service"
sed "s/USERNAME/${USER}/g" -i "service/fastapi-faucet.service"

echo "Copying service files to /etc/systemd/system/..."
sudo cp service/atomicdex-api.service /etc/systemd/system/atomicdex-api.service
sudo cp service/discord-bot-faucet.service /etc/systemd/system/discord-bot-faucet.service
sudo cp service/fastapi-faucet.service /etc/systemd/system/fastapi-faucet.service

cd /etc/systemd/system/
sudo systemctl enable atomicdex-api.service
sudo systemctl enable discord-bot-faucet.service
sudo systemctl enable fastapi-faucet.service
echo
echo "Deamon service created for atomicdex-api. To run it, use 'sudo systemctl start atomicdex-api.service'"
echo "Logs will go to ~/logs/atomicdex-api.log"
echo
echo "Deamon service created for discord-bot-faucet. To run it, use 'sudo systemctl start discord-bot-faucet.service'"
echo "Logs will go to ~/logs/discord-bot-faucet.log"
echo
echo "Deamon service created for fastapi-faucet. To run it, use 'sudo systemctl start fastapi-faucet.service'"
echo "Logs will go to ~/logs/fastapi-faucet.log"
echo
