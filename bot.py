import telebot
import time
import threading
from datetime import datetime, timedelta

# CONFIG ---------------------------------------------
token='' # Token from BotFather

language = "en"                                        # Bot Language
blocked_urls = ["tiktok.ru","iplogger.com"]            # Blocked URLs in message.text
bot_can_send_messages = True                           # Determines whether the bot can send messages to chat
max_messages_in_list = 6                               # How much messages can write in bot memory
max_users_in_list = 10                                 # How much users can join in 100 seconds
bot_can_block_admin_messages = False                   # Admin immunity to bot
contact_username = "linusunix"                         # Username for contact
max_symbols_in_message = 2000                          # Maximum number of allowed characters
# ----------------------------------------------------
lastsms = []
lastuser = []

strings = {
    "ru": {
        "welcome": "Добро пожаловать, {}.",
        "description": "Этот бот создан для предотвращения спама и флуда.",
        "sus_msg": "Подозрительное сообщение удалено. Если ваше сообщение было удалено по ошибке, пожалуйста, свяжитесь с @{}.",
    },
    "en": {
        "welcome": "Welcome, {}.",
        "description": "This bot is designed to prevent spam and flooding.",
        "sus_msg": "The suspicious message has been deleted. If your message was deleted by mistake, please contact @{}.", 
    }
}

def get_string(lang=language, key=None):
    try:
        return strings[lang][key]
    except KeyError:
        return key

if bot_can_block_admin_messages:
    memberstatus = ["administator", "owner", "member"]
else:
    memberstatus = ["member"]
bot=telebot.TeleBot(token)

def calc_ident(lst, target_value, min_total=max_messages_in_list):
    if not lst:
        return 0.0
    
    real_count = sum(1 for item in lst if item == target_value)

    if len(lst) < min_total:
        fake_penalty = min_total - len(lst)
        total_elements = len(lst) + fake_penalty
    else:
        total_elements = len(lst)
    
    return (real_count / total_elements) * 100

def clean_memory_sms():
    while 1:
        time.sleep(30)
        if len(lastsms) < 7:
            lastsms.clear()
        
def clean_memory_user():
    while 1:
        if len(lastuser) > 0:
            time.sleep(100)
            lastuser.clear()
        else:
            time.sleep(1)
        

threading.Thread(target=clean_memory_user).start()
threading.Thread(target=clean_memory_sms).start()

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,get_string(key="description"))

@bot.message_handler(content_types=["new_chat_members"])
def handle_new_member(message):
    if message.chat.type == "channel":
        return
    
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            continue
            
        lastuser.append(user.id)
        
        if len(lastuser) > 10:
            try:
                until_date = datetime.now() + timedelta(days=1)
                bot.ban_chat_member(
                    chat_id=message.chat.id,
                    user_id=user.id,
                    until_date=until_date
                )
            except Exception as e:
                return
        else:
            if bot_can_send_messages:
                bot.send_message(message.chat.id, get_string(key="welcome").format(user.first_name))
@bot.message_handler(content_types='text')
def check_message(message):
    if message.chat.type != 'channel':
        threading.Thread(target=message_reply,args=[message]).start()

def message_reply(message):
    if bot.get_chat_member(user_id=message.from_user.id,chat_id=message.chat.id).status in memberstatus:
        if len(message.text) > max_symbols_in_message:
            try:
                bot.delete_message(message_id=message.id,chat_id=message.chat.id)
            except Exception as e:
                print(e)
            else:
                if bot_can_send_messages:
                    bot_message = bot.send_message(message.chat.id, get_string(key="sus_msg").format(contact_username))
                    time.sleep(3)
                    bot.delete_message(message_id=bot_message.id,chat_id=bot_message.chat.id)
        if len(lastsms) > max_messages_in_list:
            lastsms.clear()
        
    if calc_ident(lastsms, message.from_user.id) > 80:
        try:
            bot.delete_message(message_id=message.id,chat_id=message.chat.id)
        except Exception as e:
            print(e)
        else:
            if bot_can_send_messages:
                bot_message = bot.send_message(message.chat.id, get_string(key="sus_msg").format(contact_username))
                time.sleep(3)
                bot.delete_message(message_id=bot_message.id,chat_id=bot_message.chat.id)

    for i in range(len(blocked_urls)):
        if blocked_urls[i] in message.text:
            try:
                bot.delete_message(message_id=message.id,chat_id=message.chat.id)
            except Exception as e:
                print(e)
            else:
                if bot_can_send_messages:
                    bot_message = bot.send_message(message.chat.id, get_string(key="sus_msg").format(contact_username))
                    time.sleep(3)
                    bot.delete_message(message_id=bot_message.id,chat_id=bot_message.chat.id)
    lastsms.append(message.from_user.id)

bot.infinity_polling(none_stop = True)
