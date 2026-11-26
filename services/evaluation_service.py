from services.llm import generate_text, parse_json


def evaluate_all_answers(job_role, qa_list):
    """
    qa_list = [{"id": ..., "question": "...", "type": "...", "answer": "..."}, ...]
    Sab answers EK hi call mein evaluate hote hain.
    Returns: dict {answer_id: scores+feedback}, ya None agar evaluation na ho saki.
    """
    results = {}
    non_blank = []

    for qa in qa_list:
        if qa["answer"].strip() == "":
            results[qa["id"]] = {
                "relevance_score": 0, "technical_accuracy_score": 0,
                "communication_score": 0, "completeness_score": 0,
                "strengths": "N/A", "weaknesses": "Answer was left blank.",
                "missing_concepts": "A complete answer was expected but not provided."
            }
        else:
            non_blank.append(qa)

    if not non_blank:
        return results

    items_text = ""
    for qa in non_blank:
        items_text += f"\nID: {qa['id']}\nQuestion ({qa['type']}): {qa['question']}\nAnswer: {qa['answer']}\n"

    prompt = f"""You are an expert interview evaluator for the role of "{job_role}".

Evaluate EACH of the following question-answer pairs. For each, score 0-100 on: relevance, technical accuracy (or logical soundness if non-technical), communication clarity, and completeness.
Be strict and honest: a vague, off-topic, or "no idea" answer must get a low score (under 20), and only detailed, correct answers should score above 80.
Also give brief strengths, weaknesses, and missing_concepts.
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
                results[int(item["id"])] = item
            if all(qa["id"] in results for qa in non_blank):
                return results
            print("Evaluation incomplete: some answers missing in AI response")
        except Exception as e:
            print("Evaluation JSON parse error:", e)

    # Fake 50 scores nahi: caller ko batao ke evaluation nahi hui
    return None