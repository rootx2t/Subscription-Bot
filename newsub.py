import datetime
import time
import logging
from telegram import Bot
from telegram.ext import CommandHandler, Updater

# ========= CONFIG =========
TOKEN = "8246711932:AAGN1raJxfSH8Qf2_Rx4ECyJmrgMIfXYifA"   # <-- তোমার টোকেন বসাও
ADMIN_ID = 6999604701
CHANNEL_ID = -1003075312230
INVITE_LINK = "https://t.me/+9e5QtDXXc9U4NDM1"
# ==========================

# Logging setup (console-এ output দেখাবে)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = Bot(token=TOKEN)
subscribers = {}  # memory-based user data

# ---------- Commands ----------
def start(update, context):
    update.message.reply_text("👋 Welcome! Please contact admin to start your subscription.")

def add_user(update, context):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    if len(context.args) < 2:
        update.message.reply_text("⚠️ Usage: /add_user <user_id> <days>")
        return

    try:
        user_id = int(context.args[0])
        days = int(context.args[1])
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
        subscribers[user_id] = expiry_date

        bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ Access granted for {days} days.\n"
                f"Expires on: {expiry_date.date()}\n\n"
                f"Join the channel:\n{INVITE_LINK}"
            )
        )

        update.message.reply_text(
            f"✅ User {user_id} added for {days} days (till {expiry_date.date()})."
        )
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}")

# ---------- NEW COMMAND: List Users ----------
def list_users(update, context):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    if not subscribers:
        update.message.reply_text("ℹ️ No active VIP users.")
        return

    message = "📋 *VIP Subscribers List:*\n\n"
    for user_id, expiry in subscribers.items():
        message += f"👤 `{user_id}` — Expires: *{expiry.strftime('%Y-%m-%d %H:%M')}*\n"

    update.message.reply_text(message, parse_mode="Markdown")

# ---------- Subscription check ----------
def check_subscriptions():
    now = datetime.datetime.now()
    for user_id, expiry in list(subscribers.items()):
        if now > expiry:
            try:
                bot.ban_chat_member(CHANNEL_ID, user_id)
                del subscribers[user_id]
                logging.info(f"Removed expired user {user_id}")
            except Exception as e:
                logging.error(f"Error removing {user_id}: {e}")

# ---------- Main run ----------
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add_user", add_user))
    dp.add_handler(CommandHandler("list_users", list_users))  # ✅ Added command

    logging.info("✅ Bot started successfully!")

    updater.start_polling()

    # প্রতি 1 ঘণ্টা পর পর subscription check করবে
    while True:
        check_subscriptions()
        time.sleep(3600)

if __name__ == "__main__":
    main()
