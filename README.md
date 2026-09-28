# 🎯 AI-Powered Interview Coach

An AI-driven web application that helps students, fresh graduates, and job seekers prepare for technical and behavioral interviews. The system generates role-specific interview questions using Google's Gemini AI, evaluates candidate answers, and produces a detailed readiness report with actionable feedback.
### Live https://maazkhan55446.pythonanywhere.com

## 📌 Problem Statement

Most students and fresh graduates struggle to prepare effectively for job interviews due to a lack of structured practice and personalized feedback. Traditional mock interviews are time-consuming and not always accessible. This project solves that by providing an on-demand, AI-powered interview coach that simulates real interviews and gives instant, data-driven feedback.

## ✨ Key Features

- **User Authentication** — Secure registration, login, and session management
- **Role-Based Question Generation** — AI-generated technical, HR, behavioral, and problem-solving questions tailored to 7 job roles (Data Scientist, Data Analyst, AI Engineer, ML Engineer, Software Engineer, Frontend Developer, Backend Developer)
- **Resume-Personalized Questions** *(optional)* — Upload a resume (PDF) to get questions tailored to your actual skills and experience
- **AI Answer Evaluation** — Each answer is scored on relevance, technical accuracy, communication, and completeness
- **Readiness Assessment** — Overall readiness score, technical score, communication score, and confidence estimate
- **Feedback System** — AI-generated strengths, weaknesses, and missing concepts per answer
- **Performance Dashboard** — Track previous attempts, average/best scores, and weak topic analysis
- **Skill Gap Analysis** — Identifies which question categories (technical, HR, behavioral, problem-solving) need improvement

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS (custom dark theme), JavaScript |
| Backend | Python, Flask |
| Database | SQLite (via SQLAlchemy ORM) |
| AI Integration | Google Gemini API (`google-genai` SDK) |
| Authentication | Flask-Login, Werkzeug password hashing |
| Resume Parsing | pdfplumber |

## 📂 Project Structure
ai-interview-coach/
├── app.py # Application entry point
├── config.py # Configuration (DB, secret key, API key)
├── models/ # Database models (User, Interview, Answer)
├── routes/ # Flask blueprints (auth, dashboard, interview)
├── services/ # Business logic (Gemini AI, evaluation, resume parsing)
├── templates/ # Jinja2 HTML templates
├── static/css/ # Stylesheets
└── requirements.txt # Python dependencies

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

```bash
# Clone the repository
git clone https://github.com/64271maaz/ai-interview-coach.git
cd ai-interview-coach

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file in the root directory with:
# GEMINI_API_KEY=your_api_key_here
# SECRET_KEY=any_random_secret_string

# Run the application
python app.py
```

The app will be available at `http://127.0.0.1:5000`

## 🧠 How It Works

1. User registers/logs in and selects a target job role
2. (Optional) User uploads their resume for personalized questions
3. Gemini AI generates 5 relevant interview questions
4. User answers each question in text form
5. Gemini AI evaluates all answers in a single batched call (relevance, accuracy, communication, completeness)
6. A readiness report is generated with scores, strengths, weaknesses, and improvement suggestions
7. Dashboard tracks progress across all attempts over time

## 📈 Future Enhancements

- Downloadable PDF reports
- Voice-based answer submission
- Multi-language support
- Admin panel for question bank management
- Migration to PostgreSQL for production deployment

## 👤 Author

Developed as a semester project for BS Data Science.

---
*This project uses the Gemini API for educational purposes as part of a university coursework project.*
