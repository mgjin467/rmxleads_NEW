# Vercel 배포 안내 (500 오류 수정)

이 배포본은 Vercel Root Directory가 `./`(저장소 최상위) 또는 `rmx_leads`인 경우 모두 지원합니다.

권장: Vercel → Project Settings → Build and Deployment → Root Directory를 `./`로 설정하고 저장한 다음 새 배포를 실행하세요. Framework Preset은 Other, Build/Install/Output override는 끕니다.

이번 수정은 `rmx_leads/`를 Root Directory로 잡았을 때도 `api/index.py`, `vercel.json`, Flask가 포함된 `requirements.txt`가 인식되도록 구성한 것입니다.

오류 재발 시 배포 페이지에서 Logs 중 **Runtime Logs**를 확인하세요. Build Logs의 `Deployment completed`는 실행 성공을 보장하지 않습니다.

구글 인증 환경변수: `GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT` (JSON 전체).

주의: 웹 화면/조회 API용 배포입니다. `/api/run`의 백그라운드 수집, `/api/settings` 영구 저장은 Vercel 함수에서 지원되지 않도록 설정되어 있습니다.
