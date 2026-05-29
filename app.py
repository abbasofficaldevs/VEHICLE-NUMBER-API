from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

API_URL = "https://abhaykumar.xo.je/api/proxy.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Connection": "keep-alive"
}

@app.route("/lookup", methods=["GET"])
def lookup():
    number = request.args.get("num")

    if not number:
        return jsonify({
            "status": "failed",
            "message": "num parameter required"
        })

    try:
        session = requests.Session()

        response = session.get(
            API_URL,
            params={
                "tool": "number_info",
                "query": number
            },
            headers=HEADERS,
            timeout=30
        )

        data = response.json()
        result = data.get("data", {})

        # Convert emoji keys to normal keys
        fixed = {
            "Name": result.get("👤 Name"),
            "Father Name": result.get("👨 Father Name"),
            "Mobile Number": result.get("📱 Mobile Number"),
            "Aadhaar": result.get("🪪 Aadhaar"),
            "Address": result.get("📍 Address"),
            "Alternate Number": result.get("📞 Alternate Number"),
            "Circle": result.get("📡 Circle"),
            "Status": result.get("ℹ️ Status")
        }

        # Not found
        if fixed.get("Status") == "No information found":
            return jsonify({
                "status": "failed",
                "message": "Data not found",
                "records": [],
                "note": [
                    "Credit SkillsQuark Team",
                    "Only for educational testing purpose",
                    "We do not promote any illegal activities"
                ]
            })

        # Old response format
        cleaned = [{
            "mobile": fixed.get("Mobile Number"),
            "name": fixed.get("Name"),
            "father_name": fixed.get("Father Name"),
            "address": fixed.get("Address"),
            "alternate": fixed.get("Alternate Number"),
            "circle": fixed.get("Circle"),
            "id": fixed.get("Aadhaar"),
            "email": None
        }]

        return jsonify({
            "status": "success",
            "total_records": len(cleaned),
            "records": cleaned,
            "note": [
                "Credit SkillsQuark Team",
                "Only for educational testing purpose",
                "We do not promote any illegal activities"
            ]
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Request failed: {str(e)}"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
