```py
pip install telebot pillow
```
```python
import re
from PIL import Image
from io import BytesIO
from telebot import TeleBot, types

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
                if message.media.document:
                    if message.media.document.mime_type.startswith('image/'):
                        receipt_photo = message.media.document.get_file_id()
                        file_info = bot.get_file(receipt_photo)
                        downloaded_file = bot.download_file(file_info.file_path)
                        receipt_bytes = BytesIO()
                        receipt_bytes.write(downloaded_file)
                        receipt_bytes.seek(0)
                        image = Image.open(receipt_bytes)
                        image.verify()  # Verify if the image is valid
                        bot.send_message(message.chat.id, "👍*Your payment receipt has been received.*", parse_mode="Markdown")
                        # Here you can add the code to save the receipt to a directory on the server for admin review
                        # You can also notify the admin with the payment details and the receipt image
                        bot.send_message(OWNER_ID, "💳*New Payment Receipt from @{}*
💸*Amount - {} {}
*Payment Receipt Image*".format(message.from_user.username, payment_amount, TOKEN))
                        # Add the user to a list of paid users
                        with open('paid_users.json', 'r+') as file:
                            data = json.load(file)
                            if message.chat.id not in data:
                                data[message.chat.id] = True
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
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!
Error on command: check_payment_receipt
Error details: "+str(e))
        return

# Add this new button to the existing inline keyboard for the withdrawal process
def withdraw_keyboard(user_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton(
        text='💸 Withdraw', callback_data='withdraw'))
    keyboard.add(types.InlineKeyboardButton(
        text='Payment Receipt', callback_data='payment_receipt'))
    return keyboard

# Update the withdraw message to include the new payment receipt button
def withdraw_message(user_id):
    data = json.load(open('users.json', 'r'))
    user_balance = data['balance'].get(str(user_id), 0)
    return f"*Your Balance: {user_balance} {TOKEN}*

Send /withdraw to withdraw or /payment_receipt to submit your payment receipt.

*Note: You must pay the initial fee to use the bot.*
Use /settings to set your wallet and /help for more info."

# Update the withdraw button callback data to handle the payment receipt submission
@bot.callback_query_handler(func=lambda call: call.data == 'withdraw')
def withdraw_callback(call):
    user_id = call.from_user.id
    if user_id not in bonus:
        return check_payment_receipt(call.message)
    else:
        bot.send_message(call.message.chat.id, "⚠️*You have already taken the bonus for today.*", parse_mode="Markdown")

# Define the bot token and other constants
TOKEN = "TRON"
BOT_TOKEN = "7875776570:AAHtFXT-956iWbDx66ee5sBWeLOLRb_4Y1s"
OWNER_ID = 705635925
CHANNELS = ["@safonai"]
Mini_Withdraw = 500

bot = TeleBot(BOT_TOKEN)

# Main bot logic
@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.chat.id
        msg = message.text
        data = json.load(open('users.json', 'r'))
        if user_id not in data['referred']:
            data['referred'].update({str(user_id): 0})
            data['total'].update({str(user_id): 0})
        if user_id not in data['balance'].keys():
            data['balance'].update({str(user_id): 0})
        if user_id not in data['wallet'].keys():
            data['wallet'].update({str(user_id): "none"})
        if user_id not in data['withd'].keys():
            data['withd'].update({str(user_id): 0})
        json.dump(data, open('users.json', 'w'))
        balance = data['balance'].get(str(user_id), 0)
        wallet = data['wallet'].get(str(user_id), "none")
        bot.send_message(message.chat.id, f"*Welcome to {bot.get_me().first_name} Bot* \n\n"
                                      f"*Your TRX Address is {wallet}.*\n\n"
                                      f"*Your Current Balance is {balance} {TOKEN}.*", parse_mode="Markdown")
        bot.send_message(message.chat.id, "*Send /settings to set your TRX wallet.*", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "This command having error pls wait for ficing the glitch by admin")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!
Error on command: "+message.text)

# Handle messages
def handle_message(message):
    if message.text == '/settings':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row("Set Wallet", "Withdraw")
        bot.send_message(message.chat.id, "Choose an action", reply_markup=keyboard)
    elif message.text == 'Set Wallet':
        bot.send_message(message.chat.id, "Send your TRX wallet address.")
        bot.register_next_step_handler(message, set_wallet)
    elif message.text == 'Withdraw':
        bot.send_message(message.chat.id, withdraw_message(message.chat.id), parse_mode="Markdown")
    elif message.text == '/payment_receipt':
        bot.send_message(message.chat.id, "Send your payment receipt.")
        bot.register_next_step_handler(message, check_payment_receipt)

# Handle callback data
@bot.callback_query_handler(func=lambda call: call.data == 'payment_receipt')
def payment_receipt_callback(call):
    check_payment_receipt(call.message)

def set_wallet(message):
    user_id = message.chat.id
    try:
        data = json.load(open('users.json', 'r')).get('wallet')
        if len(message.text) == 34:
            if message.text not in data.values():
                data[str(user_id)] = message.text
                bot.send_message(message.chat.id, "Your TRX wallet has been set to " + message.text)
                json.dump({'balance': {}, 'wallet': data, 'withd': {}, 'referred': {}, 'total': 0}, open('users.json', 'w'))
            else:
                bot.send_message(message.chat.id, "Your TRX wallet is already set.")
        else:
            bot.send_message(message.chat.id, "Your TRX wallet is not set correctly.")
    except Exception as e:
        bot.send_message(message.chat.id, "This command having error pls wait for ficing the glitch by admin")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!
Error on command: set_wallet
Error details: "+str(e))

# Handle message text
@bot.message_handler(func=lambda message: message.text and message.text.startswith("/"))
def command_handler(message):
    cmd = message.text.split(" ", 1)[0].lower()
    args = message.text.split(" ", 1)[1:] if len(message.text.split()) > 1 else ""
    if cmd == '/withdraw':
        withdraw(message)
    elif cmd == '/payment_receipt':
        payment_receipt(message)
    elif cmd == '/settings':
        handle_message(message)
    else:
        bot.send_message(message.chat.id, "Unknown command.")

def withdraw(message):
    user_id = message.chat.id
    data = json.load(open('users.json', 'r')).get('balance', {})
    if user_id not in data:
        data[str(user_id)] = 0
        json.dump({'balance': data, 'wallet': {}, 'withd': {}, 'referred': {}, 'total': 0}, open('users.json', 'w'))
    bot.send_message(message.chat.id, f"*Withdraw {data.get(str(user_id), 0)} {TOKEN}?*", parse_mode="Markdown")
    bot.register_next_step_handler(message, withdraw_confirm)

def withdraw_confirm(message):
    try:
        user_id = message.chat.id
        amount = float(message.text)
        if amount < Mini_Withdraw:
            bot.send_message(message.chat.id, f"Minimum withdrawal is {Mini_Withdraw} {TOKEN}.", parse_mode="Markdown")
        else:
            data = json.load(open('users.json', 'r')
            balance = data.get('balance', {}).get(str(user_id), 0)
            wallet = data.get('wallet', {}).get(str(user_id), "none")
            if wallet == "none":
                bot.send_message(message.chat.id, "_❌ Wallet not set._", parse_mode="Markdown")
                return
            if balance >= amount:
                data['balance'].update({str(user_id): balance - amount})
                data['withd'].update({str(user_id): data.get(str(user_id), 0) + amount})
                json.dump(data, open('users.json', 'w'))
                bot.send_message(message.chat.id, f"*Withdrawal of {amount} {TOKEN} requested.*", parse_mode="Markdown")
                bot.send_message(OWNER_ID, f"*Withdrawal of {amount} {TOKEN} requested by {message.from_user.first_name}.*")
            else:
                bot.send_message(message.chat.id, f"_❌ Insufficient balance to withdraw {amount} {TOKEN}. Your balance is {balance} {TOKEN}._", parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid amount.", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred.", parse_mode="Markdown")
        bot.send_message(OWNER_ID, "Your bot got an error fix it fast!
Error on command: withdraw_confirm
Error details: "+str(e))

# Handle callback data
def callback_handler(callback):
    user_id = callback.from_user.id
    callback_data = callback.data
    if callback_data == 'withdraw':
        withdraw(callback.message)
    elif callback_data == 'payment_receipt':
        payment_receipt(callback.message)

# Add callback data handling
bot.callback_query_handler(callback_handler)

# Start the bot
if __name__ == '__main__':
    bot.polling(none_stop=True)
```
