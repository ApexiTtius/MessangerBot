import telebot
from datetime import datetime
from getsettings import getset
import time
import logging

# Configure logging to record errors to a file.  This is highly recommended for production bots.
logging.basicConfig(filename='bot.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

token, Chats = getset("settings.txt")
bot = telebot.TeleBot(token)

# Rate limiting parameters (adjust as needed based on Telegram's rate limits)
REQUEST_LIMIT = 30  # Maximum number of requests per time window
TIME_WINDOW = 60  # Time window in seconds
requests_made = 0
last_request_time = time.time()


def send_with_rate_limit(message, chat_id, message_thread_id=None, caption=None):
    global requests_made, last_request_time

    time_since_last_request = time.time() - last_request_time

    if time_since_last_request < TIME_WINDOW and requests_made >= REQUEST_LIMIT:
        sleep_time = TIME_WINDOW - time_since_last_request
        logging.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)
        requests_made = 0

    try:
        if message.animation:
            bot.send_animation(chat_id, message.animation.file_id, caption=caption, message_thread_id=message_thread_id)
        elif message.photo:
            bot.send_photo(chat_id, message.photo[-1].file_id, caption=caption, message_thread_id=message_thread_id)
        elif message.sticker:
            bot.send_sticker(chat_id, message.sticker.file_id, message_thread_id=message_thread_id)
        requests_made += 1
        last_request_time = time.time()
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 429:
            retry_after = int(e.description.split(": ")[1].split()[0])
            logging.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            send_with_rate_limit(message, chat_id, message_thread_id)  #Retry
        else:
            logging.exception(f"Telegram API error: {e}")


@bot.message_handler(content_types=['animation', 'photo', 'sticker'], func=lambda message: message.chat.type == 'private')
def handle_gif(message):
    date_time = message.date
    formatted_date_time = datetime.fromtimestamp(date_time).strftime("%Y-%m-%d %H:%M:%S")
    logm = f"Дата: {formatted_date_time}\nПользователь: {message.chat.username} {message.chat.first_name} {message.chat.last_name}"

    if message.sticker:
        send_with_rate_limit(message, Chats[0][0], int(Chats[0][1]))
        bot.forward_message(from_chat_id=message.chat.id, chat_id=Chats[1], message_id=message.message_id)

    else:
        send_with_rate_limit(message, Chats[0][0], int(Chats[0][1]))
        send_with_rate_limit(message, Chats[1], caption=logm)


if __name__ == "__main__":
    while(True):
        try:
            bot.polling(none_stop=True)
        except:
            time.sleep(60)
