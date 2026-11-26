from fpdf import FPDF

# Gemini kabhi kabhi special unicode characters deta hai (curly quotes, long dash).
# Standard PDF fonts sirf latin-1 support karte hain, is liye unhe pehle saaf karte hain.
REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u2022": "-", "\u00a0": " ",
}


def clean(text):
    if text is None:
        return ""
    text = str(text)
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


def answer_avg(a):
    return ((a.relevance_score or 0) + (a.technical_accuracy_score or 0) +
            (a.communication_score or 0) + (a.completeness_score or 0)) / 4


class ReportPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 20, 32)
        self.rect(0, 0, 210, 28, style="F")
        self.set_text_color(45, 212, 191)
        self.set_font("Helvetica", "B", 18)
        self.set_xy(10, 8)
        self.cell(0, 10, "AI Interview Coach - Readiness Report", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.set_y(34)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def section_title(pdf, title):
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(13, 148, 136)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)


def labeled(pdf, label, text, rgb):
    """Ek coloured bold label, uske saamne wrapped text."""
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*rgb)
    pdf.cell(34, 5, label, new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 5, clean(text) or "-", new_x="LMARGIN", new_y="NEXT")


def build_recommendations(interview, answers):
    recs = []

    # 1. Kamzor question types
    by_type = {}
    for a in answers:
        by_type.setdefault(a.question_type or "general", []).append(answer_avg(a))
    for qtype, scores in by_type.items():
        avg = sum(scores) / len(scores)
        if avg < 60:
            recs.append(f"Practice more {qtype} questions (current average: {avg:.0f}/100).")

    # 2. Missing concepts jo AI ne batayi
    seen = set()
    for a in answers:
        concepts = (a.missing_concepts or "").strip()
        if concepts and concepts.upper() != "N/A" and concepts not in seen:
            seen.add(concepts)
            recs.append(f"Revise: {concepts[:200]}")
        if len(seen) >= 5:
            break

    # 3. Overall advice
    overall = interview.overall_score or 0
    if overall >= 75:
        recs.append("You are in good shape. Keep practising with different roles and harder questions.")
    elif overall >= 50:
        recs.append("Solid base. Add concrete examples and key terminology to make answers more complete.")
    else:
        recs.append("Focus on fundamentals first, then structure answers clearly (for behavioral questions use the STAR method).")

    return recs


def generate_report_pdf(interview, answers, candidate_name):
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # ---- Candidate details ----
    details = [
        ("Candidate", candidate_name),
        ("Job Role", interview.job_role),
        ("Interview Date", interview.date_taken.strftime("%d %b %Y")),
        ("Resume Used", "Yes" if interview.resume_used else "No"),
    ]
    for label, value in details:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(38, 7, f"{label}:")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, clean(value), new_x="LMARGIN", new_y="NEXT")

    # ---- Score boxes ----
    section_title(pdf, "Readiness Scores")
    scores = [
        ("Overall", interview.overall_score),
        ("Technical", interview.technical_score),
        ("Communication", interview.communication_score),
        ("Confidence", interview.confidence_score),
    ]
    box_w, gap = 45, 10 / 3
    x, y = 10, pdf.get_y()
    for i, (label, value) in enumerate(scores):
        if i == 0:
            pdf.set_fill_color(20, 184, 166)
            pdf.set_text_color(15, 20, 32)
        else:
            pdf.set_fill_color(235, 240, 245)
            pdf.set_text_color(30, 30, 30)
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(box_w, 14, f"{(value or 0):.1f}", align="C", fill=True)
        pdf.set_xy(x, y + 14)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(box_w, 8, label, align="C", fill=True)
        x += box_w + gap
    pdf.set_y(y + 28)
    pdf.set_text_color(0, 0, 0)

    # ---- Summary: best strength / biggest weakness ----
    if answers:
        best = max(answers, key=answer_avg)
        worst = min(answers, key=answer_avg)
        section_title(pdf, "Summary")
        labeled(pdf, "Key Strength:", best.strengths, (22, 163, 74))
        pdf.ln(1)
        labeled(pdf, "Key Weakness:", worst.weaknesses, (220, 38, 38))

    # ---- Question by question ----
    section_title(pdf, "Question-by-Question Feedback")
    for i, a in enumerate(answers, start=1):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, clean(f"Q{i} [{(a.question_type or 'general').upper()}] {a.question_text}"),
                       new_x="LMARGIN", new_y="NEXT")

        answer_text = (a.user_answer or "").strip() or "(No answer provided)"
        labeled(pdf, "Your Answer:", answer_text[:500], (80, 80, 80))
        labeled(pdf, "Scores:",
                f"Relevance {a.relevance_score or 0:.0f} | Technical {a.technical_accuracy_score or 0:.0f} | "
                f"Communication {a.communication_score or 0:.0f} | Completeness {a.completeness_score or 0:.0f}",
                (37, 99, 235))
        labeled(pdf, "Strengths:", a.strengths, (22, 163, 74))
        labeled(pdf, "Weaknesses:", a.weaknesses, (220, 38, 38))
        labeled(pdf, "Missing Concepts:", a.missing_concepts, (180, 120, 0))
        pdf.ln(4)

    # ---- Recommendations ----
    section_title(pdf, "Recommendations")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    for rec in build_recommendations(interview, answers):
        pdf.multi_cell(0, 6, clean(f"- {rec}"), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())