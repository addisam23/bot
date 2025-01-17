import re

import json

import time

from PIL import Image

from io import BytesIO

import telebot


# TOKEN DETAILS

TOKEN = "TRON"

BOT_TOKEN = "7875776570:AAHtFXT-956iWbDx66ee5sBWeLOLRb_4Y1s"

PAYMENT_CHANNEL = "@safonai"  # add payment channel here including the '@' sign

OWNER_ID = 705635925  # write owner's user id here

CHANNELS = ["@safonai"]  # add channels to be checked here

Daily_bonus = 0.00  # Put daily bonus amount here

Mini_Withdraw = 500  # Minimum withdraw amount

Per_Refer = 0.50  # Per referral bonus


bot = telebot.TeleBot(BOT_TOKEN)

bonus = {}



def check_payment_receipt(message):

    try:

        if message.text.startswith("Payment Receipt:"):

            # Get payment details from the message text

            payment_info = re.findall(r'\d+\.[0-9]{2} [A-Za-z]{3}\b', message.text)

            if not payment_info:

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

                    bot.send_message(OWNER_ID, f"💳*New Payment Receipt from @{message.from_user.username}*\n💸*Amount - {payment_amount} {TOKEN}*\n*Payment Receipt Image*")


                    # Add the user to a list of paid users

                    with open('paid_users.json', 'r+') as file:

                        data = json.load(file)

                        if str(message.chat.id) not in data:

                            data[str(message.chat.id)] = True

                            file.seek(0)

                            json.dump(data, file)

                            file.truncate()

                        else:

                            bot.send_message(message.chat.id, "⚠️*You have already paid the fee.*", parse_mode="Markdown")

                else:

                    bot.send_message(message.chat.id, "⚠️*Please attach the payment receipt as an image.*", parse_mode="Markdown")

            else:

                bot.send_message(message.chat.id, "⚠️*Please attach the payment receipt.*", parse_mode="Markdown")

    except Exception as e:

        bot.send_message(message.chat.id, "⚠️*Something went wrong.*", parse_mode="Markdown")

        bot.send_message(OWNER_ID, f"Your bot got an error. Fix it fast!\nError on command: check_payment_receipt\nError details: {str(e)}")



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



def menu(user_id):

    keyboard = telebot.types.ReplyKeyboardMarkup(True)

    keyboard.row('🆔 Account')

    keyboard.row('🙌🏻 Referrals', '🎁 Bonus', '💸 Withdraw')

    keyboard.row('⚙️ Set Wallet', '📊 Statistics')

    bot.send_message(user_id, "*🏡 Home*", parse_mode="Markdown", reply_markup=keyboard)



@bot.message_handler(commands=['start'])

def start(message):

    try:

        user_id = str(message.chat.id)

        data = {}


        # Load or initialize users.json

        try:

            with open('users.json', 'r') as file:

                data = json.load(file)

        except FileNotFoundError:

            data = {

                'referred': {},

                'total': 0,

                'referby': {},

                'checkin': {},

                'DailyQuiz': {},

                'balance': {},

                'wallet': {},

                'withd': {},

                'id': {}

            }


        if user_id not in data['referred']:

            data['referred'][user_id] = 0

            data['total'] += 1

        if user_id not in data['referby']:

            data['referby'][user_id] = user_id

        if user_id not in data['checkin']:

            data['checkin'][user_id] = 0

        if user_id not in data['DailyQuiz']:

            data['DailyQuiz'][user_id] = "0"

        if user_id not in data['balance']:

            data['balance'][user_id] = 0

        if user_id not in data['wallet']:

            data['wallet'][user_id] = "none"

        if user_id not in data['withd']:

            data['withd'][user_id] = 0

        if user_id not in data['id']:

            data['id'][user_id] = data['total'] + 1


        with open('users.json', 'w') as file:

            json.dump(data, file)


        markup = telebot.types.InlineKeyboardMarkup()

        markup.add(telebot.types.InlineKeyboardButton(text='🤼‍♂️ Joined', callback_data='check'))

        msg_start = "*🍔 To Use This Bot You Need To Join This Channel - "

        for channel in CHANNELS:

            msg_start += f"\n➡️ {channel}\n"

        msg_start += "*"

        bot.send_message(user_id, msg_start, parse_mode="Markdown", reply_markup=markup)

    except Exception as e:

        bot.send_message(message.chat.id, "This command has an error, please wait for fixing by admin")

        bot.send_message(OWNER_ID, f"Your bot got an error. Fix it fast!\nError on command: {message.text}\nError details: {str(e)}")



@bot.callback_query_handler(func=lambda call: True)

def query_handler(call):

    try:

        ch = check(call.message.chat.id)

        if call.data == 'check':

            if ch:

                user_id = str(call.message.chat.id)

                data = json.load(open('users.json', 'r'))


                bot.answer_callback_query(callback_query_id=call.id, text='✅ You joined. Now you can earn money')

                bot.delete_message(call.message.chat.id, call.message.message_id)


                if user_id not in data['refer']:

                    data['refer'][user_id] = True


                    if user_id not in data['referby']:

                        data['referby'][user_id] = user_id

                        json.dump(data, open('users.json', 'w'))


                    ref_id = data['referby'][user_id]

                    if ref_id != user_id:

                        if ref_id not in data['balance']:

                            data['balance'][ref_id] = 0

                        if ref_id not in data['referred']:

                            data['referred'][ref_id] = 0


                        data['balance'][ref_id] += Per_Refer

                        data['referred'][ref_id] += 1

                        bot.send_message(ref_id, f"*🏧 New Referral on Level 1, You Got : +{Per_Refer} {TOKEN}*", parse_mode="Markdown")


                    json.dump(data, open('users.json', 'w'))

                    return menu(call.message.chat.id)


                else:

                    json.dump(data, open('users.json', 'w'))

                    return menu(call.message.chat.id)


            else:

                bot.answer_callback_query(callback_query_id=call.id, text='❌ You have not joined')

                bot.delete_message(call.message.chat.id, call.message.message_id)

                markup = telebot.types.InlineKeyboardMarkup()

                markup.add(telebot.types.InlineKeyboardButton(text='🤼‍♂️ Joined', callback_data='check'))

                msg_start = "*🍔 To Use This Bot You Need To Join This Channel - \n➡️ @ Fill your channels at line: 101*"

                bot.send_message(call.message.chat.id, msg_start, parse_mode="Markdown", reply_markup=markup)

    except Exception as e:

        bot.send_message(call.message.chat.id, "This command has an error, please wait for fixing by admin")

        bot.send_message(OWNER_ID, f"Your bot got an error. Fix 
