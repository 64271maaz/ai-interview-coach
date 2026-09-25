from google import genai
from google.genai import types
from config import Config
import json
import time

client = genai.Client(api_key=Config.GEMINI_API_KEY)

def generate_questions(job_role, num_questions=5, resume_text=""):
    """
    Job role (aur agar available ho to resume) ke hisaab se interview questions generate karta hai.
    """

    if resume_text:
        prompt = f"""You are an expert technical interviewer. Generate {num_questions} interview questions for the job role: "{job_role}".

Here is the candidate's resume content:
\"\"\"
{resume_text}
\"\"\"

Base some questions on the candidate's actual skills, projects, and experience mentioned in the resume, and include a mix of technical, HR, behavioral, and problem-solving questions relevant to "{job_role}".

Return ONLY a valid JSON array, no extra text, no markdown formatting, in this exact format:
[
  {{"question": "question text here", "type": "technical"}},
  {{"question": "question text here", "type": "hr"}}
]
"""
    else:
        prompt = f"""You are an expert technical interviewer. Generate {num_questions} interview questions for the job role: "{job_role}".

Include a mix of question types: technical, HR, behavioral, and problem-solving.

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
                config=types.GenerateContentConfig(temperature=0.7),
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

    return [
        {"question": f"Tell me about your experience relevant to the {job_role} role.", "type": "hr"},
        {"question": f"What are the key technical skills required for a {job_role}?", "type": "technical"},
        {"question": f"Describe a challenging problem you solved related to {job_role} work.", "type": "problem-solving"},
        {"question": "How do you handle tight deadlines and pressure at work?", "type": "behavioral"},
        {"question": f"Where do you see yourself growing within a {job_role} career path?", "type": "hr"},
    ]