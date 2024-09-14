import telebot
import time
import threading

# CONFIG ---------------------------------------------
token='' # Token from BotFather

blocked_urls = ["t.me","tiktok.ru","iplogger.com"]     # Blocked URLs in message.text
bot_can_send_messages = True                           # Determines whether the bot can send messages to chat
max_messages_in_list = 5                               # How much messages can write in bot memory
bot_can_block_admin_messages = True                    # Admin immunity to bot
contact_username = "huekx"                             # Username for contact
max_symbols_in_message = 2000                          # Maximum number of allowed characters
# ----------------------------------------------------
lastsms = []
if bot_can_block_admin_messages:
    memberstatus = ["administator", "owner", "member"]
else:
    memberstatus = ["member"]
bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,"🇷🇺 Этот бот создан для предотвращения спама и флуда.\n🇺🇸 This bot is designed to prevent spam and flooding.")
@bot.message_handler(content_types='text')
def check_message(message):
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
                    bot_message = bot.send_message(message.chat.id, f"The suspicious message has been deleted. If your message was deleted by mistake, please contact @{contact_username}.")
                    time.sleep(3)
                    bot.delete_message(message_id=bot_message.id,chat_id=bot_message.chat.id)
        if len(lastsms) > max_messages_in_list:
            lastsms.clear()
    
        if message.text in lastsms:
            try:
                bot.delete_message(message_id=message.id,chat_id=message.chat.id)
            except Exception as e:
                print(e)
            else:
                if bot_can_send_messages:
                    bot_message = bot.send_message(message.chat.id, f"The suspicious message has been deleted. If your message was deleted by mistake, please contact @{contact_username}.")
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
                    bot_message = bot.send_message(message.chat.id, f"The suspicious message has been deleted. If your message was deleted by mistake, please contact @{contact_username}.")
                    time.sleep(3)
                    bot.delete_message(message_id=bot_message.id,chat_id=bot_message.chat.id)
        print(f"{message.text} - from @{message.from_user.username}, {message.chat.title}")
        lastsms.append(message.text)
bot.infinity_polling(none_stop = True)
