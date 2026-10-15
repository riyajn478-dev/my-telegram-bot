import json
import logging
import urllib.request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ⚙ CONFIGURATION:
BOT_TOKEN = "8921302097:AAE2cNRLcsDxNePTEoaPlzK6VyNtC7oEukw"
CHANNEL_USERNAME = "@EARN_KARO_TELEGRAM"
CHANNEL_URL = "https://t.me/earn_karo_telegram"

# Aapki Admin Telegram Chat ID (Yahan apni numeric ID daal dena)
ADMIN_CHAT_ID = "8832555712"

WEB_APP_URL = "https://riyajn478-dev.github.io/earn-karo-telegram/" 
SUPPORT_URL = "https://t.me/Earn_Karo_Support"
TUTORIAL_VIDEO_LINK = "https://t.me/earn_karo_telegram/12"


# 1. /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("✅ Yes, I Have Joined", callback_data="check_joined")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"👋 Hello *{user.first_name}*!\n\n"
        f"To use the bot, you must join our official channel first:\n"
        f"👉 {CHANNEL_USERNAME}\n\n"
        f"After joining the channel, click the **'Yes, I Have Joined'** button below!"
    )

    await update.message.reply_text(
        welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
    )


# 2. Button clicks handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_joined":
        user_id = query.from_user.id
        bot = context.bot

        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in ["left", "kicked"]:
                await query.answer(
                    "❌ You have not joined the channel yet! Please join first.",
                    show_alert=True,
                )
                return
        except Exception as e:
            print("Channel check notice:", e)

        keyboard = [
            [InlineKeyboardButton("🎥 How to use Earn karo", url=TUTORIAL_VIDEO_LINK)],
            [InlineKeyboardButton("🚀 Earn Karo", web_app={"url": WEB_APP_URL})],
            [InlineKeyboardButton("🛠 Support", url=SUPPORT_URL)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        success_text = "👇 Choose an option from the menu below:"

        await query.edit_message_text(
            text=success_text, reply_markup=reply_markup, parse_mode="Markdown"
        )


# 🔔 Admin Alert Function (Without any extra pip packages)
async def send_withdrawal_alert_to_admin(bot, user_id, username, amount, upi_id, withdrawal_id):
    keyboard = [
        [
            InlineKeyboardButton("💳 Mark Paid", callback_data=f"mark_paid_{withdrawal_id}_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{withdrawal_id}_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    alert_text = (
        f"🔔 **New Withdrawal Request!**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"🔗 **Username:** @{username}\n"
        f"💰 **Amount:** ₹{amount}\n"
        f"💳 **UPI ID / Details:** `{upi_id}`\n"
        f"🆔 **Withdrawal ID:** `{withdrawal_id}`"
    )

    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=alert_text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        print("Failed to send admin alert:", e)


def main():
    # Note: python-telegram-bot package to chahiye hi hoga bot chalane ke liye, 
    # lekin firebase-admin ki zaroorat khatam kar di hai!
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Earn Karo User Bot is running successfully (No extra DB packages needed)...")
    application.run_polling()


if __name__ == "__main__":
    main()
