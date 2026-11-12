import os, json, logging, threading
from flask import Flask, render_template, jsonify, request
from google.oauth2.service_account import Credentials

from config import CFG
from sheet import HEADERS_AGG

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "data", "settings.json")

DEFAULT_SETTINGS = {
    "plant_lat": CFG.PLANT_LAT,
    "plant_lon": CFG.PLANT_LON,
    "search_radius_km": CFG.SEARCH_RADIUS_KM,
    "region_keywords": ["진천", "음성", "청주"],
    "region_mode": "OR",
    "content_keywords": ["레미콘"],
    "content_mode": "OR",
    "days_back": 30,
}


def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(s):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


def _read_from_sheet():
    try:
        import gspread
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT", "").strip()
        if raw:
            creds = Credentials.from_service_account_info(json.loads(raw), scopes=scopes)
        else:
            credential_path = CFG.GOOGLE_SERVICE_ACCOUNT_JSON
            if not os.path.isabs(credential_path):
                credential_path = os.path.join(os.path.dirname(__file__), credential_path)
            if not os.path.exists(credential_path):
                return None, "Google 인증정보가 없습니다. Vercel 환경변수 GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT를 설정하세요."
            creds = Credentials.from_service_account_file(credential_path, scopes=scopes)
        gc = gspread.authorize(creds)
        try:
            sh = gc.open(CFG.SPREADSHEET_NAME)
        except gspread.SpreadsheetNotFound:
            results = gc.list_spreadsheet_files(
                title=CFG.SPREADSHEET_NAME, include_team_drive_items=True
            )
            sh = gc.open_by_key(results[0]["id"])
        ws = sh.worksheet(CFG.WS_AGG)
        return ws.get_all_records(), None
    except Exception as e:
        logging.exception("Google Sheets 조회 오류")
        return None, f"Google Sheets 연결 실패 ({type(e).__name__}). Vercel Runtime Logs를 확인하세요."


def _read_from_cache():
    path = os.path.join(os.path.dirname(__file__), "data", "leads_cache.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _load_leads():
    rows, err = _read_from_sheet()
    cached = _read_from_cache()
    merged = {r.get("id"): r for r in cached}
    for r in (rows or []):
        if r.get("id"):
            merged[r["id"]] = r
    result = sorted(merged.values(), key=lambda x: x.get("score", 0), reverse=True)
    return result, (err if not rows else None)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    s = load_settings()
    return render_template(
        "index.html",
        plant_lat=s["plant_lat"],
        plant_lon=s["plant_lon"],
        radius_km=s["search_radius_km"],
        spreadsheet=CFG.SPREADSHEET_NAME,
        worksheet=CFG.WS_AGG,
    )


@app.route("/api/leads")
def api_leads():
    rows, err = _load_leads()
    s = load_settings()
    return jsonify({
        "leads": rows,
        "error": err,
        "plant": {
            "lat": s["plant_lat"],
            "lon": s["plant_lon"],
            "radius_km": s["search_radius_km"],
        },
        "headers": HEADERS_AGG,
    })


@app.route("/api/config")
def api_config():
    return jsonify({
        "plant_lat": CFG.PLANT_LAT,
        "plant_lon": CFG.PLANT_LON,
        "radius_km": CFG.SEARCH_RADIUS_KM,
        "spreadsheet": CFG.SPREADSHEET_NAME,
        "worksheet": CFG.WS_AGG,
        "has_nara_key": bool(CFG.DATAGOKR_SERVICE_KEY),
        "has_kakao_key": bool(CFG.KAKAO_REST_API_KEY),
        "has_service_account": bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT")) or os.path.exists(os.path.join(os.path.dirname(__file__), CFG.GOOGLE_SERVICE_ACCOUNT_JSON)),
        "is_vercel": bool(os.getenv("VERCEL")),
        "can_save_settings": not bool(os.getenv("VERCEL")),
        "can_run_pipeline": not bool(os.getenv("VERCEL")),
    })


@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify(load_settings())


@app.route("/api/settings", methods=["POST"])
def post_settings():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"ok": False, "msg": "JSON 객체가 필요합니다."}), 400
    allowed = {
        "plant_lat", "plant_lon", "search_radius_km",
        "region_keywords", "region_mode",
        "content_keywords", "content_mode",
        "days_back",
    }
    current = load_settings()
    for k in allowed:
        if k in data:
            current[k] = data[k]
    if os.getenv("VERCEL"):
        return jsonify({"ok": False, "msg": "Vercel에서는 로컬 설정 파일을 영구 저장할 수 없습니다. 외부 DB 저장소가 필요합니다."}), 501
    save_settings(current)
    return jsonify({"ok": True, "settings": current})


@app.route("/api/run", methods=["POST"])
def api_run():
    if os.getenv("VERCEL"):
        return jsonify({"ok": False, "msg": "Vercel에서는 현재 백그라운드 수집 방식을 지원하지 않습니다. 수집기는 별도 서버/스케줄러에서 실행해야 합니다."}), 501
    import pipeline
    if pipeline.get_status()["running"]:
        return jsonify({"ok": False, "msg": "이미 실행 중입니다"})
    s = load_settings()
    t = threading.Thread(target=pipeline.run, args=(s,), daemon=True)
    t.start()
    return jsonify({"ok": True, "msg": "수집 시작됨"})


@app.route("/api/status")
def api_status():
    if os.getenv("VERCEL"):
        return jsonify({"running": False, "msg": "Vercel: 웹 조회 전용. 데이터 수집은 외부 실행 환경에서 수행해야 합니다.", "last": None, "supported": False})
    import pipeline
    return jsonify({**pipeline.get_status(), "supported": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
