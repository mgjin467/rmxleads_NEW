from app import app

def test_routes():
    client=app.test_client()
    for path in ["/", "/api/leads", "/api/config", "/api/settings", "/api/status"]:
        r=client.get(path)
        assert r.status_code==200, (path, r.status_code, r.data[:200])

def test_vercel_rejects_writes(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    c=app.test_client()
    assert c.post("/api/run").status_code==501
    assert c.post("/api/settings", json={"days_back":10}).status_code==501
