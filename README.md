# 🎓 AI Attendance Assistant

An AI-powered attendance management system built using Flask, SQLite, and Groq AI. The application helps manage student attendance records, provides attendance analytics, supports AI-powered conversations, and generates intelligent attendance reports.

---

# 🚀 Features

## 📚 Student Management

✅ Add new students

✅ Delete individual students

✅ Clear all student records

✅ Search students by name

✅ View attendance records in a dashboard

---

## 📊 Attendance Analytics

✅ Calculate attendance percentage automatically

✅ Identify students below 75% attendance

✅ Display highest attendance student

✅ Display lowest attendance student

✅ Attendance status classification:

* Excellent
* Good
* Warning

---

## 🤖 AI Features

✅ AI-powered chatbot using Groq API

✅ Chat history memory

✅ AI-generated attendance reports

✅ Attendance insights and recommendations

---

## 🔄 Multi-Step Workflow

1. Retrieve student attendance data from SQLite database
2. Analyze attendance statistics
3. Send data to AI model
4. Generate intelligent reports and responses

---

# 🛠️ Technologies Used

* Python
* Flask
* SQLite
* HTML
* CSS
* Groq API
* Python Dotenv

---

# 📸 Screenshots

## Dashboard

![Dashboard](screenshots/dashboard.png)

## AI Chatbot

![AI Chatbot](screenshots/chatbot.png)

## AI Attendance Report

![AI Report](screenshots/report.png)

---

# 📦 Installation

## Clone Repository

```bash
git clone <your-repository-url>
cd AI_Attendance_Assistant
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Create .env File

Create a file named `.env`

```env
GROQ_API_KEY=your_groq_api_key
```

## Run Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 📁 Project Structure

```text
AI_Attendance_Assistant/
│
├── app.py
├── database.py
├── groq_helper.py
├── requirements.txt
├── README.md
├── .env.example
├── templates/
│   └── index.html
└── screenshots/
```

---

# 🔐 Environment Variables

Example `.env.example`

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

⚠️ Never upload your real API key to GitHub.

---

# 🎯 Future Improvements

* Export reports to PDF
* Export attendance data to Excel
* Face Recognition Attendance Integration
* Attendance Trend Charts
* Student Edit Functionality
* Admin Authentication

---

# 👨‍💻 Author

**Mohd Shahnawaz**
If you want to login user name (mohd123)
                          password(111)
AI Attendance Assistant – Internship Project
