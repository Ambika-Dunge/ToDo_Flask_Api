# To‑Do Pro — Flask REST API + Attractive UI

A clean, fully‑runnable To‑Do list REST API built with **Flask**, with a sleek UI.
Data is kept in memory while the app runs and is also persisted to `tasks.json`
so your tasks survive restarts.

---

## Features
- Endpoints:
  - `POST /tasks` → Add a new task (fields: `title`, optional `due_date` `YYYY-MM-DD`)
  - `GET /tasks` → Get all tasks
  - `GET /tasks/{id}` → Get a single task by ID
  - `PUT /tasks/{id}` → Update task (any of `title`, `due_date`, `completed`)
  - `DELETE /tasks/{id}` → Delete a task
- JSON responses with proper HTTP status codes
- Error handling (JSON 4xx/5xx)
- In‑memory list + JSON file persistence (`tasks.json`)
- Pretty UI served at `/` (Tailwind + Poppins font)

---

## Quickstart

### 1) Create and activate a virtual environment (optional but recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install requirements
```bash
pip install -r requirements.txt
```

### 3) Run the server
```bash
python app.py
```
Server will start at `http://127.0.0.1:5000/`

- Visit `http://127.0.0.1:5000/` for the **UI**
- API base URL is `http://127.0.0.1:5000`

> The file `tasks.json` is created/updated automatically to persist tasks.

---

## API Reference & Postman Examples

### 1) POST /tasks — Create a task
**Request Body (JSON)**
```json
{
  "title": "Finish Flask project",
  "due_date": "2025-08-31"
}
```
**cURL**
```bash
curl -X POST http://127.0.0.1:5000/tasks   -H "Content-Type: application/json"   -d '{ "title":"Finish Flask project", "due_date":"2025-08-31" }'
```
**Responses**
- `201 Created` with the created task JSON
- `400 Bad Request` if `title` is missing/empty or `due_date` invalid

### 2) GET /tasks — List all tasks
**cURL**
```bash
curl http://127.0.0.1:5000/tasks
```

### 3) GET /tasks/{id} — Get by ID
**cURL**
```bash
curl http://127.0.0.1:5000/tasks/1
```

### 4) PUT /tasks/{id} — Update fields
**Request Body (any subset)**
```json
{
  "title": "Finish Flask project (v2)",
  "due_date": "2025-09-05",
  "completed": true
}
```
**cURL**
```bash
curl -X PUT http://127.0.0.1:5000/tasks/1   -H "Content-Type: application/json"   -d '{ "title":"Finish Flask project (v2)", "due_date":"2025-09-05", "completed":true }'
```
**Responses**
- `200 OK` with updated task
- `400 Bad Request` if invalid fields
- `404 Not Found` if ID doesn’t exist

### 5) DELETE /tasks/{id} — Delete
**cURL**
```bash
curl -X DELETE http://127.0.0.1:5000/tasks/1 -i
```
**Responses**
- `204 No Content` on success
- `404 Not Found` if missing

---

## Postman Collection
Import `ToDoPro.postman_collection.json` into Postman. It includes sample requests for all endpoints.

---

## How to connect to a real database later

### Option A: SQLite with SQLAlchemy (lightweight, file‑based)
1. Install:
   ```bash
   pip install SQLAlchemy
   ```
2. Create a `models.py` with a `Task` model and use a SQLite URI like:
   ```python
   from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
   from sqlalchemy.orm import declarative_base, sessionmaker

   Base = declarative_base()

   class Task(Base):
       __tablename__ = "tasks"
       id = Column(Integer, primary_key=True, autoincrement=True)
       title = Column(String(255), nullable=False)
       completed = Column(Boolean, default=False, nullable=False)
       due_date = Column(Date, nullable=True)

   engine = create_engine("sqlite:///todo.db", echo=False, future=True)
   SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
   Base.metadata.create_all(engine)
   ```
3. Replace in‑memory list with DB queries using sessions (CRUD with SQLAlchemy).

### Option B: PostgreSQL with SQLAlchemy (production‑friendly)
1. Install:
   ```bash
   pip install "SQLAlchemy[postgresql]" psycopg2-binary
   ```
2. Use a Postgres URI:
   ```python
   engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/tododb")
   ```
3. Keep the same ORM `Task` model and swap only the connection string. Migrations can be managed with **Alembic**:
   ```bash
   pip install alembic
   alembic init migrations
   ```

**Controller changes**: CRUD handlers will query the DB session instead of the in‑memory list. You’ll still return the same JSON shapes, so the UI remains unchanged.

---

## Project Structure
```
todo-flask-api-ui/
├─ app.py
├─ requirements.txt
├─ tasks.json
├─ templates/
│  └─ index.html
└─ static/
   └─ style.css
```

---

## Notes
- This project runs **entirely locally**. Tailwind and Google Fonts are loaded via CDN for convenience.
- If you plan to deploy, you should pin dependencies and run using a production server (e.g., `gunicorn` or `waitress`).

Enjoy building!
