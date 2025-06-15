# Django E-commerce Backend

A comprehensive, production-ready e-commerce backend built with Django REST Framework and PostgreSQL. This project follows industry best practices and implements a complete e-commerce solution with modern architecture patterns.

## 🚀 Features

### Core Functionality
- **User Management**: Custom user model with JWT authentication, profiles, and address management
- **Product Catalog**: Categories, brands, products with variants, images, and reviews
- **Shopping Cart**: Session-based cart with wishlist functionality
- **Order Management**: Complete order lifecycle with status tracking
- **Payment Processing**: Multiple payment methods with Stripe integration
- **Shipping**: Flexible shipping methods with tracking and label generation
- **Admin Panel**: Comprehensive Django admin with custom interfaces

### Technical Features
- **RESTful API**: Complete REST API with proper HTTP methods and status codes
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Database**: PostgreSQL with optimized queries and proper indexing
- **File Storage**: Image upload handling with proper validation
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Testing**: Comprehensive test suite with pytest
- **Logging**: Structured logging with different levels
- **CORS**: Cross-origin resource sharing support
- **Pagination**: Efficient pagination for all list endpoints
- **Filtering**: Advanced filtering and search capabilities

## 🏗️ Architecture

This project follows the **Model-View-Template (MVT)** pattern with Django and implements a **modular architecture** using Django apps:

```
ecommerce/
├── ecommerce/              # Main project settings
├── apps/                   # Application modules
│   ├── core/              # Shared utilities and base models
│   ├── users/             # User management and authentication
│   ├── products/          # Product catalog and reviews
│   ├── cart/              # Shopping cart and wishlist
│   ├── orders/            # Order management and coupons
│   ├── payments/          # Payment processing
│   └── shipping/          # Shipping and delivery
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

### MVT Pattern Explanation

**Model (M)**: Represents the data layer
- Database models define the structure and relationships
- Business logic is encapsulated in model methods
- Data validation and constraints are enforced at the model level

**View (V)**: Handles the business logic and API endpoints
- ViewSets and APIViews process HTTP requests
- Serializers handle data validation and transformation
- Permissions control access to resources

**Template (T)**: In this API-only project, serializers serve as the presentation layer
- Serializers format data for API responses
- Different serializers for list, detail, and create/update operations
- Consistent API response structure

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery tasks)
- Git

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd django-ecommerce-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Database
DEBUG=True
SECRET_KEY=your-super-secret-key-here
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Stripe (for payments)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key

# File Storage
MEDIA_URL=/media/
STATIC_URL=/static/

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup

```bash
# Create PostgreSQL database
createdb ecommerce_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Load Sample Data (Optional)

```bash
# Create sample categories and products
python manage.py shell
```

```python
from apps.products.models import Category, Brand
from apps.users.models import User

# Create sample data
category = Category.objects.create(name="Electronics", description="Electronic products")
brand = Brand.objects.create(name="TechBrand", description="Technology brand")
```

### 7. Start Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | User registration |
| POST | `/api/v1/auth/login/` | User login |
| POST | `/api/v1/auth/logout/` | User logout |
| POST | `/api/v1/auth/token/refresh/` | Refresh JWT token |
| GET | `/api/v1/auth/profile/` | Get user profile |
| PUT | `/api/v1/auth/profile/` | Update user profile |

### Product Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products/products/` | List products |
| POST | `/api/v1/products/products/` | Create product (sellers only) |
| GET | `/api/v1/products/products/{slug}/` | Get product details |
| PUT | `/api/v1/products/products/{slug}/` | Update product |
| DELETE | `/api/v1/products/products/{slug}/` | Delete product |
| GET | `/api/v1/products/categories/` | List categories |
| GET | `/api/v1/products/brands/` | List brands |

### Cart Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cart/` | Get user's cart |
| POST | `/api/v1/cart/add/` | Add item to cart |
| PUT | `/api/v1/cart/items/{id}/update/` | Update cart item |
| DELETE | `/api/v1/cart/items/{id}/remove/` | Remove cart item |
| DELETE | `/api/v1/cart/clear/` | Clear cart |

### Order Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/orders/orders/` | List user orders |
| GET | `/api/v1/orders/orders/{id}/` | Get order details |
| POST | `/api/v1/orders/create/` | Create order from cart |
| POST | `/api/v1/orders/orders/{id}/cancel/` | Cancel order |

### Example API Requests

#### User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

#### User Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

#### Add Product to Cart
```bash
curl -X POST http://localhost:8000/api/v1/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "product_id": "product-uuid-here",
    "quantity": 2
  }'
```

## 🔐 JWT Authentication

This project uses JWT (JSON Web Tokens) for authentication with the following flow:

1. **Registration/Login**: User provides credentials and receives access + refresh tokens
2. **API Requests**: Include access token in Authorization header: `Bearer <access_token>`
3. **Token Refresh**: Use refresh token to get new access token when it expires
4. **Logout**: Blacklist refresh token to prevent further use

### Token Lifetimes
- **Access Token**: 15 minutes (configurable)
- **Refresh Token**: 7 days (configurable)

### Security Features
- Automatic token rotation on refresh
- Token blacklisting on logout
- Secure token storage recommendations

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific test file
pytest tests/test_users.py

# Run with verbose output
pytest -v
```

### Test Structure
- **Unit Tests**: Test individual components and models
- **Integration Tests**: Test API endpoints and workflows
- **Fixtures**: Reusable test data setup
- **Factories**: Generate test data with Factory Boy

## 🚀 Deployment

### Production Settings

1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use managed PostgreSQL service
3. **Static Files**: Configure proper static file serving
4. **Security**: Enable HTTPS, set secure headers
5. **Monitoring**: Add logging and monitoring services

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "ecommerce.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📊 Database Schema

### Key Models

**User Model**
- Custom user with email authentication
- User types: customer, seller, admin
- Profile information and preferences

**Product Model**
- Hierarchical categories
- Brand associations
- Variants with attributes
- Image galleries
- Review system

**Order Model**
- Complete order lifecycle
- Address storage (JSON)
- Status tracking
- Payment integration

**Cart Model**
- Session-based shopping cart
- Wishlist functionality
- Quantity management

## 🔧 Configuration

### Django Settings

The project uses environment-based configuration:

- **Development**: Debug enabled, console email backend
- **Production**: Security headers, database optimization
- **Testing**: In-memory database, fast password hashing

### API Configuration

- **Pagination**: 20 items per page (configurable)
- **Filtering**: Django Filter integration
- **Permissions**: Role-based access control
- **Throttling**: Rate limiting for API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages
- Keep functions and classes focused

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the test files for usage examples

## 🔄 Changelog

### Version 1.0.0
- Initial release with complete e-commerce functionality
- JWT authentication system
- Product catalog with reviews
- Shopping cart and wishlist
- Order management system
- Payment processing integration
- Shipping and tracking system
- Comprehensive admin interface
- Full test coverage
- API documentation

---

**Built with ❤️ using Django REST Framework**