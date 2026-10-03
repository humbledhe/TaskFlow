TaskFlow

«A backend-first task management REST API built with FastAPI, PostgreSQL, and asynchronous SQLAlchemy.»

TaskFlow is a task management API focused on building a clean, maintainable, and production-oriented backend.

The project combines asynchronous database operations, JWT authentication, secure password hashing, email OTP verification, database migrations, custom exceptions, and automated testing.

✨ Features

Authentication & Security

- User registration
- JWT-based authentication
- Access and refresh tokens
- Protected routes
- Secure password hashing with Argon2
- Bearer token authentication
- Authentication-specific exception handling

Email Verification

- Email-based account verification
- One-time password (OTP) verification
- Hashed OTP storage
- OTP expiration
- Verification state tracking
- Asynchronous email delivery

Task Management

- User-owned tasks
- Task creation and management
- Task status handling
- Task priority handling
- Protected task operations

Database

- PostgreSQL
- SQLAlchemy 2.x asynchronous ORM
- Alembic migrations
- Foreign-key relationships
- Separate internal database identifiers and public identifiers

Development

- FastAPI automatic API documentation
- Pydantic validation
- Service-layer architecture
- Custom application exceptions
- Automated tests with pytest
- Test coverage with pytest-cov

🏗️ Architecture

TaskFlow follows a layered backend architecture designed to separate HTTP handling, business logic, persistence, and infrastructure concerns.

                    ┌───────────────┐
                    │    Client     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Routers    │
                    │  HTTP Layer   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Services    │
                    │ Business Logic│
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  SQLAlchemy   │
                    │   Async ORM   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  PostgreSQL   │
                    └───────────────┘

Supporting Components

Authentication
├── Password hashing
├── JWT access tokens
├── JWT refresh tokens
└── Authentication dependencies

Email Verification
├── OTP generation
├── OTP hashing
├── OTP expiration
└── Account verification

Database Management
├── SQLAlchemy
├── Alembic
├── Foreign-key relationships
└── Database migrations

The goal is to avoid putting business logic directly inside route handlers and instead keep each layer responsible for a specific part of the application.

🛠️ Tech Stack

Technology| Purpose
Python 3.14+| Programming language
FastAPI| REST API framework
PostgreSQL| Relational database
SQLAlchemy 2.x| Asynchronous ORM
Alembic| Database migrations
Pydantic| Validation and serialization
Pydantic Settings| Configuration management
PyJWT| JWT authentication
pwdlib + Argon2| Password hashing
aiosmtplib| Asynchronous email delivery
Uvicorn| ASGI server
pytest| Automated testing
pytest-cov| Test coverage
uv| Dependency and environment management

The project configuration and dependencies are defined in "pyproject.toml".

📁 Project Structure

TaskFlow/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── routers/
│   └── main.py
├── migrations/
│   ├── versions/
│   └── ...
├── .gitignore
├── .python-version
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── README.md

The project structure may evolve as new features and infrastructure are added.

🚀 Getting Started

Prerequisites

Make sure you have the following installed:

- Python 3.14+
- PostgreSQL
- "uv"

Check your installed versions:

python --version
uv --version

1. Clone the Repository

git clone https://github.com/humbledhe/TaskFlow.git
cd TaskFlow

2. Install Dependencies

TaskFlow uses "uv" for dependency and environment management.

Install the project dependencies:

uv sync

Install development dependencies:

uv sync --dev

3. Configure the Environment

Create a ".env" file in the project root.

Example:

DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/taskflow

SECRET_KEY=your-secret-key

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-password
SMTP_FROM=your-email@example.com

Use a strong secret key and real credentials for your development environment.

«Important: Never commit your ".env" file or expose credentials in source control.»

🗄️ Database

TaskFlow uses PostgreSQL with SQLAlchemy's asynchronous API.

Apply Existing Migrations

uv run alembic upgrade head

Check Current Migration

uv run alembic current

View Migration History

uv run alembic history

Create a Migration

After modifying your SQLAlchemy models:

uv run alembic revision --autogenerate -m "describe your change"

Then apply the migration:

uv run alembic upgrade head

Roll Back a Migration

uv run alembic downgrade -1

▶️ Running the API

Start the development server with:

uv run uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

📚 API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI

http://127.0.0.1:8000/docs

ReDoc

http://127.0.0.1:8000/redoc

🔐 Authentication Flow

TaskFlow uses JWT-based authentication.

The general authentication flow is:

Client
  │
  ▼
Register
  │
  ▼
Create User
  │
  ├── Hash Password
  │
  └── Send OTP Email
          │
          ▼
      Verify OTP
          │
          ▼
   Verified Account
          │
          ▼
        Login
          │
          ▼
   Issue JWT Tokens
          │
          ▼
  Access Protected Routes

Protected Requests

Authenticated requests include the access token in the "Authorization" header:

Authorization: Bearer <access_token>

🔑 Password Security

Passwords are never stored directly in the database.

TaskFlow uses "pwdlib" with Argon2 for password hashing.

Plain Password
      │
      ▼
    Argon2
      │
      ▼
 Password Hash
      │
      ▼
  PostgreSQL

During authentication, the submitted password is verified against the stored password hash rather than comparing plaintext passwords.

📧 OTP Verification

TaskFlow uses one-time passwords for email verification.

The OTP lifecycle is:

Generate OTP
     │
     ▼
Hash OTP
     │
     ▼
Store Hash + Expiration
     │
     ▼
Send OTP Email
     │
     ▼
User Submits OTP
     │
     ▼
Verify OTP Hash
     │
     ▼
Check Expiration
     │
     ▼
Mark Account as Verified

The plaintext OTP is not stored in the database.

OTP records include an expiration time to prevent old verification codes from being used indefinitely.

🧩 API Design

TaskFlow separates responsibilities across different application layers.

Routers

Responsible for:

- Handling HTTP requests
- Request validation
- Authentication dependencies
- HTTP responses
- Calling application services

Services

Responsible for:

- Business rules
- Database operations
- Authentication logic
- User operations
- OTP verification
- Task operations

Schemas

Responsible for:

- Request validation
- Response serialization
- API data contracts

Models

Responsible for:

- Database tables
- Relationships
- Persistence mapping

Core

Contains cross-cutting application functionality such as:

- Configuration
- Security
- Authentication utilities
- Application exceptions

🧪 Testing

TaskFlow uses "pytest" for automated testing.

Run Tests

uv run pytest

Run Tests with Coverage

uv run pytest --cov

Testing is part of the development workflow and will be expanded as the application grows.

🧰 Development Commands

Install Dependencies

uv sync

Install Development Dependencies

uv sync --dev

Run Development Server

uv run uvicorn app.main:app --reload

Run Tests

uv run pytest

Run Tests with Coverage

uv run pytest --cov

Create Migration

uv run alembic revision --autogenerate -m "migration message"

Apply Migrations

uv run alembic upgrade head

Roll Back Migration

uv run alembic downgrade -1

🔒 Security Considerations

TaskFlow currently includes:

- Password hashing with Argon2
- JWT-based authentication
- Hashed OTP storage
- OTP expiration
- Protected resources
- Environment-based configuration
- Parameterized database queries through SQLAlchemy

For production deployment, additional security and infrastructure measures should be considered, including:

- HTTPS
- Secure secret management
- Database access controls
- Email infrastructure
- Rate limiting
- Logging
- Monitoring
- Token revocation or rotation
- Production-grade deployment configuration

🗺️ Roadmap

The project is actively evolving. Planned improvements include:

- [ ] Complete authentication flow
- [ ] Complete email verification flow
- [ ] Password reset
- [ ] Token revocation / rotation
- [ ] Task filtering
- [ ] Task pagination
- [ ] Task search
- [ ] Task sorting
- [ ] Due dates and reminders
- [ ] Background task processing
- [ ] Redis integration
- [ ] More comprehensive test coverage
- [ ] API rate limiting
- [ ] Production deployment configuration
- [ ] CI/CD
- [ ] API versioning

🎯 Project Goals

TaskFlow is intended to go beyond a basic CRUD application.

The project focuses on learning and applying:

- REST API design
- Authentication systems
- Business-logic separation
- Asynchronous Python
- Relational database design
- Database migrations
- Application-level exceptions
- Transactional email
- Automated testing
- Maintainable backend architecture

The primary goal is to understand not only how individual components work, but also how they interact within a real backend application.

📌 Project Status

Status: 🚧 Active Development

Current Version: "0.1.0"

TaskFlow is currently a learning and development project, with additional authentication, task-management, infrastructure, testing, and production-readiness features planned.

📄 License

No license has been specified for this project yet.

👨‍💻 Author

Built by Prosper.

GitHub: "@humbledhe" (https://github.com/humbledhe)