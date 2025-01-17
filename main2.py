import re
import json
import time
from io import BytesIO
from PIL import Image
import telebot

# TOKEN DETAILS
TOKEN = "TRON"
BOT_TOKEN = "7875776570:AAHtFXT-956iWbDx66ee5sBWeLOLRb_4Y1s"
PAYMENT_CHANNEL = "@safonai"  # add payment channel here including the '@' sign
OWNER_ID = 705635925  # write owner's user id here.. get it from @MissRose_Bot by /id
CHANNELS = ["@safonai"]  # add channels to be checked here in the format - ["Channel 1", "Channel 2"]
Daily_bonus = 0.00  # Put daily bonus amount here!
Mini_Withdraw = 500  # remove 0 and add the minimum withdraw you want to set
Per_Refer = 0.50  # add per refer bonus here

bot = telebot.TeleBot(BOT_TOKEN)

bonus = {}

def check_payment_receipt(message):
    try:
        if message.text.startswith("Payment Receipt:"):
            payment_info = re.findall(r'\d+\.[0-9]{2} [A-Za-z]{3}\b', message.text)
            if len(payment_info) == 0:
                bot.send_message(message.chat.id, "❌*Please include the payment amount in your message.*", parse_mode="Markdown")
                return
            payment_amount = float(payment_info[0].split()[0])
            if payment_amount < Mini_Withdraw:
                bot.send_message(message.chat.id, f"❌*Minimum payment to use the bot is {Mini_Withdraw} {TOKEN}. You paid {payment_amount} {TOKEN}.*", parse_mode="Markdown")
                return
            if message.media:
                if message.media.document and message.media.document.mime_type.startswith('image/'):
                    receipt_photo = message.media.document.file_id
                    file_info = bot.get_file(receipt_photo)
                    downloaded_file = bot.download_file(file_info.file_path)
                    receipt_bytes = BytesIO(downloaded_file)
                    image = Image.open(receipt_bytes)
                    image.verify()  # Verify if the image is valid
                    bot.send_message(message.chat.id, "👍*Your payment receipt has been received.*", parse_mode="Markdown")
                    bot.send_message(OWNER_ID, "💳*New Payment Receipt from @{}*\n💸*Amount - {} {}\n*Payment Receipt Image*".format(message.from_user.username, payment_amount, TOKEN))
                    with open('paid_users.json', 'r+') as file:
                        data = json.load(file)
                        if str(message.chat.id) not in data:
                            data[str(message.chat.id)] = True
                            file.seek(0)
                            json.dump(data, file)
                        else:
                            bot.send_message(message.chat.id, "⚠️*You have already paid the fee.*", parse_mode="Markdown")
                            return
                else:
                    bot.send_message(message.chat.id, "⚠️*Please attach the payment receipt as an image.*", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "⚠️*Please attach the payment receipt.*", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️*Something went wrong.*", parse_mode="Markdown")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!\nError on command: check_payment_receipt\nError details: "+str(e))
        return

@bot.message_handler(func=lambda message: message.text and message.text.startswith("Payment Receipt:"))
def payment_receipt_handler(message):
    check_payment_receipt(message)

def withdraw_keyboard(user_id):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(telebot.types.InlineKeyboardButton(text='💸 Withdraw', callback_data='withdraw'))
    keyboard.add(telebot.types.InlineKeyboardButton(text='Payment Receipt', callback_data='payment_receipt'))
    return keyboard

def withdraw_message(user_id):
    with open('users.json', 'r') as file:
        data = json.load(file)
    user_balance = data['balance'].get(str(user_id), 0)
    return f"*Your Balance: {user_balance} {TOKEN}*\n\nSend /withdraw to withdraw or /payment_receipt to submit your payment receipt.\n\n*Note: You must pay the initial fee to use the bot.*\nUse /settings to set your wallet and /help for more info.\n"

@bot.callback_query_handler(func=lambda call: call.data == 'withdraw')
def withdraw_callback(call):
    user_id = call.from_user.id
    if user_id not in bonus:
        check_payment_receipt(call.message)
    else:
        bot.send_message(call.message.chat.id, "⚠️*You have already taken the bonus for today.*", parse_mode="Markdown")

def menu(id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🆔 Account')
    keyboard.row('🙌🏻 Referrals', '🎁 Bonus', '💸 Withdraw')
    keyboard.row('⚙️ Set Wallet', '📊Statistics')
    bot.send_message(id, "*🏡 Home*", parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user = str(message.chat.id)
        data = json.load(open('users.json', 'r'))
        if user not in data['referred']:
            data['referred'][user] = 0
            data['total'] += 1
        if user not in data['referby']:
            data['referby'][user] = user
        if user not in data['checkin']:
            data['checkin'][user] = 0
        if user not in data['DailyQuiz']:
            data['DailyQuiz'][user] = "0"
        if user not in data['balance']:
            data['balance'][user] = 0
        if user not in data['wallet']:
            data['wallet'][user] = "none"
        if user not in data['withd']:
            data['withd'][user] = 0
        if user not in data['id']:
            data['id'][user] = data['total']
        json.dump(data, open('users.json', 'w'))
        print(data)

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='🤼‍♂️ Joined', callback_data='check'))
        msg_start = "*🍔 To Use This Bot You Need To Join This Channel - "
        for i in CHANNELS:
            msg_start += f"\n➡️ {i}\n"
        msg_start += "*"
        bot.send_message(user, msg_start, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, "This command has an error, please wait for fixing by admin")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!\n Error on command: " + message.text)
        return

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    try:
        ch = check(call.message.chat.id)
        if call.data == 'check':
            if ch:
                data = json.load(open('users.json', 'r'))
                user_id = call.message.chat.id
                bot.answer_callback_query(callback_query_id=call.id, text='✅ You joined. Now you can earn money')
                bot.delete_message(call.message.chat.id, call.message.message_id)
                if str(user_id) not in data['refer']:
                    data['refer'][str(user_id)] = True
                    if str(user_id) not in data['referby']:
                        data['referby'][str(user_id)] = str(user_id)
                        json.dump(data, open('users.json', 'w'))
                    if int(data['referby'][str(user_id)]) != user_id:
                        ref_id = data['referby'][str(user_id)]
                        ref = str(ref_id)
                        if ref not in data['balance']:
                            data['balance'][ref] = 0
                        if ref not in data['referred']:
                            data['referred'][ref] = 0
                        json.dump(data, open('users.json', 'w'))
                        data['balance'][ref] += Per_Refer
                        data['referred'][ref] += 1
                        bot.send_message(ref_id, f"*🏧 New Referral on Level 1, You Got : +{Per_Refer} {TOKEN}*", parse_mode="Markdown")
                        json.dump(data, open('users.json', 'w'))
                        return menu(call.message.chat.id)
                    else:
                        json.dump(data, open('users.json', 'w'))
                        return menu(call.message.chat.id)
            else:
                bot.answer_callback_query(callback_query_id=call.id, text='❌ You are not Joined')
                bot.delete_message(call.message.chat.id, call.message.message_id)
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(text='🤼‍♂️ Joined', callback_data='check'))
                msg_start = "*🍔 To Use This Bot You Need To Join This Channel - \n➡️ @ Fill your channels at line: 101 and 157*"
                bot.send_message(call.message.chat.id, msg_start, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        bot.send_message(call.message.chat.id, "This command has an error, please wait for fixing by admin")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!\n Error on command: " + call.data)
        return

@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        if message.text == '🆔 Account':
            data = json.load(open('users.json', 'r'))
            accmsg = '*👮 User : {}\n\n⚙️ Wallet : *`{}`*\n\n💸 Balance : *`{}`* {}*'
            user_id = message.chat.id
            user = str(user_id)

            if user not in data['balance']:
                data['balance'][user] = 0
            if user not in data['wallet']:
                data['wallet'][user] = "none"

            json.dump(data, open('users.json', 'w'))

            balance = data['balance'][user]
            wallet = data['wallet'][user]
            msg = accmsg.format(message.from_user.first_name, wallet, balance, TOKEN)
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")

        if message.text == '🙌🏻 Referrals':
            data = json.load(open('users.json', 'r'))
            ref_msg = "*⏯️ Total Invites : {} Users\n\n👥 Referrals System\n\n1 Level:\n🥇 Level°1 - {} {}\n\n🔗 Referral Link ⬇️\n{}*"
            bot_name = bot.get_me().username
            user_id = message.chat.id
            user = str(user_id)

            if user not in data['referred']:
                data['referred'][user] = 0
            json.dump(data, open('users.json', 'w'))

            ref_count = data['referred'][user]
            ref_link = 'https://telegram.me/{}?start={}'.format(bot_name, message.chat.id)
            msg = ref_msg.format(ref_count, Per_Refer, TOKEN, ref_link)
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")

        if message.text == "⚙️ Set Wallet":
            user_id = message.chat.id
            user = str(user_id)

            keyboard = telebot.types.ReplyKeyboardMarkup(True)
            keyboard.row('🚫 Cancel')
            send = bot.send_message(message.chat.id, "_⚠️Send your TRX Wallet Address._", parse_mode="Markdown", reply_markup=keyboard)
            bot.register_next_step_handler(message, trx_address)

        if message.text == "🎁 Bonus":
            user_id = message.chat.id
            user = str(user_id)
            cur_time = int((time.time()))
            data = json.load(open('users.json', 'r'))
            if (user_id not in bonus.keys()) or (cur_time - bonus[user_id] > 60 * 60 * 24):
                data['balance'][user] += Daily_bonus
                bot.send_message(user_id, f"Congrats you just received {Daily_bonus} {TOKEN}")
                bonus[user_id] = cur_time
                json.dump(data, open('users.json', 'w'))
            else:
                bot.send_message(message.chat.id, "❌*You can only take bonus once every 24 hours!*", parse_mode="Markdown")
            return

        if message.text == "📊Statistics":
            user_id = message.chat.id
            user = str(user_id)
            data = json.load(open('users.json', 'r'))
            msg = "*📊 Total members : {} Users\n\n🥊 Total successful Withdraw : {} {}*"
            msg = msg.format(data['total'], data.get('totalwith', 0), TOKEN)
            bot.send_message(user_id, msg, parse_mode="Markdown")
            return

        if message.text == "💸 Withdraw":
            user_id = message.chat.id
            user = str(user_id)

            data = json.load(open('users.json', 'r'))
            if user not in data['balance']:
                data['balance'][user] = 0
            if user not in data['wallet']:
                data['wallet'][user] = "none"
            json.dump(data, open('users.json', 'w'))

            bal = data['balance'][user]
            wall = data['wallet'][user]
            if wall == "none":
                bot.send_message(user_id, "_❌ Wallet Not set_", parse_mode="Markdown")
                return
            if bal >= Mini_Withdraw:
                bot.send_message(user_id, "_Enter Your Amount_", parse_mode="Markdown")
                bot.register_next_step_handler(message, amo_with)
            else:
                bot.send_message(user_id, f"_❌ Your balance is low, you should have at least {Mini_Withdraw} {TOKEN} to Withdraw_", parse_mode="Markdown")
                return
    except Exception as e:
        bot.send_message(message.chat.id, "This command has an error, please wait for fixing by admin")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!\n Error on command: " + message.text)
        return

def trx_address(message):
    try:
        if message.text == "🚫 Cancel":
            return menu(message.chat.id)
        if len(message.text) == 34:
            user_id = message.chat.id
            user = str(user_id)
            data = json.load(open('users.json', 'r'))
            data['wallet'][user] = message.text
            bot.send_message(message.chat.id, "*💹 Your TRX wallet is set to " + data['wallet'][user] + "*", parse_mode="Markdown")
            json.dump(data, open('users.json', 'w'))
            return menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, "*⚠️ It's Not a Valid TRX Address!*", parse_mode="Markdown")
            return menu(message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, "This command has an error, please wait for fixing by admin")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!\n Error on command: " + message.text)
        return

def amo_with(message):
    try:
        user_id = message.chat.id
        amo = message.text
        user = str(user_id)
        data = json.load(open('users.json', 'r'))
        if user not in data['balance']:
            data['balance'][user] = 0
        if user not in data['wallet']:
            data['wallet'][user] = "none"
        json.dump(data, open('users.json', 'w'))

        bal = data['balance'][user]
        wall = data['wallet'][user]
        msg = message.text
        if not msg.isdigit():
            bot.send_message(user_id, "_📛 Invalid value. Enter only numeric value. Try again_", parse_mode="Markdown")
            return
        if int(message.text) < Mini_Withdraw:
            bot.send_message(user_id, f"_❌ Minimum withdraw is {Mini_Withdraw} {TOKEN}_", parse_mode="Markdown")
            return
        if int(message.text) > bal:
            bot.send_message(user_id, "_❌ You Can't withdraw More than Your Balance_", parse_mode="Markdown")
            return
        amo = int(amo)
        data['balance'][user] -= amo
        data['totalwith'] = data.get('totalwith', 0) + amo
        bot_name = bot.get_me().username
        json.dump(data, open('users.json', 'w'))
        bot.send_message(user_id, "✅* Withdraw is requested to our owner automatically\n\n💹 Payment Channel :- " + PAYMENT_CHANNEL + "*", parse_mode="Markdown")

        markupp = telebot.types.InlineKeyboardMarkup()
        markupp.add(telebot.types.InlineKeyboardButton(text='🍀 BOT LINK', url=f'https://telegram.me/{bot_name}?start={OWNER_ID}'))

        send = bot.send_message(PAYMENT_CHANNEL, "✅* New Withdraw\n\n⭐ Amount - " + str(amo) + f" {TOKEN}\n🦁 User - @" + message.from_user.username + "\n💠 Wallet* - `" + data['wallet'][user] + "`\n☎️ *User Referrals = " + str(data['referred'][user]) + "\n\n🏖 Bot Link - @" + bot_name + "\n⏩ Please wait our owner will confirm it*", parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markupp)
    except Exception as e:
        bot.send_message(message.chat.id, "This command has an error, please wait for fixing by admin")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!\n Error on command: " + message.text)
        return

if __name__ == '__main__':
    bot.polling(none_stop=True)
