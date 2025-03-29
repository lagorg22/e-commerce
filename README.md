# E-Commerce API

A robust RESTful API built with Django REST Framework for an e-commerce platform, featuring user authentication, product management, shopping cart functionality, order processing, and user balance management.

## Features

- **User Management**
  - Registration and authentication with JWT
  - Admin and regular user roles
  - User profile with balance
  - Account deletion and password change functionality

- **Product Management**
  - Product listing, details, creation, update, and deletion
  - Admin-only product management

- **Shopping Cart**
  - Add/remove products from cart
  - Adjust quantities
  - Calculate total amount

- **Order Processing**
  - Create orders from cart
  - Order status tracking
  - Order cancellation with refunds

- **Balance Management**
  - Deposit funds to user balance
  - Automatic payment from balance
  - Refunds to balance
  - Transaction history

## Technology Stack

- **Django & Django REST Framework** - Backend framework
- **Simple JWT** - JWT authentication
- **drf-yasg** - Swagger API documentation
- **Pillow** - Image processing
- **CORS Headers** - Cross-Origin Resource Sharing
- **Django Filter** - Advanced filtering

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lagorg22/e-commerce
   cd e-commerce
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the API**
   - API endpoints: `http://127.0.0.1:8000/`
   - Admin interface: `http://127.0.0.1:8000/admin/`
   - API documentation: `http://127.0.0.1:8000/docs/`

## API Endpoints

### Authentication

- `POST /users/register/` - Register a new user
- `POST /users/register/admin/` - Register an admin user
- `POST /users/login/` - Login and obtain JWT tokens
- `POST /users/logout/` - Logout and invalidate tokens
- `POST /users/password/change/` - Change user password
- `DELETE /users/delete/` - Delete user account

### User Profile & Balance

- `GET /users/profile/` - Get user profile with balance information
- `POST /users/deposit/` - Deposit funds to balance
- `GET /users/transactions/` - View transaction history

### Products

- `GET /products/` - List all products
- `GET /products/{id}/` - Get product details
- `POST /products/` - Create new product (admin only)
- `PUT /products/{id}/` - Update product (admin only)
- `DELETE /products/{id}/` - Delete product (admin only)

### Cart

- `GET /cart/` - View current cart
- `POST /cart/add/` - Add product to cart
- `POST /cart/update/` - Update product quantity
- `DELETE /cart/remove/{id}/` - Remove product from cart
- `DELETE /cart/clear/` - Clear cart

### Orders

- `GET /orders/` - List user orders
- `GET /orders/{id}/` - Get order details
- `POST /orders/create/` - Create new order from cart
- `DELETE /orders/{id}/cancel/` - Cancel order and refund

## Design Considerations

### Architecture

- **Service Layer Architecture**: Business logic is encapsulated in model methods and separate functions
- **DRF ViewSets and APIViews**: Consistent API design patterns
- **Permission-Based Access Control**: Admin vs regular user permissions
- **Atomic Transactions**: Database integrity is maintained with transaction blocks

### Balance Management

- Regular users have a balance for purchasing products
- Admin users do not have a balance (returns null)
- All balance transactions are logged for audit purposes
- Atomicity is ensured during balance operations

### Data Models

- **User**: Extended with UserProfile for balance management
- **Product**: Basic product information
- **Cart & CartItem**: Temporary storage for shopping session
- **Order & OrderItem**: Permanent record of purchases
- **Transaction**: Record of all balance changes
