# rmx_leads

Python CLI toolkit for collecting, scoring, and visualizing ready-mix concrete leads (Korean construction bids/permits).

## Stack
- Python 3.12
- Libraries: requests, pandas, gspread, google-auth, beautifulsoup4, lxml, tenacity, folium, pyyaml, python-dotenv, openpyxl

## Layout
- `rmx_leads/main_minimal.py` – minimal pipeline (Nara bids only)
- `rmx_leads/main_full.py` – full pipeline (Nara + HUB + Notices + EIA)
- `rmx_leads/generate_map.py` – Folium HTML map generator
- `rmx_leads/modules/`, `rmx_leads/parsers/` – source-specific scrapers

## Workflow
- `Start application` (console): `cd rmx_leads && python main_minimal.py`

## Configuration
Set environment variables (see `rmx_leads/config.py`) to enable each data source:
`DATAGOKR_SERVICE_KEY`, `KAKAO_REST_API_KEY`, `HUB_SERVICE_KEY`, `EIA_*`,
`PLANT_LAT`, `PLANT_LON`, `SEARCH_RADIUS_KM`, Google Sheets / Telegram credentials.
Without keys, modules log a skip warning and exit cleanly.
