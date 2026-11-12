# Ready-Mix Leads 개발 및 운영 가이드

## 1. 프로젝트 목적과 처리 흐름
나라장터 등 공고 데이터 → 수집기(별도 실행) → 키워드/지역 필터 → 카카오 지오코딩 → 공장 반경/예상 레미콘 물량/점수 → 로컬 캐시 및 Google Sheets(일부 수집 스크립트) → Flask API → 지도와 표.

`pipeline.py`는 현재 캐시 파일 저장 방식이며 **자동으로 Google Sheets에 쓰지 않습니다**. `main_full.py`, `main_minimal.py`는 Google Sheets upsert를 별도로 수행합니다. 모듈이 존재하는 것과 현재 웹 버튼에 통합된 것은 다릅니다.

## 2. 파일 안내
- `app.py`: 웹 서버, API, 캐시/Google Sheets 조회, 설정
- `templates/index.html`: Leaflet 지도, 검색·필터·설정 UI (HTML/CSS/JS 단일 파일)
- `config.py`: 환경변수 및 기본값
- `pipeline.py`: 웹의 로컬 수집 버튼이 호출하는 나라장터 수집 흐름
- `main_full.py`: 나라장터·건축 인허가·지자체 공고·EIA를 다루는 확장 수집기
- `main_minimal.py`, `run_local.py`: 개별 수집 실행 도구
- `modules/`: 원천 데이터 API/스크래핑 연계
- `parsers/`: 공고 상세주소 추출
- `geocode.py`, `scoring.py`, `utils.py`: 좌표 변환, 점수 계산, 공통 함수
- `sheet.py`: 시트 접근/upsert
- `data/leads_cache.json`: 배포 시 포함된 오래된 캐시 스냅샷 (영구 DB 아님)

## 3. 주요 API
| 메서드 | 경로 | 기능 | 환경 |
|---|---|---|---|
| GET | `/` | 대시보드 렌더링 | 모두 |
| GET | `/api/leads` | 시트+캐시 합쳐 점수순 데이터, 상태 오류 | 모두 |
| GET | `/api/config` | API 키 존재 여부(실제 키 미노출), 실행 가능 기능 | 모두 |
| GET | `/api/settings` | 현재 서버 설정 읽기 | 모두 |
| POST | `/api/settings` | 서버 설정 JSON 저장 | 로컬만; Vercel 501 |
| POST | `/api/run` | Python 백그라운드 스레드로 수집 시작 | 로컬만; Vercel 501 |
| GET | `/api/status` | 로컬 수집 진행 메시지 | 모두(배포 모드 비활성) |

## 4. 환경변수
| 변수 | 의미 | 비고 |
|---|---|---|
| PLANT_LAT, PLANT_LON | 공장 좌표 | WGS84 십진수, 0이면 공장 미지정 |
| SEARCH_RADIUS_KM | 기본 검색 반경 | km |
| SPREADSHEET_NAME, WS_AGG | Google Sheets 문서명/집계 탭 | 기본 ReadyMix_Leads / Leads |
| GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT | 서비스 계정 JSON 문자열 전체 | Vercel 비밀 환경변수 |
| GOOGLE_SERVICE_ACCOUNT_JSON | 로컬 서비스 계정 JSON 파일 경로 | GitHub 업로드 금지 |
| DATAGOKR_SERVICE_KEY | 나라장터 API 인증키 | 비밀 |
| KAKAO_REST_API_KEY | 카카오 주소→좌표 API 키 | 비밀 |
| HUB_SERVICE_KEY, HUB_API_BASE, HUB_DUMP_FILES | 건축·인허가 수집 | 선택 |
| EIA_SERVICE_KEY, EIA_API_BASE, EIA_SEARCH_URL | EIA 수집 | 선택 |
| NOTICE_SITES_CONFIG | 지자체 공고 사이트 YAML | 로컬 경로 |
| TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID | 알림 전송 설정 | 구현과 연계 여부 확인 필요 |

서비스 계정 이메일을 대상 스프레드시트에 공유해야 읽을 수 있습니다. Vercel의 환경변수 변경 후에는 새 배포가 필요합니다. API 키와 개인정보는 Git 커밋/프런트 JS에 절대 넣지 않습니다.

## 5. 검색과 설정의 차이
- **검색창/출처/단계/거리/점수 필터:** 이미 불러온 결과의 브라우저 표시만 변경합니다. CSV도 현재 필터 결과입니다.
- **설정 드로어:** 공장 위치, 수집 기간, 키워드(OR/AND) 설정. 로컬 Flask에서는 서버 파일 저장 가능. Vercel에서는 저장 불가능하므로 브라우저 초안만 저장하며 수집 작업에 적용되지 않습니다.
- 나라장터 공고 수집 조건은 `pipeline.py` / 실행 환경의 설정을 확인하세요. 이미 저장된 캐시 데이터를 바꾸지는 않습니다.

## 6. Vercel과 수집기의 역할 구분
Vercel Functions는 요청당 실행이며 배포 파일 시스템은 읽기 전용(`/tmp` 임시 저장은 영구 보존 안 됨). Python 스레드 수집과 JSON 영구 쓰기는 불안정하거나 불가능합니다. 현재 `/api/run` 및 `/api/settings` POST는 명시적으로 501을 반환합니다.

안정적인 확장안: Windows 작업 스케줄러 / GitHub Actions / Cloud Run Jobs 중 하나에서 수집기 실행 → Google Sheets/BigQuery 같은 외부 저장소 갱신 → Vercel은 읽기 전용 Flask API/화면 제공. 웹에서 ‘지금 수집’을 활성화하려면 인증된 작업 큐/외부 실행 서비스 및 상태 DB를 별도로 연결해야 합니다.

## 7. 개발 순서
1. 새 기능 요구를 '데이터 수집 / 계산·정제 / API / UI' 중 어디에 넣을지 구분
2. 기존 API 응답 필드(`id`, `제목`, `source`, `lat`, `lon`, `score`, `distance_km`, `est_m3`) 유지
3. `python -m compileall -q .` 및 `python -m pytest`(테스트 추가 후)
4. `python app.py` 로컬 확인 → `/api/config`, `/api/leads`, `/` 확인
5. Git 브랜치에 수정·테스트, Preview 배포 후 Production 승격
6. Google Sheets 캐시가 실시간으로 갱신되는지, 키 실패 시 상태 안내가 맞는지 점검

추천 후속 개발: 로그인/권한, 공고별 최신 수집 시각, 실제 마감일/공고 상태, 반경 외 보기, 중복 제거, 지도 마커 성능(대량 데이터 시), 수집기 외부 실행 및 작업 이력 테이블, 설정 저장 DB.

## 8. 주의사항
- `score`, `est_m3`은 `scoring.py`의 규칙 기반 추정값이고, 확정 발주 물량이 아닙니다.
- Google 인증 오류가 나면 `data/leads_cache.json` 스냅샷으로 보일 수 있어 '최신 공고'로 취급하면 안 됩니다.
- `/api/leads`는 현재 로그인 없이 누구나 호출 가능. 공개 서비스 운영 전 인증/인가 및 키 관리가 필요합니다.
- 화면 Leaflet / OpenStreetMap 타일과 외부 링크에 의존합니다. 서비스 트래픽 증가 시 타일 이용정책을 확인하세요.
