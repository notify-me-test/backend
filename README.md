# E-commerce Backend API

A robust Django REST Framework backend for an e-commerce application, built with clean architecture principles and comprehensive testing.

## 🏗️ Project Structure

```
backend/
├── ecommerce/                 # Main Django project configuration
│   ├── settings.py           # Django settings and configuration
│   ├── urls.py               # Main URL routing
│   ├── wsgi.py               # WSGI application entry point
│   └── asgi.py               # ASGI application entry point
├── products/                  # Main application module
│   ├── models.py             # Database models (Product, Category, ProductImage, ProductReview)
│   ├── views.py              # API view sets with dependency injection
│   ├── services.py           # Business logic layer
│   ├── repositories.py       # Data access layer with abstract interfaces
│   ├── serializers.py        # DRF serializers for API responses
│   ├── urls.py               # Application-specific URL routing
│   ├── admin.py              # Django admin configuration
│   ├── apps.py               # Django app configuration
│   └── tests/                # Comprehensive test suite
│       ├── test_models.py    # Model tests
│       ├── test_views.py     # View tests
│       ├── test_services.py  # Service layer tests
│       ├── test_repositories.py # Repository tests
│       └── test_serializers.py # Serializer tests
├── requirements.txt           # Python dependencies
├── manage.py                 # Django management script
├── Dockerfile                # Container configuration
├── docker-compose.yml        # Docker Compose setup
├── entrypoint.sh             # Container startup script
├── sample_data.json          # Initial data for development
└── db.sqlite3                # SQLite database (development)
```

## 🚀 Local Development Setup

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv, or conda)

### Option 1: Local Python Environment

1. **Clone and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Load sample data:**
   ```bash
   python manage.py loaddata sample_data.json
   ```

6. **Start development server:**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000/`

### Option 2: Docker (Recommended)

1. **Build and run with Docker:**
   ```bash
   # Build the container
   docker build -t ecommerce-backend .
   
   # Run the container
   docker run -p 8000:8000 ecommerce-backend
   ```

2. **Or use Docker Compose:**
   ```bash
   docker-compose up --build
   ```

### What Happens Automatically
- Database migrations run automatically
- Sample products, categories, and reviews are loaded
- Django development server starts on port 8000
- All API endpoints become immediately accessible

## 🧪 Running Tests Locally

### Prerequisites
- All dependencies installed (from requirements.txt)
- Virtual environment activated

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Modules
```bash
# Run only model tests
python manage.py test products.tests.test_models

# Run only view tests
python manage.py test products.tests.test_views

# Run only service tests
python manage.py test products.tests.test_services

# Run only repository tests
python manage.py test products.tests.test_repositories
```

### Run Tests with Coverage
```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

### Test Structure
- **Model Tests**: Test database model validation and relationships
- **View Tests**: Test API endpoints and HTTP responses
- **Service Tests**: Test business logic with mocked dependencies
- **Repository Tests**: Test data access layer operations
- **Serializer Tests**: Test data transformation and validation

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products/` | List all products (paginated) |
| `GET` | `/products/{id}/` | Get specific product details |
| `POST` | `/products/` | Create new product |
| `PUT` | `/products/{id}/` | Update existing product |
| `DELETE` | `/products/{id}/` | Delete product |
| `POST` | `/products/{id}/update_stock/` | Update product stock quantity |
| `GET` | `/products/low_stock/` | Get products with low stock |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/categories/` | List all categories |
| `GET` | `/categories/{id}/` | Get specific category details |
| `POST` | `/categories/` | Create new category |
| `PUT` | `/categories/{id}/` | Update existing category |
| `DELETE` | `/categories/{id}/` | Delete category |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/reviews/` | List all product reviews |
| `GET` | `/reviews/{id}/` | Get specific review details |
| `POST` | `/reviews/` | Create new review |
| `PUT` | `/reviews/{id}/` | Update existing review |
| `DELETE` | `/reviews/{id}/` | Delete review |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/search/?q={query}` | Search products by name/description |

## 🏛️ Design Patterns & Architecture

### 1. **Clean Architecture (Layered Architecture)**
- **Models Layer**: Django ORM models for data representation
- **Repository Layer**: Abstract data access interfaces and implementations
- **Service Layer**: Business logic and validation
- **View Layer**: API endpoints and HTTP handling
- **Serializer Layer**: Data transformation and validation

### 2. **Repository Pattern**
- Abstract interfaces (`ProductRepositoryInterface`, `CategoryRepositoryInterface`)
- Concrete implementations (`ProductRepository`, `CategoryRepository`)
- Separation of data access logic from business logic
- Easy to swap implementations (e.g., for testing or different databases)

### 3. **Service Layer Pattern**
- Business logic encapsulation in service classes
- Validation and business rules enforcement
- Transaction management and error handling
- Clean separation from data access and presentation layers

### 4. **Dependency Injection**
- ViewSets accept service dependencies in constructors
- Factory methods provide default implementations
- Easy to inject mock services for testing
- Loose coupling between components

### 5. **Strategy Pattern**
- Different repository implementations can be swapped
- Service classes can work with any repository implementation
- Easy to extend with new data sources or caching strategies

### 6. **Factory Pattern**
- Factory methods in ViewSets for default service creation
- Centralized object creation logic
- Easy to modify object creation behavior

### 7. **Observer Pattern (Django signals)**
- Automatic timestamp updates on model save
- Cascading operations (e.g., category deletion affecting products)

## 🔧 Configuration

### Environment Variables
- `DEBUG`: Django debug mode (default: True)
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Allowed host names
- `CORS_ALLOWED_ORIGINS`: Frontend origins for CORS

### Database
- **Development**: SQLite3 (file-based)
- **Production**: Configurable (PostgreSQL, MySQL, etc.)

### REST Framework Settings
- **Permissions**: AllowAny (development only)
- **Pagination**: PageNumberPagination with 20 items per page
- **Renderers**: JSON only
- **CORS**: Enabled for frontend integration

## 🐳 Docker Configuration

### Container Features
- Python 3.11 slim base image
- Automatic dependency installation
- Database initialization and sample data loading
- Development server startup
- Health checks and error handling

### Port Mapping
- Container port: 8000
- Host port: 8000 (configurable)

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Use different port
docker run -p 8001:8000 ecommerce-backend
# or
python manage.py runserver 8001
```

#### Database Errors
- Container automatically retries migrations
- Check logs: `docker logs <container_id>`
- Reset database: Delete `db.sqlite3` and restart

#### Build Failures
- Ensure all files are present
- Check Docker logs for specific errors
- Verify Python version compatibility

#### Test Failures
- Ensure virtual environment is activated
- Check all dependencies are installed
- Verify database migrations are up to date

### Useful Commands
```bash
# View running containers
docker ps

# View container logs
docker logs <container_id>

# Stop container
docker stop <container_id>

# Remove container
docker rm <container_id>

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

## 📚 Dependencies

### Core Dependencies
- **Django 4.2.7**: Web framework
- **Django REST Framework 3.14.0**: API framework
- **Django CORS Headers 4.3.1**: Cross-origin resource sharing
- **Django Filter 23.3**: Advanced filtering
- **Pillow 10.4.0**: Image processing

### Development Dependencies
- **Coverage 7.3.2**: Test coverage reporting
- **Factory Boy 3.3.0**: Test data generation
- **Python Decouple 3.8**: Environment configuration

## 🔒 Security Notes

- **Development Mode**: Currently configured for development with `DEBUG=True`
- **Authentication**: Disabled for development (AllowAny permissions)
- **CORS**: Configured for localhost:3000 (frontend development)
- **Production**: Update settings for production deployment

## 📈 Performance Features

- **Pagination**: 20 items per page by default
- **Database Optimization**: Efficient queries with Django ORM
- **Image Handling**: Optimized image uploads and storage
- **Caching Ready**: Architecture supports easy caching implementation

## 🚀 Future Enhancements

- Authentication and authorization system
- Rate limiting and API throttling
- Redis caching integration
- Elasticsearch for advanced search
- WebSocket support for real-time updates
- GraphQL API alternative
- Microservices architecture migration