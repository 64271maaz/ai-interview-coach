from google import genai
from google.genai import types
from config import Config
import json
import time

client = genai.Client(api_key=Config.GEMINI_API_KEY)


def evaluate_all_answers(job_role, qa_list):
    """
    qa_list = [{"id": answer_id, "question": "...", "type": "...", "answer": "..."}, ...]
    Sab answers ko EK hi Gemini call mein evaluate karta hai (quota bachane ke liye).
    Returns: dict { answer_id: {scores + feedback} }
    """

    # Blank answers ko seedha 0 de dein, Gemini ko unhe evaluate karne ki zaroorat nahi
    non_blank = [qa for qa in qa_list if qa['answer'].strip() != '']
    results = {}

    for qa in qa_list:
        if qa['answer'].strip() == '':
            results[qa['id']] = {
                "relevance_score": 0, "technical_accuracy_score": 0,
                "communication_score": 0, "completeness_score": 0,
                "strengths": "N/A", "weaknesses": "Answer was left blank.",
                "missing_concepts": "A complete answer was expected but not provided."
            }

    if not non_blank:
        return results

    items_text = ""
    for qa in non_blank:
        items_text += f"\nID: {qa['id']}\nQuestion ({qa['type']}): {qa['question']}\nAnswer: {qa['answer']}\n"

    prompt = f"""You are an expert interview evaluator for the role of "{job_role}".

Evaluate EACH of the following question-answer pairs. For each, score 0-100 on: relevance, technical accuracy (or logical soundness if non-technical), communication clarity, and completeness. Also give brief strengths, weaknesses, and missing_concepts.
{items_text}
Return ONLY a valid JSON array, no markdown, in this exact format:
[
  {{"id": <the ID number>, "relevance_score": 75, "technical_accuracy_score": 70, "communication_score": 80, "completeness_score": 65, "strengths": "...", "weaknesses": "...", "missing_concepts": "..."}}
]
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3),
            )
            raw_text = response.text.strip()
            if raw_text.startswith('```'):
                raw_text = raw_text.split('```')[1]
                if raw_text.startswith('json'):
                    raw_text = raw_text[4:]

            parsed = json.loads(raw_text.strip())
            for item in parsed:
                results[item['id']] = item
            return results

        except Exception as e:
            print(f"Evaluation attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5)
            continue

    # Fallback agar sab attempts fail ho jayein
    for qa in non_blank:
        results[qa['id']] = {
            "relevance_score": 50, "technical_accuracy_score": 50,
            "communication_score": 50, "completeness_score": 50,
            "strengths": "Could not evaluate (quota/server issue).",
            "weaknesses": "Evaluation service temporarily unavailable.",
            "missing_concepts": "N/A"
        }
    return results