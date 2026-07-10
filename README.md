# CRM 360 — Customer Intelligence System

<p>
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white"/>
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
</p>

*A modern full-stack Customer Relationship Management (CRM) platform built using Flask, MySQL, JavaScript, and Chart.js.*

<p align="center">
  <img src="Screenshots/02_dashboard.png" alt="CRM 360 Dashboard" width="850"/>
</p>

**CRM 360** is a full-stack Customer Relationship Management (CRM) platform designed to help businesses track customer data, analyze sales KPIs, manage support tickets, and monitor web interactions in real time.

Built with a focus on modern UI/UX (Glassmorphism) and a robust backend architecture, this project serves as a complete, enterprise-level application demonstrating end-to-end full-stack development.

---

## 🚀 Key Features

- **Role-Based Authentication:** Secure login system differentiating between **Admin** (full access) and **Agent** (view-only) roles.
- **Dynamic Dashboard Analytics:** Real-time KPI aggregation (Total Revenue, Customer Growth, Pending Orders) powered by SQL.
- **Customer Management (CRUD):** Add new customers, view detailed 360° profiles (timelines, orders, tickets), update records, and delete customers.
- **Global Smart Search:** Instantly search across the entire database by customer name, phone number, or email.
- **Realistic Data Simulation:** Includes a Python database seeder that generates **1,900+ realistic records** across **10 normalized MySQL tables**.
- **Modern UI/UX:** Responsive dark-themed Glassmorphism interface with smooth animations and interactive Chart.js visualizations.

---

## 📸 Screenshots

<table>
<tr>
<td align="center" width="45%">

### 🔐 Login Page
<img src="Screenshots/01_login.png" width="100%">

</td>

<td width="5%"></td>

<td align="center" width="45%">

### 📊 Dashboard
<img src="Screenshots/02_dashboard.png" width="100%">

</td>
</tr>

<tr>
<td align="center">

### 👥 Customer Management
<img src="Screenshots/03_customers.png" width="100%">

</td>

<td></td>

<td align="center">

### 👤 Customer 360 Profile
<img src="Screenshots/04_customer360.png" width="100%">

</td>
</tr>

<tr>
<td align="center">

### 📦 Orders Management
<img src="Screenshots/05_orders.png" width="100%">

</td>

<td></td>

<td align="center">

### 🎫 Support Tickets
<img src="Screenshots/06_support_tickets.png" width="100%">

</td>
</tr>

<tr>
<td align="center">

### ⭐ Customer Feedback
<img src="Screenshots/07_feedback.png" width="100%">

</td>

<td></td>

<td align="center">

### 📞 Call Logs
<img src="Screenshots/08_call_logs.png" width="100%">

</td>
</tr>

<tr>
<td colspan="3" align="center">

### 🌐 Web Interactions
<br>
<img src="Screenshots/09_web_interactions.png" width="65%">

</td>
</tr>
</table>

---

## 🛠️ Technology Stack

### Frontend
- HTML5 & CSS3
- JavaScript (ES6+, Fetch API)
- Chart.js

### Backend
- Python 3
- Flask (REST API Server)
- Flask-CORS
- python-dotenv

### Database
- MySQL
- mysql-connector-python

---

## 🏗️ Architecture Overview

The system follows a classic Client-Server architecture:

1. **Client (Browser):** Vanilla JavaScript frontend making asynchronous `fetch()` API calls.
2. **Server (Flask):** Python backend exposing REST APIs and handling business logic.
3. **Database (MySQL):** Relational database storing customers, orders, support tickets, call logs, and other CRM data across 10 normalized tables.

---

## ⚙️ Local Setup Instructions

### 1. Prerequisites

- Python 3.10+
- MySQL Server & MySQL Workbench (or XAMPP)
- VS Code (with Live Server extension)

### 2. Database Setup

Create the database:

```sql
CREATE DATABASE crm360_db;
```

Run the SQL scripts provided in the `Database/` folder to create all required tables.

### 3. Backend Configuration

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside the `Backend/` folder:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=crm360_db
```

Generate users and sample data:

```bash
python create_users.py
python seed_data.py
```

Start the Flask server:

```bash
python app.py
```

The backend will run at:

```
http://localhost:5000
```

### 4. Frontend Launch

- Open the project in VS Code.
- Right-click `Frontend/login.html`.
- Select **Open with Live Server**.

Login using:

**Username:** `admin`

**Password:** `admin123`

---

## 🚀 Future Enhancements

- JWT-based authentication
- Email notifications for support tickets
- Export reports to PDF and Excel
- Docker containerization
- Cloud database deployment
- AI-powered customer insights and recommendations

---

## 📝 License

This project was built for educational and portfolio demonstration purposes. Feel free to fork, explore, and modify it for learning purposes.

---

## 👨‍💻 Author

**Saksham Tiwari**

Built as a full-stack portfolio project for learning and demonstrating backend development, database design, and frontend integration.
