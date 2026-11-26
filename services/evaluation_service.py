import re
from services.llm import generate_text, parse_json

# Answers that count as "no real answer" (compared after lowercasing and removing punctuation)
NO_ANSWER = {
    "", "no idea", "idk", "i dont know", "i don't know", "dont know", "don't know",
    "nill", "nil", "none", "na", "n/a", "no", "nothing", "not sure", "skip", "pass",
}

SCORE_KEYS = [
    "relevance_score",
    "technical_accuracy_score",
    "communication_score",
    "completeness_score",
]


def _is_no_answer(text):
    """Return True if the answer is empty, too short, or a 'no idea' style reply."""
    cleaned = re.sub(r"[^a-z' /]", "", text.lower()).strip()
    return cleaned in NO_ANSWER or len(text.strip()) < 3


def _zero_result(reason):
    """Result used when there is no meaningful answer to evaluate."""
    return {
        "relevance_score": 0,
        "technical_accuracy_score": 0,
        "communication_score": 0,
        "completeness_score": 0,
        "strengths": "N/A",
        "weaknesses": reason,
        "missing_concepts": "A complete answer was expected but not provided.",
    }


def _normalize(item):
    """
    Clean up the scores returned by the AI:
    - keep every score as a number between 0 and 100
    - fix contradictory scores (for example relevance 100 when the answer is empty)
    """
    for key in SCORE_KEYS:
        try:
            item[key] = max(0.0, min(100.0, float(item.get(key, 0))))
        except (TypeError, ValueError):
            item[key] = 0.0

    # If both technical accuracy and completeness are near zero,
    # the answer cannot be highly relevant or well communicated.
    if item["technical_accuracy_score"] <= 10 and item["completeness_score"] <= 10:
        item["relevance_score"] = min(item["relevance_score"], 15.0)
        item["communication_score"] = min(item["communication_score"], 20.0)

    item.setdefault("strengths", "")
    item.setdefault("weaknesses", "")
    item.setdefault("missing_concepts", "")
    return item


def evaluate_all_answers(job_role, qa_list):
    """
    qa_list = [{"id": ..., "question": "...", "type": "...", "answer": "..."}, ...]
    All answers are evaluated in ONE AI call (saves API quota).
    Returns: dict {answer_id: scores + feedback}, or None if evaluation failed.
    """
    results = {}
    to_evaluate = []

    # Blank or "no idea" answers get zero directly, no AI call needed
    for qa in qa_list:
        if _is_no_answer(qa["answer"]):
            results[qa["id"]] = _zero_result("No meaningful answer was provided.")
        else:
            to_evaluate.append(qa)

    if not to_evaluate:
        return results

    items_text = ""
    for qa in to_evaluate:
        items_text += (
            f"\nID: {qa['id']}\n"
            f"Question ({qa['type']}): {qa['question']}\n"
            f"Answer: {qa['answer']}\n"
        )

    prompt = f"""You are an expert interview evaluator for the role of "{job_role}".

Evaluate EACH of the following question-answer pairs. For each one, score 0-100 on:
- relevance_score: does the answer actually address the question that was asked?
- technical_accuracy_score: is the content correct (or logically sound for non-technical questions)?
- communication_score: is it clear, structured, and easy to follow?
- completeness_score: does it cover all parts of the question with enough depth?

Rules:
- Be strict and honest. Vague, off-topic, or empty answers must score under 20 on every dimension.
- Only detailed, correct, well-structured answers should score above 80.
- Judge the answer as a candidate's own response. Do not reward an answer just because it sounds polished.
- Keep the scores consistent with your feedback. If you say the answer misses the question, relevance must be low.
- Give brief strengths, weaknesses, and missing_concepts for each answer.
{items_text}
Return ONLY a valid JSON array, no markdown, in this exact format:
[
  {{"id": <the ID number>, "relevance_score": 75, "technical_accuracy_score": 70, "communication_score": 80, "completeness_score": 65, "strengths": "...", "weaknesses": "...", "missing_concepts": "..."}}
]
"""

    raw = generate_text(prompt, temperature=0.3, json_mode=True)
    if raw:
        try:
            parsed = parse_json(raw)
            for item in parsed:
                results[int(item["id"])] = _normalize(item)

            if all(qa["id"] in results for qa in to_evaluate):
                return results
            print("Evaluation incomplete: some answers are missing in the AI response")
        except Exception as e:
            print("Evaluation JSON parse error:", e)

    # No fake scores: tell the caller that evaluation did not happen
    return None