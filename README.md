# 🍽️ Canteen Kiosk Management System

A cloud-enabled web application developed to modernize the food ordering process in college and organizational canteens. The system provides a user-friendly interface for customers to browse menus, place orders, make secure online payments, and receive digital receipts, while administrators can efficiently manage menu items, orders, and customer information.

---

## 📖 Project Overview

The **Canteen Kiosk Management System** is designed to eliminate long queues and improve the efficiency of canteen operations. It provides a digital platform where users can order food online before visiting the canteen, reducing waiting time and enhancing customer satisfaction.

The application is built using **Python Flask** for the backend, **HTML, CSS, Bootstrap, and JavaScript** for the frontend, and **MySQL** for database management. It integrates the **Razorpay Payment Gateway** for secure online transactions and generates QR-code-based digital receipts.

---

## ✨ Features

### User Module

* User Registration and Login
* Secure Authentication
* Browse Food Menu
* Search Food Items
* Add Items to Cart
* Place Food Orders
* Online Payment using Razorpay
* QR Code Receipt Generation
* Order History
* User Profile Management

### Admin Module

* Secure Admin Login
* Dashboard with Order Statistics
* Add, Update, and Delete Menu Items
* Upload Food Images
* Manage Customer Orders
* Update Order Status
* View Registered Users
* Generate Reports

---

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* Bootstrap
* JavaScript

### Backend

* Python
* Flask

### Database

* MySQL
* XAMPP

### Payment Gateway

* Razorpay

### Additional Libraries

* Flask
* mysql-connector-python
* qrcode
* reportlab
* Pillow
* Werkzeug

---

## ☁️ Cloud Computing Concepts Used

* Cloud-Based Application Deployment
* Scalable Web Architecture
* Secure User Authentication
* Cloud Database Connectivity
* Online Payment Integration
* Digital Receipt Generation
* QR Code Generation
* File Upload Management

---

## 📂 Project Structure

```
canteen_kiosk/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── cart.html
│   ├── checkout.html
│   ├── admin_dashboard.html
│   └── ...
│
├── app.py
├── requirements.txt
├── database.sql
└── README.md
```

---

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/sambarajukeerthana/cloud.git
```

### Navigate to the Project Folder

```bash
cd cloud
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Database

1. Install XAMPP.
2. Start Apache and MySQL.
3. Open phpMyAdmin.
4. Create a new database.
5. Import the SQL file.
6. Update database credentials in the Flask application.

### Run the Application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 📸 System Modules

* Home Page
* User Registration
* User Login
* Food Menu
* Shopping Cart
* Checkout
* Online Payment
* QR Code Receipt
* Order History
* Admin Dashboard
* Menu Management
* Order Management

---

## 🔒 Security Features

* Password Authentication
* Session Management
* Secure Payment Processing
* Input Validation
* SQL Injection Prevention
* Protected Admin Panel

---

## 🎯 Objectives

* Digitize canteen operations.
* Reduce customer waiting time.
* Enable secure online food ordering.
* Simplify menu and order management.
* Improve customer experience.
* Support cloud-based deployment.

---

## 🚀 Future Enhancements

* AI-Based Food Recommendation System
* Real-Time Order Tracking
* Push Notifications
* Mobile Application
* Cloud Database Deployment
* AWS Deployment
* Customer Feedback and Ratings
* Analytics Dashboard
* Multi-Canteen Support
* Inventory Management

---

## 👩‍💻 Developed By

**Sambaraju Keerthana**

Master of Computer Applications (MCA)

RV College of Engineering (RVCE)

---

## 📄 License

This project is developed for educational and academic purposes.
