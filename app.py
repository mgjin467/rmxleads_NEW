"""Vercel Flask auto-discovery entrypoint (repository root)."""
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / "rmx_leads"
sys.path.insert(0, str(APP_DIR))
from rmx_leads.app import app
