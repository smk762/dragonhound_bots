#!/bin/bash
mkdir -p atomicdex
cd atomicdex
rm mm2
rm coins
wget $(curl -vvv https://api.github.com/repos/KomodoPlatform/atomicDEX-API/releases | jq -r '.[0].assets | map(select(.name | contains("Linux-Release."))) | .[0].browser_download_url') -O mm2.zip
unzip mm2.zip
rm mm2.zip
wget https://raw.githubusercontent.com/KomodoPlatform/coins/master/coins -O coins
cd ..
