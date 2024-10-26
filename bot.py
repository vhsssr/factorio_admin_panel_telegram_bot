import os
import telebot
from telebot import types
import subprocess

# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot = telebot.TeleBot(BOT_TOKEN)

# Directory path for save files
SAVES_DIR = '/opt/factorio/saves'

# List of allowed users (use ID or username)
ALLOWED_USERS = ['fsd', 'dgsg']  # Replace with allowed usernames


def is_user_allowed(user_id):
    user = bot.get_chat(user_id)
    return user.username in ALLOWED_USERS


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Hello! Use the /saves command to select a save file or /file to upload a file.")


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
    # Remove .zip extension if present
    save_file_name = os.path.splitext(save_file)[0]
    factorio_command = "/root/bin/start_factorio.sh"

    if action == "yes":
        # Run the command to restart the server with the selected save file
        try:
            bot.send_message(call.message.chat.id, save_file_name)
            result = subprocess.run([factorio_command, save_file_name], capture_output=True, text=True)
            if result.returncode != 0:
                bot.send_message(call.message.chat.id, f"server not restarted : {result.stderr}")
            else:
                bot.send_message(call.message.chat.id, f"save loaeded : '{save_file}'.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Err happen: {str(e)}")

    # bot.send_message(call.message.chat.id, f"Server restarted with save file '{save_file}'.")
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
    # Retrieve the file from the message
    file_id = message.document.file_id
    file_name = message.document.file_name

    # Download and save the file in the specified directory
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the file on the server
    file_path = os.path.join(SAVES_DIR, file_name)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, f"File '{file_name}' successfully saved to '{SAVES_DIR}'.")


if __name__ == '__main__':
    bot.polling(none_stop=True)