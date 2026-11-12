# Vercel 배포 (404 수정본)

이전 버전은 명시적 요청 라우팅이 없어서 Ready 상태에서도 404 NOT_FOUND가 나타날 수 있었습니다.
이번 수정본은 `api/index.py`를 Python Function으로 사용하고 `vercel.json`에서 `/` 및 `/api/...` 경로를 모두 연결합니다.

## GitHub 업로드
ZIP을 풀고 **그 폴더 안의 모든 파일을** GitHub 저장소 최상위에 올리세요. ZIP 파일 자체를 업로드하는 것이 아닙니다.
저장소 루트에서 바로 `vercel.json`, `requirements.txt`, `api/index.py`, `rmx_leads/`가 보여야 합니다.
기존 파일 `app.py`, `pyproject.toml`, `uv.lock`은 제거된 구성이며 과거 저장소에 남아 있으면 GitHub에서도 삭제하세요.

## Vercel 설정
- Settings → Build and Deployment → Root Directory: 저장소 최상위 `./`
- Framework Preset: `Other`
- Build Command, Output Directory, Install Command: **Override를 끄고 비워 두세요**
- GitHub에 업데이트 후 Deployments → Redeploy (Build Cache 비활성화 권장)

## 점검
1. `https://본인도메인.vercel.app/api/config` : JSON이 표시되면 Python 앱 진입점 성공
2. `https://본인도메인.vercel.app/` : HTML 화면 표시
3. `https://본인도메인.vercel.app/api/leads` : JSON 데이터/인증오류 확인
404가 반복되면 Deployment → Source에서 `api/index.py`, `vercel.json` 업로드 여부를 확인하고, Runtime Logs도 확인하세요.

## 환경변수
- `GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT` : 서비스 계정 JSON 전체(공개 GitHub에 올리지 말 것)
- `SPREADSHEET_NAME`, `WS_AGG` : 시트명/탭명
- `PLANT_LAT`, `PLANT_LON`, `SEARCH_RADIUS_KM` : 좌표/검색 반경

주의: Flask 웹 UI/데이터 조회만 Vercel에 맞춥니다. `/api/run` 백그라운드 작업과 `/api/settings` 저장은 501을 반환하므로 별도 실행 서버/DB가 필요합니다.
