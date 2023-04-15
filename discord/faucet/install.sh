#!/bin/bash

mkdir -p ~/logs
mkdir atomicdex
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx curl libcurl4-openssl-dev libssl-dev
pip3 install virtualenv==20.21.0
virtualenv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

echo "Configuring environment..."
./configure.py env_vars

echo "Setting up AtomicDEX-API..."
./configure.py atomicdex
./stop_atomicdex.sh
./update_atomicdex.sh
SCRIPT_PATH=$(pwd)
echo "Creating service files..."
cp service/TEMPLATE-atomicdex.service service/atomicdex-api.service
sed "s|SCRIPT_PATH|${SCRIPT_PATH}|g" -i "service/atomicdex-api.service"
sed "s/USERNAME/${USER}/g" -i "service/atomicdex-api.service"

echo "Copying service files to /etc/systemd/system/..."
sudo cp service/atomicdex-api.service /etc/systemd/system/atomicdex-api.service

cd /etc/systemd/system/
sudo systemctl enable atomicdex-api.service
echo
echo "Deamon service created for atomicdex-api. To run it, use 'sudo systemctl start atomicdex-api.service'"
echo "Logs will go to ~/logs/atomicdex-api.log"
