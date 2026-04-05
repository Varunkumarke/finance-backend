# Finance Dashboard API

A backend REST API for a finance dashboard system, built with **FastAPI** and **PostgreSQL**.

---

## Tech Stack

- **FastAPI** — Python web framework
- **PostgreSQL** — Relational database
- **SQLAlchemy** — ORM for database models
- **Alembic** — Database migrations
- **JWT (python-jose)** — Authentication tokens
- **Pydantic v2** — Request/response validation
- **Uvicorn** — ASGI server

---

## Project Structure

finance-backend/
├── app/
│   ├── api/routes/        # auth, users, records, dashboard
│   ├── core/              # config, database, security, role guards
│   ├── models/            # SQLAlchemy table definitions
│   ├── schemas/           # Pydantic validation schemas
│   ├── services/          # Business logic
│   ├── repositories/      # Database queries
│   └── main.py
├── alembic/               # Migration files
├── seed.py                # Demo data script
├── requirements.txt
└── .env.example


---

## Setup

### 1. Clone the repo

git clone https://github.com/Varunkumarke/finance-backend
cd finance-backend

### 2. Install dependencies

pip install -r requirements.txt


### 3. Create a `.env` file

cp .env.example .env

Update the `DATABASE_URL` with your PostgreSQL credentials:
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/finance_db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256


### 4. Create the database
```bash
psql -U postgres -c "CREATE DATABASE finance_db;"
```

### 5. Run migrations
```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### 6. Seed demo data
```bash
python seed.py
```

Demo users created:

| Email | Password | Role |
|---|---|---|
| admin@demo.com | admin123 | admin |
| analyst@demo.com | analyst123 | analyst |
| viewer@demo.com | viewer123 | viewer |

### 7. Start the server
```bash
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive API documentation.

---

## Roles & Access

| Role | What they can do |
|---|---|
| `viewer` | View records and dashboard |
| `analyst` | View + create/edit/delete their own records |
| `admin` | Full access including user management |

Role checking is handled via a `RoleChecker` dependency in `app/core/dependencies.py`.


## Design Decisions

- **Layered architecture** — Routes → Services → Repositories. Each layer has one responsibility.
- **Soft delete** — Records are never permanently deleted, just flagged as `is_deleted = True`. Important for financial data history.
- **Ownership check** — Analysts can only edit/delete records they created. Admins can edit any record.
- **Default role** — New users get `viewer` role. Only admins can promote users.
- **JWT auth** — Stateless tokens signed with HS256. User ID is stored in the token payload.

