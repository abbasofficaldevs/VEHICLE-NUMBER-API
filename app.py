from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

API_URL = "https://abhaykumar.xo.je/api/proxy.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://abhaykumar.xo.je/home.php",
    "Connection": "keep-alive"
}

@app.route("/lookup", methods=["GET"])
def lookup():
    number = request.args.get("num")

    if not number:
        return jsonify({"status": "failed", "message": "num parameter required"})

    try:
        r = requests.get(
            API_URL,
            params={"tool": "number_info", "query": number},
            headers=HEADERS,
            timeout=30
        )

        # STEP 1: check empty response
        if not r.text or r.text.strip() == "":
            return jsonify({
                "status": "error",
                "message": "Empty response from API"
            })

        # STEP 2: safe JSON parse
        try:
            data = r.json()
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON response",
                "raw": r.text[:200]
            })

        result = data.get("data", {})

        # STEP 3: not found handling
        if result.get("ℹ️ Status") == "No information found":
            return jsonify({
                "status": "failed",
                "message": "Data not found",
                "records": []
            })

        # STEP 4: old format response
        cleaned = [{
            "mobile": result.get("📱 Mobile Number"),
            "name": result.get("👤 Name"),
            "father_name": result.get("👨 Father Name"),
            "address": result.get("📍 Address"),
            "alternate": result.get("📞 Alternate Number"),
            "circle": result.get("📡 Circle"),
            "id": result.get("🪪 Aadhaar"),
            "email": None
        }]

        return jsonify({
            "status": "success",
            "total_records": len(cleaned),
            "records": cleaned
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)
