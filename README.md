# Lav AI Chat

A real-time AI chat application built with **Django**, **Django Channels (WebSockets)** and the **Google Gemini API**. Users send a message and get an AI reply instantly, without refreshing the page.

![Lav AI Chat screenshot](screenshots/chat.png)

## Features

- Real-time messaging over WebSockets (Django Channels)
- AI responses powered by Google Gemini
- User accounts with a REST API (Django REST Framework)
- Chat history stored in the database
- Simple web interface served from a Django template
- Works locally with SQLite and in-memory channels, with optional PostgreSQL and Redis for production

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Django, Django Channels, Django REST Framework |
| AI | Google Gemini API |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite (default), PostgreSQL (optional) |
| Channel layer | In-memory (default), Redis (optional) |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/bharath-kumr/lav-ai-chat.git
cd lav-ai-chat
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the example file and add your own Gemini API key:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free key at [Google AI Studio](https://aistudio.google.com/apikey). Never commit your `.env` file.

### 5. Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for local development |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `GEMINI_API_KEY` | Your Gemini API key |
| `GEMINI_MODEL` | Gemini model name to use |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Optional PostgreSQL settings |
| `REDIS_URL` | Optional Redis URL for the channel layer |

## Project Structure

```
lav_backend/
├── accounts/        # User accounts and auth API
├── chat/            # Models, WebSocket consumers, Gemini service
├── core/            # Django settings, ASGI/WSGI, URLs
├── templates/       # Chat page (index.html)
├── manage.py
├── requirements.txt
└── .env.example
```

## Author

**Bharath Kumar K**, Python Full-Stack Developer, Chennai, India

GitHub: [@bharath-kumr](https://github.com/bharath-kumr)
