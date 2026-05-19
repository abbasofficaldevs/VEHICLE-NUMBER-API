
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ==========================================
# MASTER API
# ==========================================

@app.route("/")
def home():
    return jsonify({
        "owner": "Rajan",
        "message": "Master API Running",
        "endpoints": {
            "joke": "/api?joke=true",
            "country": "/api?country=india",
            "weather": "/api?weather=true&lat=52.52&lon=13.41",
            "gender": "/api?gender=rahul",
            "age": "/api?age=rajan",
            "nationality": "/api?nation=nathaniel",
            "university": "/api?university=india",
            "currency": "/api?currency=USD",
            "faker": "/api?faker=true",
            "instagram": "/api?instagram=rajan_hacker_123",
            "image": "/api?image=girl"
        }
    })

# ==========================================
# MAIN API ROUTE
# ==========================================

@app.route("/api")
def api():

    # RANDOM JOKE
    if request.args.get("joke"):
        url = "https://official-joke-api.appspot.com/random_joke"
        data = requests.get(url).json()

        return jsonify({
            "type": "joke",
            "result": data
        })

    # COUNTRY INFO
    elif request.args.get("country"):
        country = request.args.get("country")

        url = f"https://restcountries.com/v3.1/name/{country}"
        data = requests.get(url).json()

        return jsonify({
            "type": "country",
            "result": data
        })

    # WEATHER
    elif request.args.get("weather"):
        lat = request.args.get("lat")
        lon = request.args.get("lon")

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

        data = requests.get(url).json()

        return jsonify({
            "type": "weather",
            "result": data
        })

    # GENDER PREDICTION
    elif request.args.get("gender"):
        name = request.args.get("gender")

        url = f"https://api.genderize.io?name={name}"
        data = requests.get(url).json()

        return jsonify({
            "type": "gender",
            "result": data
        })

    # AGE PREDICTION
    elif request.args.get("age"):
        name = request.args.get("age")

        url = f"https://api.agify.io?name={name}"
        data = requests.get(url).json()

        return jsonify({
            "type": "age",
            "result": data
        })

    # NATIONALITY
    elif request.args.get("nation"):
        name = request.args.get("nation")

        url = f"https://api.nationalize.io?name={name}"
        data = requests.get(url).json()

        return jsonify({
            "type": "nationality",
            "result": data
        })

    # UNIVERSITY SEARCH
    elif request.args.get("university"):
        country = request.args.get("university")

        url = f"http://universities.hipolabs.com/search?country={country}"
        data = requests.get(url).json()

        return jsonify({
            "type": "university",
            "result": data
        })

    # CURRENCY
    elif request.args.get("currency"):
        base = request.args.get("currency")

        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        data = requests.get(url).json()

        return jsonify({
            "type": "currency",
            "result": data
        })

    # FAKER PERSON
    elif request.args.get("faker"):
        url = "https://fakerapi.it/api/v1/persons?_quantity=1"

        data = requests.get(url).json()

        return jsonify({
            "type": "faker",
            "result": data
        })

    # INSTAGRAM LOOKUP
    elif request.args.get("instagram"):
        user = request.args.get("instagram")

        url = f"https://jdcreator.site/ig/ig.php?user={user}"

        data = requests.get(url).json()

        return jsonify({
            "type": "instagram",
            "result": data
        })

    # AI IMAGE
    elif request.args.get("image"):
        prompt = request.args.get("image")

        image_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1920&height=1080&model=flux"

        return jsonify({
            "type": "image",
            "image_url": image_url
        })

    # NO PARAMETER
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid Parameter"
        })


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)