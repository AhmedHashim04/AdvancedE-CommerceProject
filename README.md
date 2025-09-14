<!-- 
                          ->give him difult shipping plan 
                         |
Seller -- upload product |
                         |
                          -> change shipping plan

 -->

# 🛒 Advanced Ecommerce System
A powerful, scalable ecommerce platform built with Django, designed for multi-seller marketplaces. Each seller can register, manage their own dedicated dashboard, and access personalized tools for products, orders, shipping, and analytics. The system supports multi-shipping company integration, enabling sellers to offer various delivery options with flexible pricing, regions, and timeframes. Customers can select the shipping plan that suits them, with automatic cost adjustments for excess weight.

The platform features advanced coupon and discount systems, multiple payment methods, product reviews and ratings, auto-generated order forms, and real-time notifications for customers, sellers, and shipping companies. Sellers can enable multiple shipping providers, set custom shipping plans, and define pricing rules based on region, weight, and delivery time. Customers benefit from a seamless shopping experience, choosing the best shipping and payment options, applying coupons, and leaving reviews.

Additionally, the system includes an advertisements module, allowing sellers to promote products through banners and ads for increased visibility and sales.
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

### 🧾 Multi-Seller Marketplace
- Sellers register and manage their own dashboard
- Personalized management for products, orders, shipping, and analytics
- Seller-specific notifications and statistics

### 🚚 Multi-Shipping Company Integration
- Sellers can enable multiple shipping companies
- Custom shipping plans: flexible pricing, regions, delivery times
- Automatic cost calculation for excess weight
- Customers choose preferred shipping plan during checkout
- Real-time notifications for shipping companies

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
- Auto-generated order forms for each product
- Order tracking (Processing → Shipped → Delivered)
- PDF invoice generation

### 💳 Secure Payments
- VISA, MasterCard, AMEX, Meeza, Apple Pay, Google Pay, PayPal, Cash on Delivery
- Multiple payment gateways for flexibility

### 🧵 Promotions & Coupons
- Advanced coupon system: percentage, fixed, buy X get Y, shipping, collection-based discounts
- Usage limits, bulk discount codes
- Shipping coupons and region-based discounts

### 💚 Wishlist System
- Save favorite products for later

### 💬 Product Reviews & Ratings
- Customers can leave reviews and ratings on products
- Review moderation by sellers
- Ratings displayed on product pages

### 👤 User Profiles
- Multi-address support
- Guest and registered checkout

### 🔍 Advanced Filtering & Search
- Filter by price, rating, brand, category, color, etc.
- Related products & "Bought Together" suggestions

### 📦 Region-Based Shipping
- Shipping cost calculations by region
- Shipping weight calculations
- Sellers define shipping zones and pricing

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

### 💌 Real-Time Notifications
- Instant updates for customers, sellers, and shipping companies
- Order status changes, low stock alerts, promotions, and more
- Email notifications for orders, password resets, and marketing

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
