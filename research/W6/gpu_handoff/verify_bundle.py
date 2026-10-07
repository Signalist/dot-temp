"""Verify the current public W6 payload, not an obsolete historical manifest."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/verify_manifest.py'),run_name='__main__')
