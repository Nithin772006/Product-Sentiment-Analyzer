# Development Guide

## Local Services

Run backend and frontend in separate terminals.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Code Standards

- Keep API routes thin.
- Put request handling in controllers.
- Put reusable business logic in services.
- Keep React pages focused on route-level layout.
- Move reusable UI into `frontend/src/components`.
- Do not commit `.env`, build output, virtual environments, or `node_modules`.

## Docker Readiness

The repository includes `.dockerignore` and environment examples. Dockerfiles and Compose files should be added only after the backend and frontend startup commands stabilize.
