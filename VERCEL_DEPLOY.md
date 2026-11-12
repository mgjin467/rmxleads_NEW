# Vercel 배포 안내

## 1. 배포
이 폴더 전체를 GitHub 저장소 루트에 업로드하고 Vercel에서 해당 저장소를 Import 합니다.
- Root Directory: `./` (저장소 루트)
- Framework Preset: Flask 또는 Other (자동 감지 권장)
- Build Command / Output Directory: 비워 둠
- Python: 3.12

이 프로젝트의 최상위 `app.py`가 Flask 앱을 내보냅니다.

## 2. 환경변수
Vercel > Project > Settings > Environment Variables에서 다음을 입력합니다.
- `GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT`: 서비스 계정 JSON 파일 **내용 전체** (JSON 텍스트). 파일을 공개 저장소에 올리지 마세요.
- `SPREADSHEET_NAME`: 구글 시트 이름 (기본 `ReadyMix_Leads`)
- `WS_AGG`: 워크시트명 (기본 `Leads`)
- `PLANT_LAT`, `PLANT_LON`, `SEARCH_RADIUS_KM`: 공장 좌표 및 검색 반경
- `DATAGOKR_SERVICE_KEY`, `KAKAO_REST_API_KEY`: 데이터 수집기를 실행하는 쪽에서 필요
서비스 계정 메일 주소를 대상 구글 시트에 공유해 주세요.

## 3. 제한 (중요)
- 웹 화면 `/` 및 구글 시트 데이터 열람 `/api/leads`는 Vercel에서 동작하도록 수정했습니다.
- `/api/run`: Vercel Functions는 이 프로젝트의 `threading.Thread` 기반 장시간 작업 실행/상태 공유를 신뢰성 있게 유지할 수 없으므로 Vercel 환경에서 501 반환. 수집 실행은 별도 상시 서버, VM, 작업 스케줄러 등으로 분리하세요.
- `/api/settings` POST: Vercel 배포 파일 시스템에 설정을 영구 저장할 수 없어 501 반환. 영구 설정 변경에는 외부 DB가 필요합니다.
- `leads_cache.json`은 배포 당시의 정적 스냅샷입니다. 신규 수집 데이터는 구글 시트에서 읽어와야 합니다.
- 외부에 공개하는 경우 인증/접근제어를 추가하세요.

## 4. 검증
`/api/config` 와 `/api/leads`를 열어 상태를 확인하세요.
로컬 테스트: `pip install -r rmx_leads/requirements.txt` 후 `python app.py` 대신 `flask --app app run --port 5000`을 실행합니다.
