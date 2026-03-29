from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from fastapi.responses import FileResponse
from pathlib import Path
import sqlite3
from datetime import datetime



app = FastAPI()

# ✅ ADD YOUR API KEY HERE
API_KEY = "99ee6a418e32eeb3f4211a21c607920c65e6e151"

# ✅ CORS (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 🔥 DATABASE SETUP
conn = sqlite3.connect("aqi.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS aqi_data (
    city TEXT,
    aqi INTEGER,
    time TEXT
)
""")
conn.commit()

# serve frontend
@app.get("/")
def home():
   file_path = Path(__file__).parent / "index.html"
   return FileResponse(file_path)

    
   
# get aqi + store
@app.get("/aqi/{city}")
def get_aqi(city: str):
    url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"
    
    response = requests.get(url).json()

    if response["status"] != "ok":
        return {"error": "City not found"}

    aqi = response["data"]["aqi"]
    time_now = datetime.now().strftime("%H:%M:%S")

 # 🔥 SAVE TO DATABASE
    cursor.execute(
        "INSERT INTO aqi_data (city, aqi, time) VALUES (?, ?, ?)",
        (city.lower(), aqi, time_now)
    )
    conn.commit()

    return {"city": city, "aqi": aqi}

# 📊 GET HISTORY
@app.get("/history/{city}")
def get_history(city: str):
    cursor.execute(
        "SELECT time, aqi FROM aqi_data WHERE city=? ORDER BY rowid DESC LIMIT 10",
        (city.lower(),)
    )
    data = cursor.fetchall()

    data.reverse()

    return {
        "labels": [row[0] for row in data],
        "values": [row[1] for row in data]
    }
    