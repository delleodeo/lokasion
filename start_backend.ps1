$env:PYTHONPATH = "$PWD"
& ".\.venv_new\Scripts\python.exe" -m uvicorn backend.main:app --reload --port 8000
