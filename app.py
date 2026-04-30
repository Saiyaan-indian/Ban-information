from flask import Flask, request, Response
import requests
import json
import math

app = Flask(__name__)


def get_player_info(player_id):
    cookies = {
        '_ga': 'GA1.1.2123120599.1674510784',
        '_fbp': 'fb.1.1674510785537.363500115',
        '_ga_7JZFJ14B0B': 'GS1.1.1674510784.1.1.1674510789.0.0.0',
        'source': 'mb',
        'region': 'MA',
        'language': 'ar',
        '_ga_TVZ1LG7BEB': 'GS1.1.1674930050.3.1.1674930171.0.0.0',
        'datadome': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
        'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',
    }

    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://shop2game.com',
        'Referer': 'https://shop2game.com/app/100067/idlogin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        'accept': 'application/json',
        'content-type': 'application/json',
        'x-datadome-clientid': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
    }

    json_data = {
        'app_id': 100067,
        'login_id': f'{player_id}',
        'app_server_id': 0,
    }

    try:
        res = requests.post('https://shop2game.com/api/auth/player_id_login', cookies=cookies, headers=headers, json=json_data)
        if res.status_code == 200:
            data = res.json()
            return {
                "nickname": data.get("nickname", "?"),
                "region": data.get("region", "?")
            }
    except:
        pass

    return {
        "nickname": "?",
        "region": "?"
    }


def format_duration(days):
    """Convert days into a readable string with days, months (30 days), years (365 days)."""
    if days <= 0:
        return "0 Days"

    years = days // 365
    remaining_days = days % 365
    months = remaining_days // 30
    days_remain = remaining_days % 30

    parts = []
    if years > 0:
        parts.append(f"{years} {'Year' if years == 1 else 'Years'}")
    if months > 0:
        parts.append(f"{months} {'Month' if months == 1 else 'Months'}")
    if days_remain > 0:
        parts.append(f"{days_remain} {'Day' if days_remain == 1 else 'Days'}")

    return " ".join(parts) if parts else "0 Days"


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
            period_days = data.get("period", 0)   # API returns period in days

            # Format duration only if banned and period > 0
            duration_str = "NOT FOUND"
            if is_banned and period_days > 0:
                duration_str = format_duration(period_days)

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
