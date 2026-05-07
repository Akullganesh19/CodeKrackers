import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import app

# Vercel needs 'app' to be in the module
# The file is api/index.py, so the URL will be /api
# We use rewrites to map /api/(.*) to this file
