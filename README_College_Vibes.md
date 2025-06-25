# 🎓 College Vibes

**College Vibes** is a web platform for managing college events and clubs, designed for both administrators and students. Admins can register clubs, and club representatives can post events and manage participants. Students can view, register, and participate in various events.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/balaji78938/college-vibes.git
cd college-vibes
```

### 2. Activate Virtual Environment

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install django

```bash
pip install django
```

### 4. Configure Django Settings

Open `collegevibes/settings.py` and **add your email configuration** for sending notifications:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'  # Use App Password or actual password (not recommended)
```

---

### 5. Configure Twilio for WhatsApp Notifications

Open `collegevibes/views.py` and add your **Twilio credentials**:

```python
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'whatsapp:+14155238886'  # or your approved number
```

---

### 6. Migrate and Run the Server

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Admin Login

Use the default credentials to access the admin dashboard:

- **Username:** `admin`
- **Password:** `admin@123`

After logging in, you can:
- Create club accounts
- Manage student and event data

---

## 👥 User Roles

### Admin
- Login to Django admin dashboard
- Register clubs
- Manage students and events

### Clubs
- Login using credentials provided by Admin
- Post events
- View participant lists

### Students
- Register with roll number and details
- View and register for events
- Receive WhatsApp/email notifications

---

## 📱 Features

- Club and Event Management
- WhatsApp Notifications using Twilio
- Email Services for Notifications
- Admin Panel for Club Control
- Student Dashboard for Event Interaction
- Certificate Generation (planned)

---

## 📌 Note

- Ensure your Gmail account has App Passwords enabled if using Gmail SMTP.
- Make sure Twilio Sandbox is enabled for WhatsApp during development.
- Do **not** commit your credentials to GitHub.

---

## 📄 License

This project is for academic use. Customize and extend as needed.
