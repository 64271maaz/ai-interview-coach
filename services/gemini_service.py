import random
from services.llm import generate_text, parse_json


def generate_questions(job_role, num_questions=5, resume_text=""):
    variety_seed = random.randint(1, 10000)

    if resume_text:
        prompt = f"""You are an expert technical interviewer. Generate {num_questions} DIFFERENT and VARIED interview questions for the job role: "{job_role}".

Here is the candidate's resume content:
\"\"\"
{resume_text}
\"\"\"

Base some questions on the candidate's actual skills, projects, and experience mentioned in the resume, and include a mix of technical, HR, behavioral, and problem-solving questions relevant to "{job_role}".
Avoid generic textbook questions. Make them specific, varied, and non-repetitive (session id: {variety_seed}).

Return ONLY a valid JSON array, no extra text, no markdown formatting, in this exact format:
[
  {{"question": "question text here", "type": "technical"}},
  {{"question": "question text here", "type": "hr"}}
]
"""
    else:
        prompt = f"""You are an expert technical interviewer. Generate {num_questions} DIFFERENT and VARIED interview questions for the job role: "{job_role}".

Include a mix of question types: technical, HR, behavioral, and problem-solving.
Avoid generic textbook questions every time. Vary the angle, scenario, and phrasing (session id: {variety_seed}).

Return ONLY a valid JSON array, no extra text, no markdown formatting, in this exact format:
[
  {{"question": "question text here", "type": "technical"}},
  {{"question": "question text here", "type": "hr"}}
]
"""

    raw = generate_text(prompt, temperature=1.0, json_mode=True)
    if raw:
        try:
            questions = parse_json(raw)
            if isinstance(questions, list) and questions:
                return questions
        except Exception as e:
            print("Question JSON parse error:", e)

    # Sab models fail: random fallback questions
    fallback_pool = [
        {"question": f"Tell me about your experience relevant to the {job_role} role.", "type": "hr"},
        {"question": f"What are the key technical skills required for a {job_role}?", "type": "technical"},
        {"question": f"Describe a challenging problem you solved related to {job_role} work.", "type": "problem-solving"},
        {"question": "How do you handle tight deadlines and pressure at work?", "type": "behavioral"},
        {"question": f"Where do you see yourself growing within a {job_role} career path?", "type": "hr"},
        {"question": f"Walk me through how you would approach a new project as a {job_role}.", "type": "technical"},
        {"question": "Describe a time you disagreed with a teammate. How did you resolve it?", "type": "behavioral"},
        {"question": f"What tools or technologies do you consider essential for a {job_role}, and why?", "type": "technical"},
        {"question": "Tell me about a mistake you made at work and what you learned from it.", "type": "behavioral"},
        {"question": f"How would you explain a complex {job_role}-related concept to a non-technical person?", "type": "problem-solving"},
        {"question": "Why do you want to work in this role instead of a related one?", "type": "hr"},
        {"question": f"How do you stay updated with the latest trends in the {job_role} field?", "type": "hr"},
    ]
    return random.sample(fallback_pool, min(num_questions, len(fallback_pool)))