# Ready-Mix Leads · 정리된 Flask 프로젝트 (v2)

Vercel 웹 조회와 별도 로컬 수집기를 하나의 저장소에서 관리합니다. 기존 API, 수집 모듈, 지도, 시트 연동 기능을 보존하되 중복된 `rmx_leads/`, `api/` 진입점은 제거했습니다.

## 시작

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
# .env.example을 .env로 복사한 뒤 값을 입력
python app.py
```

Vercel: GitHub 저장소 루트에 이 ZIP의 내용물을 배치합니다. Root Directory=`./`, Framework Preset=Flask, 빌드 명령과 Output Directory 오버라이드 없음. Flask 자동 탐지이므로 Rewrite 설정 없음.

## 기능
- 조회 `GET /`, `GET /api/leads`, `GET /api/config`, `GET /api/settings`, `GET /api/status`
- 로컬 전용 `POST /api/settings`, `POST /api/run` (Vercel에서는 501 반환)
- 지도, 정렬, 통합 텍스트 검색, 출처·단계·거리·최저 점수 필터, CSV 내보내기, 공고 원문 링크
- 브라우저 필터 저장(localStorage), Vercel 설정 변경은 로컬 초안만 보관하고 서버에 적용되지 않음
- 수집 코드 `pipeline.py`, `main_full.py`, `main_minimal.py`, `run_local.py`, `modules/`, `parsers/` 보존

**주의:** 배포에 포함된 `data/leads_cache.json`은 예시/이전 시점 캐시입니다. Google Sheets 연결 실패 시에도 목록이 보일 수 있어 실시간 공고로 간주하면 안 됩니다.

자세한 안내: `DEVELOPMENT_GUIDE.md`.
