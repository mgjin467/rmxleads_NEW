\
import os, pandas as pd, folium
from folium.plugins import MarkerCluster
from google.oauth2.service_account import Credentials
import gspread
from config import CFG

OUTPUT_HTML = "leads_map.html"

def open_df(title: str):
    scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CFG.GOOGLE_SERVICE_ACCOUNT_JSON, scopes=scopes)
    gc = gspread.authorize(creds)
    try:
        sh = gc.open(CFG.SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        results = gc.list_spreadsheet_files(title=CFG.SPREADSHEET_NAME, include_team_drive_items=True)
        sh = gc.open_by_key(results[0]["id"])
    ws = sh.worksheet(title)
    return pd.DataFrame(ws.get_all_records())

def make_map(df: pd.DataFrame):
    m = folium.Map(location=[CFG.PLANT_LAT, CFG.PLANT_LON], zoom_start=11, control_scale=True)
    folium.Marker([CFG.PLANT_LAT, CFG.PLANT_LON], tooltip="플랜트", popup="플랜트").add_to(m)
    folium.Circle(radius=CFG.SEARCH_RADIUS_KM*1000, location=[CFG.PLANT_LAT, CFG.PLANT_LON], fill=False, weight=2).add_to(m)

    clusters = {}
    for src in ["NARA","HUB","NOTICE","EIA",""]:
        clusters[src] = MarkerCluster(name=f"{src or 'UNKNOWN'}").add_to(m)

    for _, r in df.iterrows():
        lat, lon = float(r.get("lat",0) or 0), float(r.get("lon",0) or 0)
        if not lat or not lon: 
            continue
        src = r.get("source","")
        pop = (
            f"<b>{r.get('제목','')}</b><br>"
            f"{r.get('기관/사업자','')} / {r.get('단계','')}<br>"
            f"일자: {r.get('주요일자','')} / 점수: {r.get('score','')}<br>"
            f"거리: {r.get('distance_km','')} km<br>"
            f"<a href='{r.get('링크','')}' target='_blank'>상세</a>"
        )
        folium.Marker([lat,lon], popup=pop, tooltip=r.get("제목","")).add_to(clusters.get(src, m))

    folium.LayerControl().add_to(m)
    m.save(OUTPUT_HTML)
    return OUTPUT_HTML

def main():
    try:
        df = open_df(CFG.WS_AGG)
    except Exception:
        df = open_df("Leads")  # 호환
    if df.empty:
        print("데이터 없음")
        return
    out = make_map(df.sort_values("score", ascending=False))
    print(f"지도 생성: {out}")

if __name__ == "__main__":
    main()
