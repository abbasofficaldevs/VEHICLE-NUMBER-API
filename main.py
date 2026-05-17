from flask import Flask, request, jsonify
import requests
import re
import time

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# ================= VEHICLE API =================
VEHICLE_API = "https://vehicle-chass-id.vercel.app/info?vehicle="

# ================= GET FULL CHASSIS =================
def get_chassis(rc):
    try:
        r = requests.get(VEHICLE_API + rc, timeout=20)
        data = r.json()

        if data.get("status") != "success":
            return None

        chassis = (
            data.get("data", {}).get("vehicle_chasi_number")
            or data.get("data", {}).get("chassis")
            or data.get("data", {}).get("chassis_number")
            or data.get("data", {}).get("vehicle_chassis_number")
            or ""
        )

        if not chassis:
            return None

        chassis = re.sub(r'[^A-Z0-9]', '', chassis.upper())

        return chassis

    except Exception:
        return None

# ================= MOBILE FETCH =================
def get_mobile(rc, full_chassis):

    last5 = full_chassis[-5:]

    session = requests.Session()

    BASE = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }

    HP = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/statevalidation/homepage.xhtml?statecd=Mzc2MzM2MzAzNjY0MzIzODM3NjIzNjY0MzY2MjM3NDQ0Yw=="
    HB = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/statevalidation/homepage.xhtml"
    LI = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/usermgmt/login.xhtml"
    FR = "https://vahan.parivahan.gov.in/vahanservice/vahan/ui/balanceservice/form_reschedule_fitness.xhtml"

    for attempt in range(2):

        try:

            r = session.get(HP, headers=BASE, timeout=25)

            vs = re.search(
                r'<input[^>]*name="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
                r.text
            )

            if not vs:
                continue

            vs = vs.group(1)

            cid = "j_idt193"

            cm = re.search(
                r'<div[^>]*id="(j_idt\d+)"[^>]*class="[^"]*ui-chkbox',
                r.text
            )

            if cm:
                cid = cm.group(1)

            AH = {
                "Accept": "application/xml, text/xml, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded",
                "Faces-Request": "partial/ajax",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://vahan.parivahan.gov.in",
                "Referer": HP
            }

            # ================= OFFICE SELECT =================
            r = session.post(HB, headers=AH, data={
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": "fit_c_office_to",
                "javax.faces.partial.execute": "fit_c_office_to",
                "javax.faces.behavior.event": "change",
                "homepageformid": "homepageformid",
                "fit_c_office_to_input": "1",
                "javax.faces.ViewState": vs
            }, timeout=20)

            m = re.search(
                r'<update id="j_id1:javax\.faces\.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>',
                r.text
            )

            if m:
                vs = m.group(1)

            # ================= CHECKBOX =================
            r = session.post(HB, headers=AH, data={
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": cid,
                "javax.faces.partial.execute": cid,
                "javax.faces.partial.render": "proccedHomeButtonId",
                "javax.faces.behavior.event": "change",
                "homepageformid": "homepageformid",
                f"{cid}_input": "on",
                "javax.faces.ViewState": vs
            }, timeout=20)

            m = re.search(
                r'<update id="j_id1:javax\.faces\.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>',
                r.text
            )

            if m:
                vs = m.group(1)

            # ================= PROCEED =================
            r = session.post(HB, headers=AH, data={
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": "proccedHomeButtonId",
                "javax.faces.partial.execute": "@all",
                "proccedHomeButtonId": "proccedHomeButtonId",
                "homepageformid": "homepageformid",
                f"{cid}_input": "on",
                "javax.faces.ViewState": vs
            }, timeout=20)

            m = re.search(
                r'<update id="j_id1:javax\.faces\.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>',
                r.text
            )

            if m:
                vs = m.group(1)

            # ================= DIALOG =================
            dlg = "j_idt536"

            dm = re.search(
                r'id="(j_idt\d+)"[^>]*class="[^"]*ui-button',
                r.text
            )

            if dm:
                dlg = dm.group(1)

            r = session.post(HB, headers=AH, data={
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": dlg,
                "javax.faces.partial.execute": "@all",
                dlg: dlg,
                "homepageformid": "homepageformid",
                f"{cid}_input": "on",
                "javax.faces.ViewState": vs
            }, timeout=20)

            m = re.search(
                r'<update id="j_id1:javax\.faces\.ViewState:0"><!\[CDATA\[(.*?)\]\]></update>',
                r.text
            )

            if m:
                vs = m.group(1)

            # ================= LOGIN PAGE =================
            r = session.get(
                LI + "?faces-redirect=true",
                headers={**BASE, "Referer": HP},
                timeout=20
            )

            vs = re.search(
                r'<input[^>]*name="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
                r.text
            )

            if not vs:
                continue

            vs = vs.group(1)

            fit = "j_idt506"

            fm = re.search(
                r'id="(j_idt\d+)"[^>]*type="submit"',
                r.text
            )

            if fm:
                fit = fm.group(1)

            session.post(
                LI,
                headers={
                    **BASE,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://vahan.parivahan.gov.in",
                    "Referer": LI + "?faces-redirect=true"
                },
                data={
                    "loginForm": "loginForm",
                    fit: fit,
                    "javax.faces.ViewState": vs,
                    "fitbalcTest": "fitbalcTest",
                    "pur_cd": "86"
                },
                timeout=20
            )

            # ================= FITNESS PAGE =================
            r = session.get(
                FR,
                headers={**BASE, "Referer": LI + "?faces-redirect=true"},
                timeout=20
            )

            vs = re.search(
                r'<input[^>]*name="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
                r.text
            )

            if not vs:
                continue

            vs = vs.group(1)

            # ================= VALIDATE =================
            r = session.post(FR, headers={**AH, "Referer": FR}, data={
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": "balanceFeesFine:validate_dtls",
                "javax.faces.partial.execute": "@all",
                "javax.faces.partial.render": "balanceFeesFine:auth_panel",
                "balanceFeesFine:validate_dtls": "balanceFeesFine:validate_dtls",
                "balanceFeesFine": "balanceFeesFine",
                "balanceFeesFine:tf_reg_no": rc,
                "balanceFeesFine:tf_chasis_no": last5,
                "javax.faces.ViewState": vs
            }, timeout=20)

            # ================= MOBILE EXTRACT =================
            for p in [
                r'id="balanceFeesFine:tf_mobile"[^>]*value="(\d{10})"',
                r'value="(\d{10})"[^>]*id="balanceFeesFine:tf_mobile"',
                r'tf_mobile[^>]*value="(\d{10})"'
            ]:

                m = re.search(p, r.text)

                if m and m.group(1)[0] in "6789":
                    return {
                        "success": True,
                        "reg_no": rc,
                        "mobile": m.group(1),
                        "full_chassis": full_chassis,
                        "chassis_last5": last5
                    }

            nums = re.findall(r'\b[6-9]\d{9}\b', r.text)

            if nums:
                return {
                    "success": True,
                    "reg_no": rc,
                    "mobile": nums[0],
                    "full_chassis": full_chassis,
                    "chassis_last5": last5
                }

        except Exception:
            pass

        if attempt == 0:
            time.sleep(2)

    return {
        "success": False,
        "reg_no": rc,
        "mobile": "Not Available",
        "full_chassis": full_chassis,
        "chassis_last5": last5
    }

# ================= API ROUTE =================
@app.route("/api/mobile", methods=["GET"])
def mobile_info():

    rc = request.args.get("rc", "").strip().upper()

    rc = re.sub(r'[^A-Z0-9]', '', rc)

    if not rc:
        return jsonify({
            "success": False,
            "error": "RC parameter required"
        }), 400

    # ================= FETCH FULL CHASSIS =================
    full_chassis = get_chassis(rc)

    if not full_chassis:
        return jsonify({
            "success": False,
            "error": "Unable to fetch chassis from vehicle API"
        }), 400

    # ================= FETCH MOBILE =================
    return jsonify(get_mobile(rc, full_chassis))

# ================= START =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
