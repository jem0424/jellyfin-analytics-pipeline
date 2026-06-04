import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Config
JELLYFIN_URL = os.getenv("JELLYFIN_URL")
API_KEY = os.getenv("API_KEY")
DB_CONN = os.getenv("DB_CONN")

headers = {"X-Emby-Token": API_KEY}

# Connect to PostgreSQL
conn = psycopg2.connect(DB_CONN)
cur = conn.cursor()

# Create tables if they don't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_plays (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR,
        username VARCHAR,
        item_id VARCHAR,
        item_name VARCHAR,
        item_type VARCHAR,
        artist VARCHAR,
        album VARCHAR,
        played_at TIMESTAMP,
        play_duration BIGINT,
        extracted_at TIMESTAMP DEFAULT NOW()
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_items (
        id SERIAL PRIMARY KEY,
        item_id VARCHAR UNIQUE,
        item_name VARCHAR,
        item_type VARCHAR,
        artist VARCHAR,
        album VARCHAR,
        genre VARCHAR,
        year INTEGER,
        extracted_at TIMESTAMP DEFAULT NOW()
    );
""")

conn.commit()

# Extract users
users_resp = requests.get(f"{JELLYFIN_URL}/Users", headers=headers)
users = users_resp.json()

# Extract play history per user
for user in users:
    user_id = user["Id"]
    username = user["Name"]

    history_resp = requests.get(
        f"{JELLYFIN_URL}/Users/{user_id}/Items",
        headers=headers,
        params={
            "Filters": "IsPlayed",
            "IncludeItemTypes": "Audio",
            "Fields": "UserData,Artists,Album,Genres,ProductionYear",
            "Recursive": True,
            "Limit": 1000
        }
    )

    if history_resp.status_code != 200:
        continue

    items = history_resp.json().get("Items", [])

    for item in items:
        user_data = item.get("UserData", {})
        last_played = user_data.get("LastPlayedDate")
        play_count = user_data.get("PlayCount", 0)
        artists = item.get("Artists", [])
        artist = item.get("AlbumArtist") or (artists[0] if artists else None)
        if last_played:
            cur.execute("""
                INSERT INTO raw_plays 
                (user_id, username, item_id, item_name, item_type, artist, album, played_at, play_duration)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                user_id,
                username,
                item["Id"],
                item.get("Name"),
                item.get("Type"),
                artist,
                item.get("Album"),
                last_played,
                item.get("RunTimeTicks", 0) // 10000000
            ))

        # Insert into items table
        genre_list = item.get("Genres", [])
        cur.execute("""
            INSERT INTO raw_items
            (item_id, item_name, item_type, artist, album, genre, year)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (item_id) DO NOTHING
        """, (
            item["Id"],
            item.get("Name"),
            item.get("Type"),
            artist,
            item.get("Album"),
            genre_list[0] if genre_list else None,
            item.get("ProductionYear")
        ))

conn.commit()
cur.close()
conn.close()
print(f"Extraction complete at {datetime.now()}")
