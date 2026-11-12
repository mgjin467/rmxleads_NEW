"""Vercel Python Function entrypoint for the Flask dashboard."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "rmx_leads"))

from rmx_leads.app import app
