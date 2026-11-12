\
import os
from dotenv import load_dotenv
load_dotenv()

class CFG:
    # Plant
    PLANT_LAT = float(os.getenv("PLANT_LAT","0"))
    PLANT_LON = float(os.getenv("PLANT_LON","0"))
    SEARCH_RADIUS_KM = float(os.getenv("SEARCH_RADIUS_KM","25"))

    # Generic
    REGION_KEYWORD = os.getenv("REGION_KEYWORD","")
    MIN_FLOOR_EST_M3 = float(os.getenv("MIN_FLOOR_EST_M3","0"))

    # Nara
    DATAGOKR_SERVICE_KEY = os.getenv("DATAGOKR_SERVICE_KEY","")
    NARA_ROWS_PER_PAGE = int(os.getenv("NARA_ROWS_PER_PAGE","200"))

    # Kakao Geocoding
    KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY","")

    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","./service_account.json")
    SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME","ReadyMix_Leads")
    WS_AGG = os.getenv("WS_AGG","Leads")
    WS_NARA = os.getenv("WS_NARA","Leads_Nara")
    WS_HUB = os.getenv("WS_HUB","Leads_Hub")
    WS_NOTICE = os.getenv("WS_NOTICE","Leads_Notice")
    WS_EIA = os.getenv("WS_EIA","Leads_EIA")

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN","")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID","")

    # HUB
    HUB_SERVICE_KEY = os.getenv("HUB_SERVICE_KEY","")
    HUB_API_BASE = os.getenv("HUB_API_BASE","https://apis.data.go.kr/1613000/ArchPmsService_v2")
    HUB_DUMP_FILES = [p.strip() for p in os.getenv("HUB_DUMP_FILES","").split(",") if p.strip()]

    # Notices
    NOTICE_SITES_CONFIG = os.getenv("NOTICE_SITES_CONFIG","./data/sample_local_notices_sites.yaml")

    # EIA
    EIA_API_BASE = os.getenv("EIA_API_BASE","")
    EIA_SERVICE_KEY = os.getenv("EIA_SERVICE_KEY","")
    EIA_SEARCH_URL = os.getenv("EIA_SEARCH_URL","")
