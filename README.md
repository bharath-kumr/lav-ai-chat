# Lav - AI Dev Companion

Django + Channels (WebSocket) + JWT + Google Gemini. Chat UI is included (`templates/index.html`).
Local default: SQLite + in-memory channels (no Postgres/Redis needed).

## Run (Windows, Python 3.12)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        (then put your GEMINI_API_KEY inside .env)
python manage.py makemigrations accounts chat
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000 , register, and chat.
Get a free Gemini key: https://aistudio.google.com/apikey
