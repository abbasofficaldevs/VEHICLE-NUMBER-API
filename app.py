from flask import Flask, request, jsonify
import requests
import re
import json
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vehicle_cache.json")

CHASSIS_API_URL = "https://vehicle2chassis.profilework239.workers.dev/?plate={}"

HOMEPAGE_URL = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/statevalidation/homepage.xhtml?statecd=Mzc2MzM2MzAzNjY0MzIzODM3NjIzNjY0MzY2MjM3NDQ0Yw=="
HOMEPAGE_BASE = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/statevalidation/homepage.xhtml"
LOGIN_URL = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/usermgmt/login.xhtml"
FORM_URL = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/balanceservice/form_reschedule_fitness.xhtml"


def load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}


def save_cache(cache):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except:
        pass


def get_from_cache(vehicle_number):
    cache = load_cache()
    return cache.get(vehicle_number, {}).get("number")


def save_to_cache(vehicle_number, mobile_number):
    cache = load_cache()
    cache[vehicle_number] = {
        "number": mobile_number,
        "cached_at": datetime.now().isoformat()
    }
    save_cache(cache)


def create_session():
    session = requests.Session()

    retry = Retry(
        total=2,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504]
    )

    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=10,
        pool_maxsize=10
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    })

    return session


def get_chassis_last_5(vehicle_number):
    try:
        resp = requests.get(
            CHASSIS_API_URL.format(vehicle_number),
            timeout=20
        )

        if resp.status_code != 200:
            return {
                "success": False,
                "error": f"API status {resp.status_code}"
            }

        try:
            data = resp.json()
        except:
            return {
                "success": False,
                "error": "Invalid JSON response"
            }

        chassis = str(data.get("chassis", "")).replace(" ", "")

        if len(chassis) >= 5:
            return {
                "success": True,
                "chassis_last_5": chassis[-5:]
            }

        return {
            "success": False,
            "error": "Chassis not found"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.route("/")
def home():
    return jsonify({
        "status": "running"
    })


@app.route("/fetch", methods=["GET"])
def fetch_contact():
    vehicle_number = request.args.get(
        "vehicle_number",
        ""
    ).strip().upper()

    vehicle_number = re.sub(r"[^A-Z0-9]", "", vehicle_number)

    if not vehicle_number:
        return jsonify({
            "code": 400,
            "error": "Vehicle number required"
        }), 400

    return jsonify({
        "code": 200,
        "vehicle_number": vehicle_number,
        "message": "API working"
    })


@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({
        "code": 500,
        "error": str(e)
    }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
