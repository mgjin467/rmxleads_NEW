\
import gspread
from google.oauth2.service_account import Credentials
from config import CFG

HEADERS_AGG = [
    "id","source","제목","기관/사업자","단계","주요일자","주소","lat","lon",
    "distance_km","est_m3","score","링크","수집일"
]

def open_ws(title: str, headers: list):
    scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CFG.GOOGLE_SERVICE_ACCOUNT_JSON, scopes=scopes)
    gc = gspread.authorize(creds)
    # 공유 드라이브 포함 검색
    try:
        sh = gc.open(CFG.SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        results = gc.list_spreadsheet_files(title=CFG.SPREADSHEET_NAME, include_team_drive_items=True)
        sh = gc.open_by_key(results[0]["id"])
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=1000, cols=max(30,len(headers)))
        ws.append_row(headers)
    return ws

def upsert(ws, headers: list, rows: list, id_col_name="id"):
    # Read existing IDs into a set
    data = ws.get_all_records()
    id_idx = headers.index(id_col_name)
    existing = set(str(r.get(id_col_name,"")).strip() for r in data)
    new_count = 0
    for row in rows:
        if str(row[id_idx]).strip() in existing: 
            continue
        ws.append_row(row, value_input_option="USER_ENTERED")
        new_count += 1
    return new_count
