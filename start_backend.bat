@echo off
echo Starting VSDP FastAPI Backend...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
