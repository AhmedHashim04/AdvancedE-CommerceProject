# 🛒 Advanced Ecommerce System

A powerful, scalable ecommerce platform built with Django, designed for merchants and customers with advanced features, secure payments, and real-time operations.

---

## 🚀 Technologies Used

- **Python**, **Django**: Core backend and web framework
- **MySQL**: Relational database
- **Redis**: Caching, message broker, background tasks
- **Celery**: Asynchronous task processing
- **Django Channels**: Real-time notifications (WebSockets)
- **Swagger**: API documentation
- **JWT, OAuth2, OTP**: Authentication & security
- **Docker**: Containerization & deployment
- **Pytest**: Automated testing

---

## 🎯 Key Features

### 🧾 Product & Category Management
- Merchants register, manage products, assign tags, categories, brands
- Inventory control with low stock alerts
- Product details: SKU, barcode, descriptions, currency, tax rate
- Media: main image, gallery, video, 360° view
- Product variants: size, color, etc.
- Weight, dimensions, shipping calculations

### 📊 CSV Import/Export
- Bulk product data management via CSV files

### 🛍️ Shopping Cart & Order Management
- Add/remove products, manage cart
- Order form generation, order tracking (Processing → Shipped → Delivered)
- PDF invoice generation

### 💳 Secure Payments
- VISA, MasterCard, AMEX, Meeza, Apple Pay, Google Pay, PayPal, Cash on Delivery

### 🧵 Promotions & Coupons
- Percentage, fixed, buy X get Y, shipping, collection-based discounts
- Usage limits, bulk discount codes
- Comprehensive coupon system

### 💚 Wishlist System
- Save favorite products for later

### 💬 Product Reviews & Ratings
- Customer feedback, ratings, review moderation

### 👤 User Profiles
- Multi-address support
- Guest and registered checkout

### 🔍 Advanced Filtering & Search
- Filter by price, rating, brand, category, color, etc.
- Related products & "Bought Together" suggestions

### 📦 Region-Based Shipping
- Shipping cost calculations by region
- Shipping weight calculations

### 📢 Advertisements System
- Promote products with banners and ads

### 📄 Static Pages
- About, Terms, Privacy, Contact

### 📊 Admin Tools
- Sales dashboard, bulk edits, activity logging
- Discount code management

### 🌐 Multi-Language & Multi-Currency
- Support for multiple languages and currencies

### ⚡ Performance & Security
- Redis caching for products/categories
- JWT/OAuth2 authentication, rate limiting, API security
- Admin activity logging

### 🧪 Testing & Background Tasks
- Pytest-based test coverage
- Background tasks (order notifications, email, etc.) via Celery & Redis

### 💌 Notifications
- Real-time order updates, low stock alerts
- Email notifications (orders, password resets, promotions)

---

## 📦 Getting Started

1. **Clone the repository**
2. **Configure environment variables**
3. **Build and run containers with Docker**
4. **Access the API via Swagger UI**

---

## 🛠️ Testing

- Run automated tests with Pytest for full coverage

---

## 📞 Contact & Support

For issues or support, use the integrated contact system or reach out via provided channels.

---

## 📚 API & Documentation

- Interactive API docs via Swagger
- Secure authentication with JWT, OAuth2, OTP

---

## 📝 License

This project is licensed under the MIT License.
