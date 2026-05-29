import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

API_URL = "https://abhaykumar.xo.je/api/proxy.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://abhaykumar.xo.je/home.php",
    "Connection": "keep-alive"
}

# IMPORTANT: keep session + cookie
session = requests.Session()
session.headers.update(HEADERS)

session.cookies.update({
    "PHPSESSID": "741cc4419e1decac185fd66caa78f1a2",
    "__test": "91b3585db080312acaa505b0768cf85c"
})

@app.route("/lookup", methods=["GET"])
def lookup():
    number = request.args.get("num")

    if not number:
        return jsonify({"status": "failed", "message": "num required"})

    try:
        r = session.get(
            API_URL,
            params={"tool": "number_info", "query": number},
            timeout=30
        )

        text = r.text

        # block HTML challenge
        if "<html" in text.lower() or "aes.js" in text:
            return jsonify({
                "status": "error",
                "message": "Blocked by anti-bot page (HTML response received)"
            })

        data = r.json()
        result = data.get("data", {})

        if result.get("ℹ️ Status") == "No information found":
            return jsonify({
                "status": "failed",
                "message": "Data not found",
                "records": []
            })

        return jsonify({
            "status": "success",
            "records": [{
                "mobile": result.get("📱 Mobile Number"),
                "name": result.get("👤 Name"),
                "father_name": result.get("👨 Father Name"),
                "address": result.get("📍 Address"),
                "alternate": result.get("📞 Alternate Number"),
                "circle": result.get("📡 Circle"),
                "id": result.get("🪪 Aadhaar"),
                "email": None
            }]
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
