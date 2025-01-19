#!/bin/bash

echo "installing bot service, make sure you set all needed paths"
chmod +x ./bin/install_bot_service.sh
sudo ./bin/install_bot_service.sh

echo "installing factorio service"
chmod +x ./bin/install_factorio.sh
sudo ./bin/install_factorio.sh
