FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Dono bots ko ek sath background mein chalane ke liye:
CMD ["sh", "-c", "python admin_bot.py & python bot.py"]
