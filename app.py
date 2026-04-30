from flask import Flask, request, Response
import requests
import json
import os

app = Flask(__name__)

# ... keep get_player_info() unchanged ...

def format_duration(seconds):
    """Convert ban period in seconds to a human-readable string."""
    if seconds <= 0:
        return "PERMANENT"
    
    # Convert to whole days (ignoring sub-day precision for ban durations)
    total_days = seconds // 86400
    if total_days < 1:
        return "Less than a day"
    
    years = total_days // 365
    remaining_days = total_days % 365
    months = remaining_days // 30
    days = remaining_days % 30
    
    parts = []
    if years > 0:
        parts.append(f"{years} year" + ("s" if years > 1 else ""))
    if months > 0:
        parts.append(f"{months} month" + ("s" if months > 1 else ""))
    if days > 0 or (years == 0 and months == 0):  # show days if it's the only unit
        parts.append(f"{days} day" + ("s" if days != 1 else ""))
    
    return ", ".join(parts)

def check_banned(player_id):
    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K)",
        "Accept": "application/json",
        "referer": "https://ff.garena.com/en/support/",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }

    try:
        response = requests.get(url, headers=headers)
        player_info = get_player_info(player_id)

        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)   # seconds

            if is_banned:
                duration_str = format_duration(period)
            else:
                duration_str = "NOT FOUND"

            result = {
                "Nickname": player_info["nickname"],
                "Region": player_info["region"],
                "UID": player_id,
                "Account": "BANNED🚫" if is_banned else "NOT BANNED",
                "Duration": duration_str,
                "Banned": "TRUE" if is_banned else "FALSE",
            }

            return Response(json.dumps(result, indent=4, ensure_ascii=False), mimetype="application/json")

        else:
            return Response(json.dumps({
                "❌ error": "Failed to fetch ban status from Garena server",
                "status_code": 500
            }, indent=4), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({
            "💥 exception": str(e),
            "status_code": 500
        }, indent=4), mimetype="application/json")

@app.route("/check", methods=["GET"])
def check():
    player_id = request.args.get("uid", "")

    if not player_id:
        return Response(json.dumps({
            "⚠️ error": "Player ID (uid) is required !",
            "status_code": 400
        }, indent=4), mimetype="application/json")

    return check_banned(player_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True)
