import os
import django
import asyncio
import websockets
import json
import random
from datetime import datetime, timedelta

# 1️⃣ Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrisense.settings")
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

# 2️⃣ Get the user and generate a token
User = get_user_model()
user = User.objects.get(username="musafarm")

refresh = RefreshToken.for_user(user)
access_token = refresh.access_token
access_token.set_exp(from_time=datetime.now(), lifetime=timedelta(days=365*100))
TOKEN = str(access_token)

URL = f"ws://192.168.254.200:8000/ws/soil/?token={TOKEN}"

# 3️⃣ Async function to send soil data every minute
async def send_soil_data():
    while True:
        try:
            async with websockets.connect(URL) as websocket:
                print("✅ Connected to server!")

                while True:
                    data = {
                        "type": "soil_update",
                        "data": {
                            "temperature": round(random.uniform(20, 35), 2),
                            "ph": round(random.uniform(5.5, 7.5), 2),
                            "nitrogen": round(random.uniform(10, 50), 2),
                            "phosphorus": round(random.uniform(5, 25), 2),
                            "potassium": round(random.uniform(80, 250), 2),
                        },
                    }

                    await websocket.send(json.dumps(data))
                    print(f"Sent: {data}")

                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                        print("Received:", response)
                    except asyncio.TimeoutError:
                        pass

                    # ⬅ Send every 60 seconds
                    await asyncio.sleep(60)

        except Exception as e:
            print("❌ Connection failed, retrying in 30s...", e)
            await asyncio.sleep(30)

asyncio.run(send_soil_data())