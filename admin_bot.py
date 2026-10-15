import json
import time
import urllib.request

# ⚙ CONFIGURATION TOKENS:
TOKEN = "8654656004:AAEheblIhDerRHM9PLmxmX3jzi7bRiKoljQ"  # Admin Bot Token
USER_BOT_TOKEN = "8921302097:AAE2cNRLcsDxNePTEoaPlzK6VyNtC7oEukw"  # User Bot Token (User ko message bhejne ke liye)
PROJECT_ID = "earncashapp-83f24"

# To track interactive steps for promo code creation & withdrawal redeem code input
user_states = {}


def send_telegram_message(chat_id, text, reply_markup=None):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
  if reply_markup:
    payload["reply_markup"] = reply_markup

  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}
  )
  try:
    with urllib.request.urlopen(req) as response:
      return json.loads(response.read().decode())
  except Exception as e:
    print("Telegram Error:", e)


# Naya function jo seedha User Bot ke token se user ko message bhejega
def send_message_to_user(user_chat_id, text):
  url = f"https://api.telegram.org/bot{USER_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": user_chat_id, "text": text, "parse_mode": "Markdown"}
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}
  )
  try:
    with urllib.request.urlopen(req) as response:
      return json.loads(response.read().decode())
  except Exception as e:
    print("User Bot Send Error:", e)


def edit_telegram_message(chat_id, message_id, text):
  url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
  payload = {
      "chat_id": chat_id,
      "message_id": message_id,
      "text": text,
      "parse_mode": "Markdown",
  }
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}
  )
  try:
    with urllib.request.urlopen(req) as response:
      return json.loads(response.read().decode())
  except Exception as e:
    print("Telegram Edit Error:", e)


def get_withdrawals():
  url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/withdrawals"
  try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode())
      return data.get("documents", [])
  except Exception as e:
    print("Firebase Error:", e)
    return []


def get_withdrawal_details(req_id):
  url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/withdrawals/{req_id}"
  try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode())
      fields = data.get("fields", {})
      return {
          "user_id": fields.get("userId", {}).get(
              "stringValue", fields.get("userId", {}).get("integerValue", "")
          ),
          "amount": fields.get("amount", {}).get(
              "stringValue", fields.get("amount", {}).get("integerValue", "")
          ),
      }
  except Exception as e:
    print("Firebase Get Withdrawal Error:", e)
    return None


def update_withdrawal_status_with_code(req_id, new_status, redeem_code):
  url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/withdrawals/{req_id}?updateMask.fieldPaths=status&updateMask.fieldPaths=redeemCode"
  payload = {
      "fields": {
          "status": {"stringValue": new_status},
          "redeemCode": {"stringValue": redeem_code},
      }
  }
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}, method="PATCH"
  )
  try:
    with urllib.request.urlopen(req) as response:
      return True
  except Exception as e:
    print("Firebase Update Error:", e)
    return False


def update_withdrawal_status(req_id, new_status):
  url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/withdrawals/{req_id}?updateMask.fieldPaths=status"
  payload = {
      "fields": {"status": {"stringValue": new_status}}
  }
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}, method="PATCH"
  )
  try:
    with urllib.request.urlopen(req) as response:
      return True
  except Exception as e:
    print("Firebase Update Error:", e)
    return False


# Firebase Helpers for Promo Codes
def set_firebase_promo_code(code, coins):
  url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/promocodes/active_code"

  now = time.localtime()
  midnight_struct = time.struct_time((
      now.tm_year,
      now.tm_mon,
      now.tm_mday,
      23,
      59,
      59,
      now.tm_wday,
      now.tm_yday,
      now.tm_isdst,
  ))
  midnight_ms = int(time.mktime(midnight_struct) * 1000)

  payload = {
      "fields": {
          "code": {"stringValue": code},
          "coins": {"integerValue": str(coins)},
          "expiresAt": {"integerValue": str(midnight_ms)},
          "createdAt": {"integerValue": str(int(time.time() * 1000))},
      }
  }
  data = json.dumps(payload).encode("utf-8")
  req = urllib.request.Request(
      url, data=data, headers={"Content-Type": "application/json"}, method="PATCH"
  )
  try:
    with urllib.request.urlopen(req) as response:
      return True
  except Exception as e:
    print("Firebase Promo Set Error:", e)
    return False


def get_firebase_active_promo():
  url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/promocodes/active_code"
  try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode())
      fields = data.get("fields", {})
      return {
          "code": fields.get("code", {}).get("stringValue", ""),
          "coins": fields.get("coins", {}).get("integerValue", "0"),
      }
  except Exception as e:
    return None


def get_promo_claims_count(code):
  url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/promo_claims"
  try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode())
      documents = data.get("documents", [])
      count = 0
      for doc in documents:
        fields = doc.get("fields", {})
        doc_code = fields.get("code", {}).get("stringValue", "")
        if doc_code == code:
          count += 1
      return count
  except Exception as e:
    print("Firebase Claims Error:", e)
    return 0


def delete_firebase_promo():
  url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/promocodes/active_code"
  req = urllib.request.Request(url, method="DELETE")
  try:
    with urllib.request.urlopen(req) as response:
      return True
  except Exception as e:
    print("Firebase Delete Error:", e)
    return False


print(
    "Admin Bot redeem code aur promo code support ke sath chalu ho gaya hai!"
)

offset = 0
while True:
  try:
    url = (
        f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
    )
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
      result = json.loads(response.read().decode())
      updates = result.get("result", [])

      for update in updates:
        offset = update["update_id"] + 1

        # Handle button clicks (Callback Queries)
        if "callback_query" in update:
          cq = update["callback_query"]
          data = cq["data"]
          chat_id = cq["message"]["chat"]["id"]
          message_id = cq["message"]["message_id"]

          if data.startswith("pay_"):
            req_id = data.split("_")[1]
            user_states[chat_id] = {
                "step": "waiting_for_redeem_code",
                "req_id": req_id,
                "msg_id": message_id,
            }
            send_telegram_message(
                chat_id,
                f"💳 Withdrawal ID `{req_id}` ke liye ab **Redeem Code** type karke bhejo:",
            )

          elif data.startswith("reject_"):
            req_id = data.split("_")[1]
            if update_withdrawal_status(req_id, "Rejected"):
              edit_telegram_message(
                  chat_id,
                  message_id,
                  f"❌ Withdrawal ID `{req_id}` ko **Reject** kar diya gaya"
                  " hai!",
              )
            else:
              edit_telegram_message(
                  chat_id,
                  message_id,
                  f"❌ Withdrawal ID `{req_id}` update karne mein error aaya!",
              )

        # Handle text messages & commands
        elif "message" in update:
          msg = update["message"]
          chat_id = msg["chat"]["id"]
          text = msg.get("text", "").strip()

          # Check if admin is in middle of any interactive state
          if chat_id in user_states:
            state = user_states[chat_id]

            if state["step"] == "waiting_for_code":
              user_states[chat_id]["code"] = text.upper()
              user_states[chat_id]["step"] = "waiting_for_coins"
              send_telegram_message(
                  chat_id,
                  f"✅ Code: *{text.upper()}*\n\n🪙 Ab is promo code ke liye"
                  " **Coins** ki value bhejo (jaise: `25`):",
              )
              continue

            elif state["step"] == "waiting_for_coins":
              try:
                coins_val = int(text)
                promo_code = user_states[chat_id]["code"]

                if set_firebase_promo_code(promo_code, coins_val):
                  send_telegram_message(
                      chat_id,
                      "🎉 *Promo Code Successfully Set!*\n\n🎟️ Code:"
                      f" `{promo_code}`\n🪙 Coins: `{coins_val}`\n⏳ Valid Till:"
                      " *Aaj Raat 12:00 AM (Midnight)*",
                  )
                else:
                  send_telegram_message(
                      chat_id, "❌ Database mein save karne mein error aaya!"
                  )
              except ValueError:
                send_telegram_message(
                    chat_id,
                    "❌ Invalid number! Kripya sirf numbers bhejo (jaise 25)."
                    " Command dobara shuru karne ke liye /setpromocode bhejo.",
                )

              del user_states[chat_id]
              continue

            elif state["step"] == "waiting_for_redeem_code":
              req_id = state["req_id"]
              msg_id = state["msg_id"]
              redeem_code = text

              # Withdrawal details fetch karo taaki user_id pata chale
              w_details = get_withdrawal_details(req_id)

              if update_withdrawal_status_with_code(
                  req_id, "Success", redeem_code
              ):
                edit_telegram_message(
                    chat_id,
                    msg_id,
                    f"✅ Withdrawal ID `{req_id}` successfully paid ho gayi"
                    f" hai!\n🎁 Redeem Code: `{redeem_code}`",
                )

                # Yahan ab User Bot Token ke zariye seedha user ke paas message jayega
                if w_details and w_details["user_id"]:
                  user_chat_id = w_details["user_id"]
                  amount = w_details["amount"]
                  user_msg = (
                      "🎉 *Congratulations!* Your withdrawal request of"
                      f" **₹{amount}** has been successfully approved!\n\n🎁"
                      f" **Your Redeem Code:** `{redeem_code}`\n\n_Copy this"
                      " code and redeem it successfully._"
                  )
                  send_message_to_user(user_chat_id, user_msg)
              else:
                send_telegram_message(
                    chat_id, "❌ Firebase update karne mein error aaya!"
                )

              del user_states[chat_id]
              continue

          # Commands Handling
          if text == "/start":
            send_telegram_message(
                chat_id,
                "👋 *Welcome to Earn Karo Admin Bot!*\n\nCommands"
                " available:\n👉 /withdrawals - Check pending withdrawals\n👉"
                " /setpromocode - Test/Set promo code\n👉"
                " /todayspromocodeclaimed - Check claims count\n👉"
                " /deletepromocode - Delete active promo code",
            )

          elif text == "/setpromocode":
            user_states[chat_id] = {"step": "waiting_for_code"}
            send_telegram_message(
                chat_id,
                "🎟️ Apne naye promo code ka naam bhejo (jaise: `NEW25`):",
            )

          elif text == "/todayspromocodeclaimed":
            promo_info = get_firebase_active_promo()
            if not promo_info or not promo_info["code"]:
              send_telegram_message(
                  chat_id, "❌ Koi bhi active promo code set nahi hai!"
              )
            else:
              code = promo_info["code"]
              claims_count = get_promo_claims_count(code)
              send_telegram_message(
                  chat_id,
                  "📊 *Promo Code Stats*\n\n🎟️ Active Code:"
                  f" `{code}`\n👥 Total Users Claimed: *{claims_count} Users*",
              )

          elif text == "/deletepromocode":
            if delete_firebase_promo():
              send_telegram_message(
                  chat_id,
                  "🗑️ Active promo code ko successfully delete/expire kar"
                  " diya gaya hai!",
              )
            else:
              send_telegram_message(
                  chat_id, "❌ Promo code delete karne mein error aaya."
              )

          elif text == "/withdrawals":
            documents = get_withdrawals()
            count = 0

            for doc in documents:
              fields = doc.get("fields", {})
              status_val = (
                  fields.get("status", {}).get("stringValue", "")
              )
              if status_val != "Pending":
                continue

              count += 1
              full_name = doc.get("name", "")
              req_id = full_name.split("/")[-1]

              name = fields.get("name", {}).get("stringValue", "N/A")
              amount = fields.get("amount", {}).get(
                  "stringValue",
                  fields.get("amount", {}).get("integerValue", "N/A"),
              )
              detail = fields.get("detail", {}).get("stringValue", "N/A")
              date = fields.get("date", {}).get("stringValue", "N/A")
              type_val = fields.get("type", {}).get("stringValue", "N/A")

              msg_text = (
                  f"🆔 *ID:* `{req_id}`\n👤 *Name:* {name}\n💰 *Amount:* ₹{amount}"
                  f" ({type_val})\n📱 *Detail:* `{detail}`\n📅 *Date:* {date}"
              )

              markup = {
                  "inline_keyboard": [[
                      {"text": "Mark Paid✅ ", "callback_data": f"pay_{req_id}"},
                      {"text": "❌ Reject Karo", "callback_data": f"reject_{req_id}"},
                  ]]
              }
              send_telegram_message(chat_id, msg_text, reply_markup=markup)

            if count == 0:
              send_telegram_message(
                  chat_id, "✅ Koi bhi pending withdrawal request nahi hai!"
              )
  except Exception as e:
    print("Polling Error:", e)
