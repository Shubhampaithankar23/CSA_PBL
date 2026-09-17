# Secure 3-Tier Web Application

Unit 1 Cloud Security PBL project with a React web tier, FastAPI application tier, and SQLite database tier.

## Run locally

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8001
```

The first startup creates the local database. Set your own account credentials before using the application; credentials are intentionally not documented in this repository.

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The backend runs at `http://127.0.0.1:8001`.

## Security controls
JWT authentication, bcrypt password hashing, backend role authorization, Pydantic input validation, SQLAlchemy ORM, protected APIs, environment-based configuration, and restricted CORS.
