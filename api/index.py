import sys
import os
from pathlib import Path

# Add the project root to sys.path so 'backend' module can be found
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.main import app

# This is the entry point for Vercel to run the FastAPI app as a serverless function.
handler = app
