# 🎓 AI Attendance Assistant

An AI-powered attendance management system with analytics, chatbot support, memory features, and automated report generation.

## 🚀 Features

### Core Features
- ✅ User authentication with secure login and registration.
- ✅ Add, delete, and update student records.
- ✅ Search students quickly.
- ✅ Dashboard with real-time attendance statistics.
- ✅ Automatic alerts for students below 75% attendance.

### AI Features
- 🤖 AI chatbot to answer questions about attendance data.
- 📜 Persistent chat history for memory and context.
- 📄 AI-generated attendance reports and analysis.

### Export Features
- 📊 Export attendance data to Excel (`.xlsx`).
- 📄 Export attendance reports to PDF (`.pdf`).

### New Features
- 🔄 Update attendance by modifying present and total days.
- 📧 Email alerts when attendance falls below 75%.

## 🛠️ Technologies Used

- **Backend:** Flask (Python)
- **AI API:** Groq AI
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap
- **Export:** Pandas, ReportLab
- **Authentication:** Flask-Login

## 📦 Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd AI_Attendance_Assistant
```

2. Install dependencies:
```bash
pip install flask flask-login pandas openpyxl reportlab groq
```

3. Set your Groq API key:
```powershell
$env:GROQ_API_KEY="your_new_key_here"
```

4. Set up the database:
```bash
python setup_database.py
```

5. Run the app:
```bash
python app.py
```

6. Login credentials:
- Username: `admin`
- Password: `admin123`

## 📁 Project Structure
```bash
AI_Attendance_Assistant/
├── app.py
├── database.py
├── groq_helper.py
├── test_ai.py
├── templates/
│   ├── index.html
│   ├── login.html
│   └── register.html
├── README.md
└── .gitignore
```

## 🔐 Environment Variables

Create a `.env.example` file like this:

```env
GROQ_API_KEY=your_key_here
```

Do not commit your real API key to the repository.