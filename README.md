# auth_app — FastAPI + JWT + role-based access

## Jak uruchomić
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt

# ustaw sekretny klucz (w konsoli, jednorazowo na czas sesji)
export SECRET_KEY="super_secret_key"   # Windows PowerShell: $Env:SECRET_KEY="super_secret_key"

# start
uvicorn main:app --reload
```

## Szybki test (curl)
```bash
# 1) Rejestracja użytkownika-admina (pierwszy raz)
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","roles":["ROLE_ADMIN"]}'

# 2) Logowanie i pobranie tokena
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3) Odpytywanie endpointów chronionych
curl http://127.0.0.1:8000/user_details -H "Authorization: Bearer $TOKEN"
curl http://127.0.0.1:8000/protected -H "Authorization: Bearer $TOKEN"

# 4) Dodanie zwykłego użytkownika (też wymaga roli admina)
curl -X POST http://127.0.0.1:8000/users \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"jan","password":"haslo123","roles":["ROLE_USER"]}'
```

## Plik środowiskowy (.env)
Skopiuj `.env.example` do `.env` i ustaw własny `SECRET_KEY` (nie commituj `.env` do repo).Linux/Mac:
```bash
cp .env.example .env
```
Windows PowerShell:
```powershell
copy .env.example .env
```

## Uruchomienie przez Docker (opcjonalnie)
```bash
docker build -t auth-app .
docker run -e SECRET_KEY=super_secret_key -p 8000:8000 auth-app
```
