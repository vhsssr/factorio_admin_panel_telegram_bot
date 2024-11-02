#!/bin/bash

# Parameters
FACTORIO_USER="factorio"
FACTORIO_DIR="/opt/factorio"
FACTORIO_VERSION="stable"  # Replace with the desired version
FACTORIO_SAVE="my-save.zip"
SYSTEMD_FILE="/etc/systemd/system/factorio.service"

# Function to exit with an error message
function exit_with_error {
  echo "$1"
  exit 1
}

# 1. Create a system user for Factorio
echo "Creating user $FACTORIO_USER..."
sudo useradd -r -m -d $FACTORIO_DIR -s /bin/false $FACTORIO_USER || exit_with_error "Failed to create user $FACTORIO_USER"

# 2. Download and install Factorio
echo "Downloading Factorio version $FACTORIO_VERSION..."
sudo mkdir -p $FACTORIO_DIR || exit_with_error "Failed to create directory $FACTORIO_DIR"
sudo chown $FACTORIO_USER:$FACTORIO_USER $FACTORIO_DIR

# Download Factorio
cd /tmp
wget https://factorio.com/get-download/$FACTORIO_VERSION/headless/linux64 -O factorio.tar.gz || exit_with_error "Failed to download Factorio"

# Extract to /opt/factorio
sudo tar -xzf factorio.tar.gz -C $FACTORIO_DIR --strip-components=1 || exit_with_error "Failed to extract Factorio"
rm factorio.tar.gz

# Create a directory for saves
sudo mkdir -p $FACTORIO_DIR/saves
sudo chown -R $FACTORIO_USER:$FACTORIO_USER $FACTORIO_DIR/saves

# 3. Create a default save file (optional)
echo "Creating a default save file..."
sudo -u $FACTORIO_USER $FACTORIO_DIR/bin/x64/factorio --create $FACTORIO_DIR/saves/$FACTORIO_SAVE || exit_with_error "Failed to create save file"

# 4. Create a systemd service file
echo "Creating systemd service file..."
sudo bash -c "cat > $SYSTEMD_FILE" <<EOL
[Unit]
Description=Factorio Headless Server
After=network.target

[Service]
Type=simple
User=$FACTORIO_USER
WorkingDirectory=$FACTORIO_DIR
ExecStart=$FACTORIO_DIR/bin/x64/factorio --start-server $FACTORIO_DIR/saves/$FACTORIO_SAVE
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable the Factorio service
echo "Enabling and starting Factorio service..."
sudo systemctl daemon-reload
sudo systemctl enable factorio.service || exit_with_error "Failed to enable Factorio service"
sudo systemctl start factorio.service || exit_with_error "Failed to start Factorio service"

echo "Factorio installation and service setup complete!"
