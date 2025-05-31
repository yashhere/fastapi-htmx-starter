# FastAPI HTMX Starter Template

A modern, production-ready starter template for building web applications with FastAPI, HTMX, and TailwindCSS.

## 🚀 Features

- **FastAPI** - Modern, fast web framework with automatic API documentation
- **HTMX** - Dynamic frontend interactions without heavy JavaScript
- **TailwindCSS** - Utility-first CSS framework for rapid UI development
- **Authentication** - Complete user system with fastapi-users
- **Database** - SQLAlchemy 2.0 with async support and Alembic migrations
- **Testing** - Pytest setup with async support
- **Development Tools** - Code formatting, linting, and type checking

## 📋 Requirements

- Python 3.11+
- uv (recommended) or pip for package management

## 🛠️ Quick Start

### 1. Clone or Copy the Template

Copy the `starter-template` directory to your desired location:

```bash
cp -r starter-template my-new-project
cd my-new-project
```

### 2. Set Up Environment

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Generate a secure secret key
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
```

### 4. Initialize Database

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
# Using CLI command
python -m app.cli serve

# Or directly with uvicorn
uvicorn app.main:app --reload
```

Visit http://localhost:8000 to see your application!

## 📁 Project Structure

```
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core configuration
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── static/       # Static files
│   ├── templates/    # Jinja2 templates
│   └── tests/        # Test files
├── alembic/          # Database migrations
├── scripts/          # Utility scripts
├── .env.example      # Environment template
├── alembic.ini       # Alembic configuration
├── pyproject.toml    # Project configuration
└── README.md         # This file
```

## 🎯 What's Included

### Authentication System
- User registration and login
- Cookie-based sessions with JWT
- Protected routes and user management
- Dynamic navigation updates

### CRUD Example
- Complete items management system
- Search and pagination
- Inline editing with HTMX
- Real-time updates without page refresh

### Modern Frontend
- HTMX for dynamic interactions
- TailwindCSS for styling
- Responsive design
- Loading states and error handling

### Development Tools
- Code formatting with Black
- Linting with Ruff
- Type checking with MyPy
- Testing with Pytest
- Database migrations with Alembic

## 🔧 Development Commands

```bash
# Start development server
python -m app.cli serve

# Run tests
python -m app.cli test

# Lint code
python -m app.cli lint

# Format code
python -m app.cli format

# Type checking
python -m app.cli check-types
```

## 🗄️ Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1
```

## 🧪 Testing

The template includes a complete testing setup:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_main.py -v
```

## 📦 Customization

### Adding New Models

1. Create model in `app/models/`
2. Add relationships if needed
3. Create corresponding schemas in `app/schemas/`
4. Generate migration: `alembic revision --autogenerate -m "Add new model"`
5. Apply migration: `alembic upgrade head`

### Adding New Routes

1. Create router in `app/api/`
2. Add route handlers
3. Include router in `app/main.py`
4. Create templates if needed

### Frontend Customization

- Modify `app/templates/base.jinja2` for layout changes
- Add custom CSS in `app/static/css/`
- Add JavaScript in `app/static/js/`
- Use HTMX attributes for dynamic behavior

## 🚀 Deployment

### Environment Variables

Set these in production:

```bash
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

### Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv pip install --system -e .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📖 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HTMX Documentation](https://htmx.org/docs/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## 🤝 Contributing

This is a starter template. Feel free to customize it for your needs!

## 📄 License

This template is provided as-is for educational and development purposes.
