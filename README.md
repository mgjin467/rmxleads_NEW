# RMX Leads — Vercel Flask native deployment

This package removes all wildcard rewrites and uses Vercel automatic Flask detection.

- For Vercel Root Directory `./`: use top-level `app.py`.
- For Vercel Root Directory `rmx_leads`: use `rmx_leads/app.py`.
- Set Framework Preset to Flask (auto-detect) and turn off build/output overrides.
- No `api/index.py` is necessary.

Existing data collection thread and local JSON settings cannot reliably persist in Vercel functions.
