from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_player_info(player_id):

    url = "https://shop.garena.sg/api/auth/player_id_login"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-MM,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://shop.garena.sg",
        "Referer": "https://shop.garena.sg/?app=100067",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Android WebView";v="138"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; RMX5070 Build/UKQ1.231108.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.157 Mobile Safari/537.36",
        "X-Requested-With": "mark.via.gp",
        "Cookie": "source=mb; region=SG; language=en; mspid2-2f6c6989c48ddf7bb10ed6524587b4ac; _fbp=fb.1.1777149093959.8996558758423537; _ga-GA1.1.1121598805.1777149095; datadome=cr6eYz_0Ekonc8FNbWJOA81W~JRJ16dYiRflc4s0KvPkLyRwxcWsbc16kex7K2BP9_z8BjkR3NmzBIAv0jL8mekQITkigqbDGFU9UxtE1jPvwaW3GAX4GDrGe9m80DxL; _ga_PMR65LMTYY=GS2.1.s1777149094$o1$g1$t1777149435$j58$10$h0",
    }

    payload = {
        "app_id": 100067,
        "login_id": f"{player_id}",
        "app_server_id": 0,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            # The API returns lowercase keys "nickname" and "region"
            return {
                "nickname": data.get("nickname", "?"),
                "region": data.get("region", "?")
            }
    except Exception:
        # Any network or parsing error → fallback
        pass

    return {"nickname": "?", "region": "?"}


def check_banned(player_id):
    """
    Combine player info with ban status from the Garena anti-hack API.
    """
    # Fixed: player_info now always uses lowercase keys
    player_info = get_player_info(player_id)

    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K)",
        "Accept": "application/json",
        "referer": "https://ff.garena.com/en/support/",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }

    try:
        ban_response = requests.get(url, headers=headers, timeout=20)

        if ban_response.status_code == 200:
            data = ban_response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)

            result = {
                "Nickname": player_info["nickname"],       # lowercase key access now works
                "Region": player_info["region"],
                "UID": player_id,
                "Account": "BANNED🚫" if is_banned else "NOT BANNED",
                "Duration": f"{period} {'DAY' if period == 1 else 'DAYS'}" if is_banned else "NOT FOUND",
                "Banned": "TRUE" if is_banned else "FALSE",
            }
            return jsonify(result)

        else:
            return jsonify({
                "❌ error": "Failed to fetch ban status from Garena server",
                "status_code": 500
            }), 500

    except Exception as e:
        return jsonify({
            "💥 exception": str(e),
            "status_code": 500
        }), 500


@app.route("/check", methods=["GET"])
def check():
    player_id = request.args.get("uid", "")

    if not player_id:
        return jsonify({
            "⚠️ error": "Player ID (uid) is required !",
            "status_code": 400
        }), 400

    return check_banned(player_id)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True)
