from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

API_URL = "https://num-to-info.sauravsingh2111.workers.dev/lookup/"

@app.route("/lookup", methods=["GET"])
def lookup():
    number = request.args.get("num")

    if not number:
        return jsonify({
            "status": "failed",
            "message": "num parameter required"
        })

    try:
        response = requests.get(f"{API_URL}{number}", timeout=20)
        data = response.json()

        results = data.get("data", [])

        # Not found
        if isinstance(results, dict) and results.get("message") == "not found":
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

        # Only 5 records
        cleaned = []
        for item in results[:5]:
            cleaned.append({
                "mobile": item.get("mobile"),
                "name": item.get("name"),
                "father_name": item.get("fname"),
                "address": item.get("address"),
                "alternate": item.get("alt"),
                "circle": item.get("circle"),
                "id": item.get("id"),
                "email": item.get("email")
            })

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

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
