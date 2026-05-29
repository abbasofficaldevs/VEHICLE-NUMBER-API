from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

API_URL = "https://abhaykumar.xo.je/api/proxy.php?tool=number_info&query="

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

        result = data.get("data", {})

        # Not found
        if result.get("Status") == "No information found":
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

        # Same old structure
        cleaned = [{
            "mobile": result.get("Mobile Number"),
            "name": result.get("Name"),
            "father_name": result.get("Father Name"),
            "address": result.get("Address"),
            "alternate": result.get("Alternate Number"),
            "circle": result.get("Circle"),
            "id": result.get("Aadhaar"),
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

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
