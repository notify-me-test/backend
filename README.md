# Backend Setup

## Containerized Development

### Prerequisites
- Docker installed on your machine
- Port 8000 available

### Quick Start with Docker
```bash
# Build the backend container
docker build -t ecommerce-backend .

# Run the backend container
docker run -p 8000:8000 ecommerce-backend
```

The API will be available at `http://localhost:8000/`

### What Happens Automatically
1. **Database Setup**: Migrations run automatically
2. **Sample Data**: Sample products, categories, and reviews are loaded
3. **Server Start**: Django development server starts on port 8000
4. **API Ready**: All endpoints are immediately accessible

### Container Management
```bash
# View running containers
docker ps

# View container logs
docker logs <container_id>

# Stop the container
docker stop <container_id>

# Remove the container
docker rm <container_id>
```

## API Endpoints

### Products
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Get specific product
- `POST /api/products/` - Create new product
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `POST /api/products/{id}/update_stock/` - Update stock quantity
- `GET /api/products/low_stock/` - Get low stock products

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}/` - Get specific category
- `POST /api/categories/` - Create new category
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category

### Reviews
- `GET /api/reviews/` - List all reviews
- `GET /api/reviews/{id}/` - Get specific review
- `POST /api/reviews/` - Create new review
- `PUT /api/reviews/{id}/` - Update review
- `DELETE /api/reviews/{id}/` - Delete review

### Search
- `GET /api/search/?q={query}` - Search products by name/description

## Development Notes

- **Database**: SQLite (development)
- **Authentication**: Currently disabled (AllowAny permissions)
- **CORS**: Enabled for frontend integration
- **Media Files**: Configured for product images
- **Pagination**: 20 items per page by default

## Troubleshooting

### Container Issues
- **Port already in use**: Use different port with `-p 8001:8000`
- **Build fails**: Check Docker logs and ensure all files are present
- **Database errors**: Container will automatically retry migrations