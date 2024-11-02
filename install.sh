#!/bin/bash

echo "installing bot service, make sure you set all needed paths"
chmod +x install_bot_service.sh
./install_bot_service.sh

echo "installing factorio service"
chmod +x install_factorio.sh
sudo ./install_factorio.sh
