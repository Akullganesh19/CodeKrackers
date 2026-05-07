from backend.main import app

# This is the entry point for Vercel to run the FastAPI app as a serverless function.
# Vercel looks for 'app' or 'handler' in the api/ directory.
handler = app
