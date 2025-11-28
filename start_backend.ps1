$env:PYTHONPATH = "$PWD"
# Load environment variables from backend/.env when starting uvicorn
& ".\.venv_new\Scripts\python.exe" -m uvicorn backend.main:app --reload --port 8000 --env-file "backend/.env"
