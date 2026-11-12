"""Vercel entrypoint when Root Directory is rmx_leads."""
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from app import app
