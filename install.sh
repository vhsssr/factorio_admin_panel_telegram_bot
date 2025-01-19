#!/bin/bash

git config --global --add safe.directory "$(git rev-parse --show-toplevel)"

echo "installing bot service, make sure you set all needed paths"
chmod +x ./bin/install_bot_service.sh
sudo ./bin/install_bot_service.sh

echo "installing factorio service"
chmod +x ./bin/install_factorio.sh
sudo ./bin/install_factorio.sh
