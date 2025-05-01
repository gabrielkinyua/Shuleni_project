from flask import Blueprint, request, jsonify
from app import db
from app.models.assessment import Assessment, Question, Submission, Answer
from app.utils.anti_plagiarism import check_plagiarism
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

bp = Blueprint('assessments', __name__, url_prefix='/api/assessments')



@bp.route('/schools/<int:school_id>/assessments', methods=['POST'])
@jwt_required()
def create_assessment(school_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    duration = data.get('duration')
    questions = data.get('questions', [])

    if not title or not duration:
        return jsonify({'error': 'Title and duration are required'}), 400

    assessment = Assessment(school_id=school_id, title=title, description=description, duration=duration)
    db.session.add(assessment)
    db.session.flush()

    for q in questions:
        question = Question(assessment_id=assessment.id, text=q['text'], question_type=q['type'], max_score=q['max_score'])
        db.session.add(question)

    db.session.commit()
    return jsonify({'id': assessment.id, 'title': assessment.title}), 201

@bp.route('/assessments/<int:assessment_id>', methods=['PUT'])
@jwt_required()
def edit_assessment(assessment_id):
    data = request.get_json()
    assessment = Assessment.query.get_or_404(assessment_id)

    assessment.title = data.get('title', assessment.title)
    assessment.description = data.get('description', assessment.description)
    assessment.duration = data.get('duration', assessment.duration)

    db.session.commit()
    return jsonify({'id': assessment.id, 'title': assessment.title})

@bp.route('/assessments/<int:assessment_id>/start', methods=['POST'])
@jwt_required()
def start_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    student_id = get_jwt_identity()

    submission = Submission(assessment_id=assessment_id, student_id=student_id)
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'submission_id': submission.id,
        'assessment': {'id': assessment.id, 'title': assessment.title, 'duration': assessment.duration},
        'end_time': (datetime.utcnow() + timedelta(minutes=assessment.duration)).isoformat()
    })

@bp.route('/assessments/<int:assessment_id>/submit', methods=['POST'])
@jwt_required()
def submit_assessment(assessment_id):
    data = request.get_json()
    submission_id = data.get('submission_id')
    answers = data.get('answers', [])

    submission = Submission.query.get_or_404(submission_id)
    if submission.assessment_id != assessment_id:
        return jsonify({'error': 'Invalid submission'}), 400

    # Save answers
    for ans in answers:
        answer = Answer(submission_id=submission_id, question_id=ans['question_id'], text=ans['text'])
        db.session.add(answer)

    # Check for plagiarism
    answer_texts = [ans['text'] for ans in answers]
    plagiarism_cases = check_plagiarism(answer_texts)
    if plagiarism_cases:
        submission.plagiarism_flag = True

    db.session.commit()
    return jsonify({'submission_id': submission.id, 'plagiarism_flag': submission.plagiarism_flag})

@bp.route('/assessments/<int:assessment_id>/results', methods=['GET'])
@jwt_required()
def view_results(assessment_id):
    submission = Submission.query.filter_by(assessment_id=assessment_id, student_id=get_jwt_identity()).first_or_404()
    answers = Answer.query.filter_by(submission_id=submission.id).all()

    return jsonify({
        'submission_id': submission.id,
        'score': submission.score,
        'plagiarism_flag': submission.plagiarism_flag,
        'answers': [{'question_id': ans.question_id, 'text': ans.text, 'score': ans.score} for ans in answers]
    })