# Backend - E-commerce Application

## Project Overview
This is the **backend** component of a prototype e-commerce application built with Django REST Framework. The application provides APIs for product management, inventory operations, and e-commerce functionality.

## Tech Stack
- **Framework**: Django with Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **API**: RESTful API with JSON responses
- **Testing**: Django's built-in testing framework with comprehensive test coverage
- **Containerization**: Docker with Docker Compose
- **Logging**: Configured API logging in `/logs/api.log`

## Architecture
- **Apps**: Modular Django apps structure with `products` app for core functionality
- **Models**: Product and inventory models with proper relationships
- **Services**: Business logic separated in `/products/services.py`
- **Repositories**: Data access layer in `/products/repositories.py`
- **Views**: API views with proper serialization and validation
- **Testing**: Comprehensive test suite covering models, services, repositories, and views

## Key Features
- Product CRUD operations via REST API
- Inventory management and tracking
- Data validation and serialization
- Error handling and logging
- Sample data loading capabilities
- API documentation and testing endpoints

## Development Setup
- **Port**: 8000 (configured in docker-compose.yml)
- **Database**: SQLite for development (db.sqlite3)
- **Debug Mode**: Enabled for development
- **Admin Interface**: Django admin available at `/admin/`
- **API Endpoints**: RESTful endpoints under `/api/`

## Docker Configuration
- **Development**: `docker compose up -d` starts the Django development server
- **Image**: Python-based container with Django dependencies
- **Volumes**: Source code mounting for hot reload
- **Environment**: DEBUG=True for development
- **Entrypoint**: Custom entrypoint script for database migrations

## Frontend Integration
- Serves REST API for React frontend application
- Frontend runs on port 3000
- CORS configured for cross-origin requests
- JSON API responses for seamless integration

## Project Structure
```
backend/
├── ecommerce/           # Django project settings
│   ├── settings.py      # Configuration
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI application
├── products/            # Main Django app
│   ├── models.py        # Data models
│   ├── views.py         # API views
│   ├── serializers.py   # API serialization
│   ├── services.py      # Business logic
│   ├── repositories.py  # Data access
│   ├── urls.py          # App URL patterns
│   └── tests/           # Comprehensive test suite
├── logs/                # Application logs
├── Dockerfile           # Container definition
├── docker-compose.yml   # Development orchestration
├── requirements.txt     # Python dependencies
├── entrypoint.sh        # Container startup script
└── manage.py            # Django management commands
```

## API Endpoints
- Product listing and CRUD operations
- Inventory management endpoints
- Proper HTTP status codes and error handling
- JSON API responses with appropriate serialization

## Related Components
- **Frontend**: React TypeScript application (separate repository)
- **Shared**: Both frontend and backend use Docker for consistent development environments