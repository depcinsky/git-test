
## Wymagania
- Python 3.10+  
- FastAPI, Uvicorn (`pip install -r requirements.txt`)

## Uruchomienie
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# dane: rozpakuj CSV do ./data lub ustaw zmienną środowiskową:
# $env:DATA_DIR = "C:\sciezka\do\danych"
python -m uvicorn main:app --reload
