from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.interview import Interview, Answer

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard')
@login_required
def dashboard_view():
    interviews = Interview.query.filter_by(user_id=current_user.id, status='completed').order_by(Interview.date_taken.desc()).all()

    if interviews:
        avg_score = round(sum(i.overall_score for i in interviews) / len(interviews), 1)
        best_score = max(i.overall_score for i in interviews)
    else:
        avg_score = 0
        best_score = 0

    # Weak topics nikalo: har question_type ka average score calculate karo
    all_answers = Answer.query.join(Interview).filter(Interview.user_id == current_user.id, Interview.status == 'completed').all()

    type_scores = {}
    for ans in all_answers:
        qtype = ans.question_type
        avg = (ans.relevance_score + ans.technical_accuracy_score + ans.communication_score + ans.completeness_score) / 4
        type_scores.setdefault(qtype, []).append(avg)

    weak_topics = []
    for qtype, scores in type_scores.items():
        type_avg = sum(scores) / len(scores)
        if type_avg < 60:  # 60 se kam ko "weak" mana hai
            weak_topics.append((qtype, round(type_avg, 1)))

    weak_topics.sort(key=lambda x: x[1])  # sabse kamzor pehle

    return render_template('dashboard.html',
                            interviews=interviews,
                            avg_score=avg_score,
                            best_score=best_score,
                            weak_topics=weak_topics,
                            total_attempts=len(interviews))