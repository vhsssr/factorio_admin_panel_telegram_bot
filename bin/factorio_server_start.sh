#!/bin/bash

# path to saves
SAVES_DIR="/opt/factorio/saves"

# if no args, show available list of saves and choose one from the list
if [ -z "$1" ]; then
  echo "Available save files:"
  ls $SAVES_DIR/*.zip | xargs -n 1 basename
  read -p "Enter the save file name (without .zip): " SAVE_NAME
else
  SAVE_NAME="$1"
fi

SAVE_FILE="$SAVES_DIR/$SAVE_NAME.zip"

# check if file exist
if [ ! -f "$SAVE_FILE" ]; then
  echo "Save file $SAVE_FILE does not exist."
  exit 1
fi

# Stopping server
echo "Stopping Factorio server..."
sudo systemctl stop factorio

# re-launch server with provided save name file
echo "Starting Factorio server with save $SAVE_FILE..."
sudo sed -i "s|--start-server .*|--start-server $SAVE_FILE|" /etc/systemd/system/factorio.service

# resest systemctl status to apply changes
sudo systemctl daemon-reload

# launch server
sudo systemctl start factorio

echo "Factorio server started with save $SAVE_FILE."
