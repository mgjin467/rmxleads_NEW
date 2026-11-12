"""Vercel-compatible Flask WSGI entrypoint."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "rmx_leads"))
from rmx_leads.app import app
