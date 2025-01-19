#!/bin/bash

# path to bot file
BOT_PATH=$(cd "$PWD/.." && pwd)/bot.py
SERVICE_NAME="t_bot"
PYTHON_PATH=$(which python || which python3)

# check existence bot.py
if [ ! -f "$BOT_PATH" ]; then
    echo "Error: Couldnt find file bot.py in $BOT_PATH"
    exit 1
fi

# Creating systemd unit for the bot
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Creating service file $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Telegram Bot
After=network.target

[Service]
ExecStart=$PYTHON_PATH $BOT_PATH
WorkingDirectory=$(dirname "$BOT_PATH")
Restart=on-failure
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

# Configuring and restarting systemd
echo "Reload systemd and launching service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Service $SERVICE_NAME installed and running."
