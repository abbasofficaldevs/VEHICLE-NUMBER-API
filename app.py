from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

API_URL = "https://abhaykumar.xo.je/api/proxy.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
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

        # IMPORTANT: handle empty response
        if not r.text or r.text.strip() == "":
            return jsonify({
                "status": "error",
                "message": "Empty response from API"
            })

        try:
            data = r.json()
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON from API",
                "raw": r.text[:200]
            })

        result = data.get("data", {})

        if result.get("ℹ️ Status") == "No information found":
            return jsonify({
                "status": "failed",
                "message": "Data not found",
                "records": []
            })

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
            "message": f"Request failed: {str(e)}"
        })

if __name__ == "__main__":
    app.run(debug=True)
