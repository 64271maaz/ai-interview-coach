from google import genai
from google.genai import types
from config import Config
import json
import time
import random

client = genai.Client(api_key=Config.GEMINI_API_KEY)

def generate_questions(job_role, num_questions=5, resume_text=""):
    """
    Diye gaye job role ke hisaab se interview questions generate karta hai.
    Har baar alag questions aayen is liye variety instructions aur higher temperature use ki hai.
    """

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
Avoid generic textbook questions every time — vary the angle, scenario, and phrasing each time this is called (session id: {variety_seed}).

Return ONLY a valid JSON array, no extra text, no markdown formatting, in this exact format:
[
  {{"question": "question text here", "type": "technical"}},
  {{"question": "question text here", "type": "hr"}}
]
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=1.0),
            )

            raw_text = response.text.strip()
            if raw_text.startswith('```'):
                raw_text = raw_text.split('```')[1]
                if raw_text.startswith('json'):
                    raw_text = raw_text[4:]

            questions = json.loads(raw_text.strip())
            return questions

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(3)
            continue

    # Fallback: ek bare pool se random 5 questions chuno, taake fallback bhi
    # baar baar same na dikhe
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