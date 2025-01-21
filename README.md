# Factorio Admin Panel Telegram Bot

This project is a Telegram bot to help manage a Factorio server. It allows server admins to control and monitor their Factorio server directly from Telegram, making server management more accessible and efficient.

## Features

- Start and stop the Factorio server from Telegram
- Execute Factorio console commands remotely
- Monitor the server's status (online/offline, player count, etc.)
- Notify admins about specific server events (e.g., player joining/leaving)

## Requirements

- **Python 3.8+**
- **Telegram Bot API Token** - You can create one with [BotFather](https://core.telegram.org/bots#botfather)
- **Factorio Server** - Installed and accessible from the system running this bot
- **Dependencies** - Listed in `requirements.txt`

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vhsssr/factorio_admin_panel_telegram_bot.git
   cd factorio_admin_panel_telegram_bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   shell prerequisites:   
   ```bash
      sudo yum install wget -y
      sudo yum install pip -y
      sudo yum install firewalld -y
      sudo systemctl start firewalld
      sudo systemctl enable firewalld

   ```


3. Configure environment variables:
   - **`TELEGRAM_BOT_TOKEN`**: Your Telegram Bot API token
   - **`ADMIN_CHAT_ID`**: Your Telegram user ID for admin-only commands as a list, e.g. ```['user1','user2']```

   Create a `.env` file in the project root and add the following:

   ```plaintext
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ADMIN_CHAT_ID=['user1','user2']
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

Once the bot is running, you can interact with it via Telegram. Use `/start` to initiate the bot and get available commands. Only the admin (based on `ADMIN_CHAT_ID`) can run server commands.

### Available Commands

- **/start** - Start the bot and view available commands
- **/status** - Check if the Factorio server is running
- **/start_server** - Start the Factorio server
- **/stop_server** - Stop the Factorio server
- **/players** - Show the list of online players
- **/send [message]** - Send a message to the Factorio server console

## Contributing

Feel free to open issues or submit pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License. See `LICENSE` for details.
```

---

This file provides an overview, setup instructions, usage examples, and contribution guidelines to help users get started with the bot quickly. Let me know if there are additional customizations or details specific to this project!