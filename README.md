🛍️ Nadancut – Django E-commerce Web Application

Nadancut is a full-stack e-commerce web application built using Django.
It includes product management, cart functionality, coupon-based discounts, secure Razorpay payment integration, and order management with stock control.

🚀 Features
🔐 User Authentication

Session-based login system

User-specific cart and order history

🛒 Shopping & Cart System

Add to cart with dynamic quantity update

Real-time price calculation

Tax and delivery charge logic

Buy Now functionality

🎟️ Coupon System

Supports percentage and fixed discount coupons

AJAX-based coupon validation

Dynamic price update after applying coupon

Prevents multiple coupon usage

Coupon stored with order details

💳 Razorpay Payment Integration

Dynamic order creation using Razorpay API

Recreates order when coupon modifies price

Secure payment capture handling

Payment verification before saving order

Invoice ID generation

📦 Order Management

Stores order details in database

Saves Razorpay order ID & payment ID

Automatically reduces product stock after successful payment

Saves and manages multiple user addresses

🛠️ Tech Stack

Backend: Django (Python)

Frontend: HTML, Bootstrap, JavaScript, jQuery

Database: SQLite

Payment Gateway: Razorpay

Version Control: Git & GitHub

⚙️ Installation & Setup

Clone the repository:

git clone https://github.com/your-username/nadancut.git
cd nadancut


Create virtual environment:

python -m venv venv


Activate virtual environment:

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Apply migrations:

python manage.py makemigrations
python manage.py migrate


Run the server:

python manage.py runserver

💡 Key Learning Outcomes

Implemented AJAX-based dynamic coupon validation

Integrated Razorpay with dynamic amount handling

Managed decimal-to-paise conversion for payments

Handled secure order capture & verification

Implemented stock management after successful transactions

Built complete end-to-end e-commerce workflow

📌 Future Improvements

Email invoice generation

Order tracking system

Admin dashboard analytics

Product review & rating system

Production deployment (AWS / DigitalOcean)

👨‍💻 Author

Aravind Somanath
Electrical & Electronics Engineering Graduate
Python Backend Developer | Django Developer
