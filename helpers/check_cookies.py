import sqlite3
import os

cookie_file = os.path.join("bot_profile", "Default", "Network", "Cookies")
if not os.path.exists(cookie_file):
    print("Cookie file not found in bot_profile")
else:
    try:
        conn = sqlite3.connect(cookie_file)
        c = conn.cursor()
        c.execute("SELECT host_key, name FROM cookies WHERE host_key LIKE '%linkedin%' LIMIT 5")
        rows = c.fetchall()
        print(f"Found {len(rows)} LinkedIn cookies in bot_profile:")
        for r in rows:
            print(r)
        conn.close()
    except Exception as e:
        print("Error reading cookies:", e)

cookie_file2 = os.path.expanduser("~/.config/chromium/Default/Network/Cookies")
if not os.path.exists(cookie_file2):
    print("Cookie file not found in ~/.config/chromium")
else:
    try:
        conn = sqlite3.connect(cookie_file2)
        c = conn.cursor()
        c.execute("SELECT host_key, name FROM cookies WHERE host_key LIKE '%linkedin%' LIMIT 5")
        rows = c.fetchall()
        print(f"Found {len(rows)} LinkedIn cookies in ~/.config/chromium:")
        for r in rows:
            print(r)
        conn.close()
    except Exception as e:
        print("Error reading cookies:", e)
