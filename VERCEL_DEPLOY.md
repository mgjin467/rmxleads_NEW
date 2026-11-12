# 배포 안내

1. ZIP 압축을 풀고 내부 **파일과 폴더**를 GitHub 저장소의 최상위에 덮어씁니다. 이전 `api/index.py`, `rmx_leads/api/index.py`는 반드시 삭제하세요.
2. Vercel Project Settings → Build and Deployment → Root Directory를 `./`로 설정하는 것을 권장합니다. 만약 `rmx_leads`로 유지해도 그 폴더에 `app.py`가 있어 동작하도록 구성했습니다.
3. Framework Preset: 자동 감지(Flask). Build Command/Output Directory/Install Command의 Override는 모두 끕니다.
4. 새 커밋을 Production에 배포합니다.
5. `/`는 HTML, `/api/config`는 JSON, `/api/leads`는 데이터 JSON이 나와야 합니다. `/api/leads`는 Google 인증이 없다면 JSON의 `error` 값으로 알려줍니다.

이전 404의 원인: `vercel.json`의 `/(.*)` → `/api/index` Rewrite가 Flask에 `/api/index` 경로로 전달되어 404가 발생했습니다. Flask 앱 자체가 전체 경로를 처리하므로 Rewrite가 필요 없습니다.

**제약:** 이 패치는 화면/GET API 배포를 목표로 합니다. 서버리스에서는 스레드 백그라운드 작업과 영구 로컬 JSON 저장을 보장하지 않습니다.
