from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

API_URL = "https://rootx-osint.in/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
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
        r = requests.get(
            API_URL,
            params={
                "type": "num",
                "key": "@abbas_devs",
                "query": number
            },
            headers=HEADERS,
            timeout=30
        )

        data = r.json()

        # error case
        if isinstance(data, dict) and data.get("status") == "error":
            return jsonify({
                "status": "failed",
                "message": "no data found",
                "records": []
            })

        records = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "MOBILE" in item:
                    records.append({
                        "mobile": item.get("MOBILE"),
                        "name": item.get("NAME"),
                        "father_name": item.get("fname"),
                        "address": item.get("ADDRESS"),
                        "alternate": item.get("alt"),
                        "circle": item.get("circle"),
                        "id": item.get("id")
                    })

        # max 5 records only
        records = records[:5]

        return jsonify({
            "status": "success",
            "total_records": len(records),
            "records": records
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
