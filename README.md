🛍️ Nadancut
Full-Stack Django E-Commerce Web Application












📌 Overview

Nadancut is a full-featured e-commerce web application built using Django.
It supports dynamic cart management, coupon-based discounts, Razorpay payment integration, order processing, and stock management — providing a complete end-to-end online shopping experience.

This project demonstrates real-world backend logic implementation including secure payment handling and dynamic price recalculations.

🚀 Core Features
🔐 Authentication System

Session-based login

User-specific cart & orders

Secure checkout flow

🛒 Cart & Checkout System

Add to cart with dynamic quantity selector

Real-time price updates

Tax calculation (18%)

Conditional delivery charge logic

Buy Now functionality

🎟️ Advanced Coupon System

Supports:

Percentage-based discounts (e.g., 50%)

Fixed amount discounts (e.g., ₹100)

AJAX-based coupon validation

Prevents:

Negative totals

Multiple coupon application

Dynamically recreates Razorpay order when coupon applied

Coupon linked to order in database (ForeignKey)

💳 Razorpay Integration

Dynamic order creation

Paise conversion handling (₹ → paise)

Secure payment capture

Handles:

Decimal rounding issues

Order mismatch errors

Payment ID & Order ID stored in database

Invoice ID auto-generated

📦 Order Management

Saves:

User

Address

Product

Quantity

Discounted price

Coupon used

Payment details

Auto stock deduction after successful payment

Prevents stock underflow

🛠️ Tech Stack
Layer	Technology
Backend	Django 5.x
Language	Python 3.12
Frontend	HTML5, Bootstrap 5, JavaScript, jQuery
Database	SQLite
Payment Gateway	Razorpay API
Version Control	Git & GitHub

## 🚀 Installation Guide

```bash
# Clone the repository
git clone https://github.com/aravindnair895/nadancut.git

# Navigate into project folder
cd nadancut

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

🧠 Backend Logic Highlights

Dynamic recalculation of payable amount after coupon

Order recreation in Razorpay when amount changes

Handling:

Float → Integer conversion errors

Capture mismatch issues

Currency validation errors

Secure payment verification before database write

ForeignKey coupon assignment validation

📂 Project Structure (Simplified)

nadancut/
│
├── models.py
├── views.py
├── urls.py
├── templates/
│   ├── buy_now.html
│   ├── cart.html
│   └── shop.html
│
├── static/
├── manage.py

📈 What This Project Demonstrates

✅ Strong Django backend logic
✅ Real-world payment gateway integration
✅ AJAX-based dynamic UI updates
✅ Database integrity management
✅ Error debugging & production-level handling
✅ Full e-commerce workflow implementation

🔮 Future Enhancements

Email invoice system

Order tracking

Admin analytics dashboard

Product reviews & ratings

Deployment on AWS / DigitalOcean

Production-ready PostgreSQL setup

👨‍💻 Author

Aravind Somanath
Python Backend Developer
Electrical & Electronics Engineering Graduate
