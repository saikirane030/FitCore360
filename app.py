from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
FITCORE_APP = ROOT / "fitcore360_app"
if str(FITCORE_APP) not in sys.path:
    sys.path.insert(0, str(FITCORE_APP))

from app import *
