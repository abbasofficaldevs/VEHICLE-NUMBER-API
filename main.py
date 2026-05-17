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
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except:
        return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except:
        pass

def get_from_cache(vehicle_number):
    cache = load_cache()
    return cache.get(vehicle_number, {}).get("number")

def save_to_cache(vehicle_number, mobile_number):
    cache = load_cache()
    cache[vehicle_number] = {"number": mobile_number, "cached_at": datetime.now().isoformat()}
    save_cache(cache)

def create_session():
    session = requests.Session()
    retry = Retry(total=2, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    })
    return session

def get_chassis_last_5(vehicle_number):
    try:
        resp = requests.get(CHASSIS_API_URL.format(vehicle_number), timeout=20)
        data = resp.json()
        chassis = data.get("chassis", "").replace(" ", "")
        if len(chassis) >= 5:
            return {"success": True, "chassis_last_5": chassis[-5:]}
        return {"success": False, "error": "Chassis too short"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def extract_viewstate(html):
    soup = BeautifulSoup(html, 'html.parser')
    vs = soup.find('input', {'name': 'javax.faces.ViewState'})
    return vs.get('value') if vs else None

def extract_viewstate_from_ajax(text):
    m = re.search(r'<update id="j_id1:javax.faces.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>', text)
    return m.group(1) if m else None

def find_checkbox_id(html):
    m = re.search(r'<div[^>]*id="(j_idt\d+)"[^>]*class="[^"]*ui-chkbox', html)
    if not m:
        m = re.search(r'PrimeFaces\.cw\("SelectBooleanCheckbox"[^}]*id:"(j_idt\d+)"', html)
    return m.group(1) if m else "j_idt193"

def fetch_mobile_number(vehicle_number, chassis_last_5):
    session = create_session()
    
    ajax_headers = {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Faces-Request': 'partial/ajax',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://vahan.parivahan.gov.in',
    }

    for attempt in range(2):
        try:
            time.sleep(1)

            # Step 1: Homepage
            r1 = session.get(HOMEPAGE_URL, timeout=30)
            if r1.status_code != 200:
                continue
            viewstate = extract_viewstate(r1.text)
            if not viewstate:
                continue

            checkbox_id = find_checkbox_id(r1.text)

            # Step 2: RTO
            ajax_headers['Referer'] = HOMEPAGE_URL
            r2 = session.post(HOMEPAGE_BASE, data={
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': 'fit_c_office_to',
                'javax.faces.partial.execute': 'fit_c_office_to',
                'javax.faces.behavior.event': 'change',
                'javax.faces.partial.event': 'change',
                'homepageformid': 'homepageformid',
                'fit_c_office_to_input': '1',
                'javax.faces.ViewState': viewstate,
            }, headers=ajax_headers, timeout=30)
            time.sleep(0.5)
            viewstate = extract_viewstate_from_ajax(r2.text) or viewstate

            # Step 3: Checkbox
            r3 = session.post(HOMEPAGE_BASE, data={
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': checkbox_id,
                'javax.faces.partial.execute': checkbox_id,
                'javax.faces.partial.render': 'proccedHomeButtonId',
                'javax.faces.behavior.event': 'change',
                'homepageformid': 'homepageformid',
                f'{checkbox_id}_input': 'on',
                'javax.faces.ViewState': viewstate,
            }, headers=ajax_headers, timeout=30)
            time.sleep(0.5)
            viewstate = extract_viewstate_from_ajax(r3.text) or viewstate

            # Step 4: Proceed
            r4 = session.post(HOMEPAGE_BASE, data={
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': 'proccedHomeButtonId',
                'javax.faces.partial.execute': '@all',
                'proccedHomeButtonId': 'proccedHomeButtonId',
                'homepageformid': 'homepageformid',
                f'{checkbox_id}_input': 'on',
                'javax.faces.ViewState': viewstate,
            }, headers=ajax_headers, timeout=30)
            time.sleep(0.5)
            viewstate = extract_viewstate_from_ajax(r4.text) or viewstate

            # Step 5: Dialog
            dialog_match = re.search(r'id="(j_idt\d+)"[^>]*class="[^"]*ui-button', r4.text)
            dialog_btn = dialog_match.group(1) if dialog_match else "j_idt536"
            r5 = session.post(HOMEPAGE_BASE, data={
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': dialog_btn,
                'javax.faces.partial.execute': '@all',
                f'{dialog_btn}': dialog_btn,
                'homepageformid': 'homepageformid',
                f'{checkbox_id}_input': 'on',
                'javax.faces.ViewState': viewstate,
            }, headers=ajax_headers, timeout=30)
            time.sleep(0.5)
            viewstate = extract_viewstate_from_ajax(r5.text) or viewstate

            # Step 6: Login page
            r6 = session.get(LOGIN_URL + "?faces-redirect=true", timeout=30, allow_redirects=True)
            time.sleep(1)
            viewstate = extract_viewstate(r6.text)
            if not viewstate:
                continue

            # Step 7: Submit fitbalcTest
            fit_match = re.search(r'id="(j_idt\d+)"[^>]*name="\1"[^>]*type="submit"', r6.text)
            fit_btn = fit_match.group(1) if fit_match else "j_idt506"
            post_headers = {
                **session.headers,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://vahan.parivahan.gov.in',
                'Referer': LOGIN_URL + "?faces-redirect=true",
            }
            r7 = session.post(LOGIN_URL, data={
                'loginForm': 'loginForm',
                f'{fit_btn}': fit_btn,
                'javax.faces.ViewState': viewstate,
                'fitbalcTest': 'fitbalcTest',
                'pur_cd': '86',
            }, headers=post_headers, timeout=30, allow_redirects=True)
            time.sleep(1)

            # Step 8: Form page
            form_headers = {**session.headers, 'Referer': LOGIN_URL + "?faces-redirect=true"}
            r8 = session.get(FORM_URL, headers=form_headers, timeout=30)
            time.sleep(1)
            viewstate = extract_viewstate(r8.text)
            if not viewstate:
                continue

            # Step 9: Submit vehicle + chassis
            ajax_headers['Referer'] = FORM_URL
            r9 = session.post(FORM_URL, data={
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': 'balanceFeesFine:validate_dtls',
                'javax.faces.partial.execute': '@all',
                'javax.faces.partial.render': 'balanceFeesFine:auth_panel',
                'balanceFeesFine:validate_dtls': 'balanceFeesFine:validate_dtls',
                'balanceFeesFine': 'balanceFeesFine',
                'balanceFeesFine:tf_reg_no': vehicle_number,
                'balanceFeesFine:tf_chasis_no': chassis_last_5,
                'javax.faces.ViewState': viewstate,
            }, headers=ajax_headers, timeout=30)

            text = r9.text

            for pat in [r'id="balanceFeesFine:tf_mobile"[^>]*value="(\d{10})"',
                         r'value="(\d{10})"[^>]*id="balanceFeesFine:tf_mobile"',
                         r'balanceFeesFine:tf_mobile[^>]*value="(\d{10})"']:
                m = re.search(pat, text, re.DOTALL)
                if m and m.group(1)[0] in '6789':
                    return {"success": True, "mobile_number": m.group(1)}

            fallback = re.findall(r'\b[6-9]\d{9}\b', text)
            if fallback:
                return {"success": True, "mobile_number": fallback[0]}

        except Exception as e:
            print(f"Attempt {attempt+1}: {e}")

        if attempt == 0:
            time.sleep(3)

    return {"success": False, "error": "Mobile number not found"}

@app.route("/fetch", methods=["GET"])
def fetch_contact():
    vehicle_number = request.args.get("vehicle_number", "").strip().upper()
    vehicle_number = re.sub(r'[^A-Z0-9]', '', vehicle_number)

    if not vehicle_number or len(vehicle_number) < 6 or len(vehicle_number) > 12:
        return jsonify({"code": 400, "error": "Invalid vehicle number"}), 400

    cached = get_from_cache(vehicle_number)
    if cached:
        return jsonify({"code": 200, "number": cached})

    chassis_result = get_chassis_last_5(vehicle_number)
    if not chassis_result["success"]:
        return jsonify({"code": 400, "error": chassis_result["error"]}), 400

    mobile_result = fetch_mobile_number(vehicle_number, chassis_result["chassis_last_5"])

    if mobile_result["success"]:
        save_to_cache(vehicle_number, mobile_result["mobile_number"])
        return jsonify({"code": 200, "number": mobile_result["mobile_number"]})

    return jsonify({"code": 400, "error": mobile_result["error"]}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
