# Finance Dashboard API

A role-based financial records management backend built with **FastAPI** and **PostgreSQL**.

---

## Tech Stack

| Layer        | Technology                         |
|--------------|------------------------------------|
| Framework    | FastAPI                            |
| Database     | PostgreSQL                         |
| ORM          | SQLAlchemy 2.0                     |
| Migrations   | Alembic                            |
| Auth         | JWT (via python-jose + passlib)    |
| Validation   | Pydantic v2                        |
| Server       | Uvicorn                            |

---

## Project Structure

```
finance-backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py          # Register, login
│   │   │   ├── users.py         # User management (admin)
│   │   │   ├── records.py       # Financial records CRUD
│   │   │   └── dashboard.py     # Summary & insights endpoints
│   │   └── router.py            # Registers all route modules
│   ├── core/
│   │   ├── config.py            # App settings from .env
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── security.py          # Password hashing, JWT utilities
│   │   └── dependencies.py      # Auth guards, role checkers (RBAC)
│   ├── models/
│   │   ├── user.py              # User SQLAlchemy model + UserRole enum
│   │   └── financial_record.py  # FinancialRecord model + RecordType enum
│   ├── schemas/
│   │   ├── user.py              # Pydantic request/response schemas
│   │   ├── financial_record.py  # Record schemas with validation
│   │   └── dashboard.py         # Dashboard response schemas
│   ├── services/
│   │   ├── auth_service.py      # Registration and login logic
│   │   ├── user_service.py      # User management logic
│   │   └── record_service.py    # Record CRUD + ownership checks
│   ├── repositories/
│   │   ├── user_repository.py   # DB queries for users
│   │   └── record_repository.py # DB queries + aggregations for records
│   └── main.py                  # FastAPI app, middleware, startup
├── alembic/                     # Database migration files
├── seed.py                      # Populate DB with demo data
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup Instructions

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd finance-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
```

### 4. Create the PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE finance_db;"
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. (Optional) Seed demo data

```bash
python seed.py
```

This creates three demo users:

| Email              | Password    | Role     |
|--------------------|-------------|----------|
| admin@demo.com     | admin123    | admin    |
| analyst@demo.com   | analyst123  | analyst  |
| viewer@demo.com    | viewer123   | viewer   |

### 7. Start the server

```bash
uvicorn app.main:app --reload
```

API available at: **http://localhost:8000**
Interactive docs: **http://localhost:8000/docs**

---

## API Reference

### Authentication

| Method | Endpoint              | Description                    | Auth Required |
|--------|-----------------------|--------------------------------|---------------|
| POST   | `/api/auth/register`  | Register a new user            | No            |
| POST   | `/api/auth/login`     | Login and receive a JWT token  | No            |

### Users (Admin only)

| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| GET    | `/api/users/me`       | Get current user profile           |
| GET    | `/api/users/`         | List all users                     |
| GET    | `/api/users/{id}`     | Get user by ID                     |
| PATCH  | `/api/users/{id}`     | Update role, name, or active status|
| DELETE | `/api/users/{id}`     | Deactivate a user account          |

### Financial Records

| Method | Endpoint                | Description                            | Min Role  |
|--------|-------------------------|----------------------------------------|-----------|
| POST   | `/api/records/`         | Create a new record                    | analyst   |
| GET    | `/api/records/`         | List records (paginated + filterable)  | viewer    |
| GET    | `/api/records/{id}`     | Get a specific record                  | viewer    |
| PATCH  | `/api/records/{id}`     | Update a record                        | analyst   |
| DELETE | `/api/records/{id}`     | Soft-delete a record                   | analyst   |

**Available filters for `GET /api/records/`:**

| Parameter   | Type   | Example               |
|-------------|--------|-----------------------|
| `type`      | string | `income` or `expense` |
| `category`  | string | `groceries`           |
| `date_from` | date   | `2024-01-01`          |
| `date_to`   | date   | `2024-12-31`          |
| `page`      | int    | `1`                   |
| `page_size` | int    | `20`                  |

### Dashboard

| Method | Endpoint                  | Description                              | Min Role  |
|--------|---------------------------|------------------------------------------|-----------|
| GET    | `/api/dashboard/summary`  | Full summary: totals, trends, categories | viewer    |
| GET    | `/api/dashboard/insights` | Expense ratios, top categories           | analyst   |

---

## Role-Based Access Control

Access control is enforced at the dependency injection layer in `app/core/dependencies.py` using the `RoleChecker` class.

```
viewer   →  read dashboard, read records
analyst  →  viewer + create/update/delete own records + insights
admin    →  analyst + manage all records + manage users
```

The `RoleChecker` is a reusable FastAPI dependency that is attached directly to route definitions:

```python
# Example: only admin can access this route
@router.get("/", dependencies=[Depends(require_admin)])
```

---

## Design Decisions and Assumptions

### Layered Architecture (Routes → Services → Repositories)
Each layer has a single responsibility:
- **Routes** handle HTTP concerns (request parsing, response codes)
- **Services** contain business logic and enforce rules
- **Repositories** contain all database queries

This makes the code easy to test, extend, and maintain independently.

### Soft Delete
Records are never permanently deleted — a `is_deleted` flag is set to `True`. This preserves financial history and is standard practice in financial systems.

### Ownership Check
Analysts can only modify or delete records they created. Admins can modify any record. This is enforced in `FinancialRecordService._check_ownership_or_admin()`.

### Default Role
New users registered via `/api/auth/register` are assigned the `viewer` role by default. An admin must explicitly promote them to `analyst` or `admin` via the user management API.

### JWT Authentication
Tokens are stateless JWTs signed with HS256. The token encodes the user's ID, which is looked up on each request via the `get_current_user` dependency.

### `Base.metadata.create_all` on Startup
For simplicity, tables are created automatically on startup if they don't exist. In a production environment, this should be replaced with Alembic migrations exclusively.

---

## Example: Using the API

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "password": "secret123"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=alice@example.com&password=secret123"

# 3. Use the token (replace TOKEN with the value from step 2)
curl http://localhost:8000/api/dashboard/summary \
  -H "Authorization: Bearer TOKEN"
```
