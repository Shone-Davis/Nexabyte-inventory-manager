# nexabyte-inventory-manager
A full-stack B2B inventory
management platform that helps small business teams
track products, monitor stock levels, manage inventory,
and identify low-stock items through a centralized dashboard.

## Live Demo
https://nexabyte-inventory-manager.up.railway.app

***Demo Login:**
- Username: admin
- Password: admin123

## Features
- Secure authentication with password hashing
- Full product management (add, edit, delete)
- Real-time product search
- Low stock alerts and threshold management
- Inventory analytics dashboard
- Modern dark UI
- Responsive layout for desktop and tablet
- Database persistence using SQLAlchemy ORM

## Architecture
- Flask Application Factory Pattern
- Blueprint-based routing structure
- SQLAlchemy ORM models
- Flask-Login authentication and session management
- Environment variable configuration
- Railway deployment pipeline

## Tech Stack
- **Backend:** Python, Flask, SQLAlchemy, Flask-Login
- **Database:** PostgreSQL (Railway) with Flask-Migrate 
- **Frontend:** Tailwind CSS, Jinja2 Templates
- **Deployment:** Railway

## How to Run Locally
```bash
git clone https://github.com/Shone-Davis/nexabyte-inventory-manager
cd nexabyte-inventory-manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
python app.py
```
Visit `http://127.0.0.1:5000`