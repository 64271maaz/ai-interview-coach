from models.user import db
from datetime import datetime

class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    job_role = db.Column(db.String(100), nullable=False)  # e.g. "Data Scientist"
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)

    # Readiness Assessment scores (0-100)
    overall_score = db.Column(db.Float, default=0)
    technical_score = db.Column(db.Float, default=0)
    communication_score = db.Column(db.Float, default=0)
    confidence_score = db.Column(db.Float, default=0)

    status = db.Column(db.String(20), default='in_progress')  # in_progress / completed
    resume_used = db.Column(db.Boolean, default=False)

    # Ek Interview ke kai Answers (one-to-many)
    answers = db.relationship('Answer', backref='interview', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Interview {self.job_role} - User {self.user_id}>'


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)

    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30))  # technical / hr / behavioral / problem_solving

    user_answer = db.Column(db.Text)

    # AI Evaluation ke results
    relevance_score = db.Column(db.Float, default=0)
    technical_accuracy_score = db.Column(db.Float, default=0)
    communication_score = db.Column(db.Float, default=0)
    completeness_score = db.Column(db.Float, default=0)

    strengths = db.Column(db.Text)           # AI ka feedback: strengths
    weaknesses = db.Column(db.Text)          # AI ka feedback: weaknesses
    missing_concepts = db.Column(db.Text)    # AI ka feedback: missing keywords/concepts

    def __repr__(self):
        return f'<Answer for Interview {self.interview_id}>'