# Ready-Mix Leads (확장판)

현장 리드 수집/정제/스코어링/시각화까지 자동화하는 파이썬 툴킷입니다.

## 구성
- `main_full.py`: (권장) 나라장터 + 건축HUB + 지자체 고시공고 + EIA 병행 수집 → 지오코딩 → 스코어 → 시트 업서트 → 텔레그램 알림
- `main_minimal.py`: (빠른 시작) 나라장터 공고만 사용 (이전 제공본 개선)
- `generate_map.py`: 시트 데이터를 Folium 지도(반경/클러스터/팝업)로 HTML 생성

- `modules/narajangteo.py`: 나라장터 공고 수집 + 상세페이지 주소 파싱
- `modules/hub.py`: 건축허가(HUB) – OpenAPI 또는 월별 덤프 파일 읽기
- `modules/notices.py`: 지자체 고시/공고 사이트 스크랩(구성 파일 기반)
- `modules/eia.py`: 환경영향평가 – API 또는 검색페이지 스크랩(구성 기반)
- `parsers/bid_detail.py`: 공고 상세 HTML에서 주소/현장 후보 추출 유틸

- `config.py`, `geocode.py`, `sheet.py`, `utils.py`, `scoring.py`

## 설치
```bash
pip install -r requirements.txt
cp .env.sample .env
# .env를 열어 키/좌표/시트명/반경 등을 수정
```

## 실행
```bash
# (권장) 풀 파이프라인
python main_full.py

# 지도 갱신
python generate_map.py
```

## 운영 팁
- HUB API가 불안정할 경우: 월별 대용량 덤프 파일(CSV/XLSX)을 `HUB_DUMP_FILES`에 경로로 넣고 사용하세요.
- 지자체 고시공고: `data/sample_local_notices_sites.yaml`에 사이트/셀렉터를 추가해 확장(샘플 제공).
- EIA: 가능하면 API를 쓰되, 불가하면 검색 리스트 스크랩 모드로 동작합니다.
- 키 보안: `.env`는 내부 저장소에 두고, 키는 레포에 커밋하지 마세요.
