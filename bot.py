import os
import json
import telebot
from telebot import types
import subprocess
import requests
from datetime import timedelta

# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot = telebot.TeleBot(BOT_TOKEN)

# Directory path for save files, Factorio server directory, and mods file
SAVES_DIR = '/opt/factorio/saves'
FACTORIO_DIR = '/opt/factorio'
FACTORIO_SERVICE_NAME = 'factorio'
MOD_LIST_PATH = os.path.join(FACTORIO_DIR, 'mods/mod-list.json')

# List of allowed users for restricted commands
ALLOWED_USERS = ['fsd', 'dgsg']  # Replace with allowed usernames


def is_user_allowed(user_id):
    user = bot.get_chat(user_id)
    return user.username in ALLOWED_USERS


def get_factorio_version():
    """Retrieve the current Factorio version from the executable."""
    try:
        result = subprocess.run([f"{FACTORIO_DIR}/bin/x64/factorio", "--version"], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else "Unknown version"
    except Exception as e:
        return f"Error retrieving version: {str(e)}"


SPACE_AGE_MODS = ["space-age", "quality", "elevated-rails"]  # List mods that are part of the "space-age" group


@bot.message_handler(commands=['mods'])
def space_age_mod(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "You do not have permission to execute this command.")
        return

    # Load mod status to check if "space-age" is enabled
    space_age_enabled = check_space_age_status()

    # Create inline buttons to enable or disable the "space-age" mod group
    markup = types.InlineKeyboardMarkup()
    action_text = "Disable Space-Age Mods" if space_age_enabled else "Enable Space-Age Mods"
    action_callback = "disable_space_age" if space_age_enabled else "enable_space_age"
    markup.add(types.InlineKeyboardButton(action_text, callback_data=action_callback))

    bot.send_message(message.chat.id, "Toggle the 'Space-Age' mod group:", reply_markup=markup)


def check_space_age_status():
    """Check if the 'space-age' mod and its dependencies are enabled in mod-list.json"""
    try:
        with open(MOD_LIST_PATH, 'r') as f:
            mod_list = json.load(f)

        # Check if all SPACE_AGE_MODS are enabled
        enabled_mods = {mod["name"]: mod["enabled"] for mod in mod_list.get("mods", [])}
        return all(enabled_mods.get(mod, False) for mod in SPACE_AGE_MODS)
    except Exception as e:
        bot.send_message(chat_id, f"Error checking mod status: {str(e)}")
        return False


@bot.callback_query_handler(func=lambda call: call.data in ["enable_space_age", "disable_space_age"])
def toggle_space_age_mod(call):
    enable_space_age = call.data == "enable_space_age"

    try:
        # Load the mod list
        with open(MOD_LIST_PATH, 'r') as f:
            mod_list = json.load(f)

        # Update the "enabled" status for all SPACE_AGE_MODS
        for mod in mod_list.get("mods", []):
            if mod["name"] in SPACE_AGE_MODS:
                mod["enabled"] = enable_space_age

        # Save the updated mod list
        with open(MOD_LIST_PATH, 'w') as f:
            json.dump(mod_list, f, indent=4)

        # Confirm changes to user and restart the server
        action_text = "enabled" if enable_space_age else "disabled"
        bot.send_message(call.message.chat.id, f"Space-Age mods have been {action_text}. Restarting server...")

        # Restart the Factorio server to apply changes
        subprocess.run(['sudo', 'systemctl', 'restart', FACTORIO_SERVICE_NAME])

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Error toggling Space-Age mods: {str(e)}")


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message,
                 "Hello! Use /saves to select a save file, \n"
                 "/file to upload a save file, \n"
                 "/mods to manage mods,  \n"
                 "/status to check server status \n"
                 "/version to check installed server version \n"
                 "/update_server to update factorio server version. \n")


@bot.message_handler(commands=['saves'])
def list_saves(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "You do not have permission to execute this command.")
        return

    # Get list of .zip files in the saves directory, excluding files with "autosave"
    saves = [f for f in os.listdir(SAVES_DIR) if f.endswith('.zip') and 'autosave' not in f]

    if not saves:
        bot.reply_to(message, "No save files available.")
        return

    # Create a keyboard to select the save file
    markup = types.InlineKeyboardMarkup()
    for save in saves:
        markup.add(types.InlineKeyboardButton(save, callback_data=f"select_{save}"))

    bot.send_message(message.chat.id, "Choose a save file:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def callback_query(call):
    save_file = call.data.replace("select_", "")
    # Ask for confirmation to use the selected save file
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Yes", callback_data=f"confirm_yes_{save_file}"),
        types.InlineKeyboardButton("No", callback_data=f"confirm_no")
    )

    bot.send_message(call.message.chat.id, f"Are you sure you want to select '{save_file}'?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_selection(call):
    data = call.data.split("_")
    action, save_file = data[1], "_".join(data[2:])
    save_file_name = os.path.splitext(save_file)[0]
    factorio_command = "/root/bin/start_factorio.sh"

    if action == "yes":
        try:
            bot.send_message(call.message.chat.id, save_file_name)
            result = subprocess.run([factorio_command, save_file_name], capture_output=True, text=True)
            if result.returncode != 0:
                bot.send_message(call.message.chat.id, f"Server not restarted: {result.stderr}")
            else:
                bot.send_message(call.message.chat.id, f"Save loaded: '{save_file_name}'.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Error occurred: {str(e)}")
    elif action == "no":
        bot.send_message(call.message.chat.id, "Selection canceled. Use /saves to choose again.")


@bot.message_handler(commands=['file'])
def file_command(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "You do not have permission to execute this command.")
        return
    bot.reply_to(message, "Send me a file, and I'll save it.")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_id = message.document.file_id
    file_name = message.document.file_name

    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_path = os.path.join(SAVES_DIR, file_name)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, f"File '{file_name}' successfully saved to '{SAVES_DIR}'.")


@bot.message_handler(commands=['status'])
def status_command(message):
    """Check and display server status."""
    try:
        # Get server status with `factorio` command or through system logs
        # Assuming this command returns active save file name, player count, and uptime
        result = subprocess.run(['sudo', 'systemctl', 'status', FACTORIO_SERVICE_NAME], capture_output=True, text=True)
        if result.returncode == 0:
            # Parsing simulated status output for demonstration purposes
            # Use actual command outputs if they differ
            save_file = "example_save"  # Extract save file name dynamically
            player_count = 5  # Extract player count dynamically
            uptime = timedelta(seconds=3600)  # Calculate actual uptime

            bot.reply_to(message, f"Server Status:\nSave: {save_file}\nPlayers: {player_count}\nUptime: {uptime}")
        else:
            bot.reply_to(message, "The server is currently stopped.")
    except Exception as e:
        bot.reply_to(message, f"Error retrieving server status: {str(e)}")

selected_mods = {}

@bot.message_handler(commands=['update_server'])
def update_server(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "You do not have permission to execute this command.")
        return

    url = "https://factorio.com/get-download/stable/headless/linux64"
    try:
        bot.reply_to(message, "Downloading latest Factorio server version...")
        response = requests.get(url)
        tar_path = os.path.join(FACTORIO_DIR, "factorio_headless.tar.xz")
        with open(tar_path, "wb") as file:
            file.write(response.content)
    except Exception as e:
        bot.reply_to(message, f"Error downloading server: {str(e)}")
        return

    try:
        subprocess.run(['sudo', 'systemctl', 'stop', FACTORIO_SERVICE_NAME], check=True)
        bot.reply_to(message, "Factorio server stopped.")
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"Failed to stop Factorio server: {e}")
        return

    try:
        subprocess.run(['sudo', 'tar', '-xJf', tar_path, '-C', FACTORIO_DIR, '--strip-components=1'], check=True)
        bot.reply_to(message, "Factorio server updated.")
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"Failed to extract server files: {e}")
        return

    try:
        subprocess.run(['sudo', 'systemctl', 'start', FACTORIO_SERVICE_NAME], check=True)
        bot.reply_to(message, "Factorio server started successfully.")
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"Failed to start Factorio server: {e}")
        return

    version = get_factorio_version()
    bot.reply_to(message, f"Updated Factorio version: {version}")


@bot.message_handler(commands=['version'])
def check_version(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "You do not have permission to execute this command.")
        return

    version = get_factorio_version()
    bot.reply_to(message, f"Current Factorio version: {version}")


if __name__ == '__main__':
    bot.polling(none_stop=True)
