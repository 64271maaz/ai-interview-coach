from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.user import db
from models.interview import Interview, Answer
from services.gemini_service import generate_questions
from services.evaluation_service import evaluate_all_answers
from services.resume_service import extract_resume_text

interview = Blueprint('interview', __name__)


@interview.route('/select-role')
@login_required
def select_role():
    return render_template('select_role.html')


@interview.route('/start-interview', methods=['POST'])
@login_required
def start_interview():
    job_role = request.form.get('job_role')

    if not job_role:
        flash('Please select a job role.')
        return redirect(url_for('interview.select_role'))

    # Resume file check karo (optional hai)
    resume_text = ""
    resume_was_used = False

    resume_file = request.files.get('resume')
    if resume_file and resume_file.filename != '':
        resume_text = extract_resume_text(resume_file)
        if resume_text:
            resume_was_used = True

    new_interview = Interview(
        user_id=current_user.id,
        job_role=job_role,
        status='in_progress',
        resume_used=resume_was_used
    )
    db.session.add(new_interview)
    db.session.commit()

    questions = generate_questions(job_role, num_questions=5, resume_text=resume_text)

    for q in questions:
        answer_entry = Answer(
            interview_id=new_interview.id,
            question_text=q.get('question', ''),
            question_type=q.get('type', 'general')
        )
        db.session.add(answer_entry)

    db.session.commit()

    return redirect(url_for('interview.take_interview', interview_id=new_interview.id))


@interview.route('/interview/<int:interview_id>')
@login_required
def take_interview(interview_id):
    interview_obj = Interview.query.get_or_404(interview_id)

    if interview_obj.user_id != current_user.id:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard.dashboard_view'))

    answers = Answer.query.filter_by(interview_id=interview_id).all()
    return render_template('interview.html', interview=interview_obj, answers=answers)


@interview.route('/interview/<int:interview_id>/submit', methods=['POST'])
@login_required
def submit_answers(interview_id):
    interview_obj = Interview.query.get_or_404(interview_id)

    if interview_obj.user_id != current_user.id:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard.dashboard_view'))

    answers = Answer.query.filter_by(interview_id=interview_id).all()

    # Pehle sab jawab collect karo, ek list mein
    qa_list = []
    for answer in answers:
        submitted_text = request.form.get(f'answer_{answer.id}', '').strip()
        answer.user_answer = submitted_text
        qa_list.append({
            "id": answer.id,
            "question": answer.question_text,
            "type": answer.question_type,
            "answer": submitted_text
        })

    # Sab answers ko EK hi Gemini call mein evaluate karwao (quota bachane ke liye)
    results = evaluate_all_answers(interview_obj.job_role, qa_list)

    total_relevance = 0
    total_technical = 0
    total_communication = 0
    total_completeness = 0

    for answer in answers:
        result = results.get(answer.id, {})

        answer.relevance_score = result.get('relevance_score', 0)
        answer.technical_accuracy_score = result.get('technical_accuracy_score', 0)
        answer.communication_score = result.get('communication_score', 0)
        answer.completeness_score = result.get('completeness_score', 0)
        answer.strengths = result.get('strengths', '')
        answer.weaknesses = result.get('weaknesses', '')
        answer.missing_concepts = result.get('missing_concepts', '')

        total_relevance += answer.relevance_score
        total_technical += answer.technical_accuracy_score
        total_communication += answer.communication_score
        total_completeness += answer.completeness_score

    count = len(answers) if answers else 1

    avg_relevance = total_relevance / count
    avg_technical = total_technical / count
    avg_communication = total_communication / count
    avg_completeness = total_completeness / count

    interview_obj.technical_score = round(avg_technical, 1)
    interview_obj.communication_score = round(avg_communication, 1)
    interview_obj.overall_score = round(
        (avg_relevance + avg_technical + avg_communication + avg_completeness) / 4, 1
    )
    interview_obj.confidence_score = round((avg_completeness + avg_communication) / 2, 1)
    interview_obj.status = 'completed'

    db.session.commit()

    flash('Interview evaluated successfully!')
    return redirect(url_for('interview.view_report', interview_id=interview_obj.id))


@interview.route('/interview/<int:interview_id>/report')
@login_required
def view_report(interview_id):
    interview_obj = Interview.query.get_or_404(interview_id)

    if interview_obj.user_id != current_user.id:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard.dashboard_view'))

    answers = Answer.query.filter_by(interview_id=interview_id).all()
    return render_template('report.html', interview=interview_obj, answers=answers)