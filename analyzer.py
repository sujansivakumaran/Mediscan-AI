import re
import spacy
from transformers import pipeline

nlp = spacy.load("en_core_web_sm")

summarizer = pipeline("summarization",model="facebook/bart-large-cnn")

qa_model = pipeline("question-answering",model="distilbert-base-cased-distilled-squad")


def detect_report_type(text):
    text = text.lower()

    blood = ["hemoglobin", "platelet", "glucose", "wbc", "rbc"]
    prescription = ["tablet", "capsule", "medicine", "mg"]
    discharge = ["admission", "discharge", "diagnosis"]

    blood_score = sum(1 for k in blood if k in text)
    prescription_score = sum(1 for k in prescription if k in text)
    discharge_score = sum(1 for k in discharge if k in text)

    if max(blood_score, prescription_score, discharge_score) == 0:
        return "Unknown Report"

    if blood_score >= max(prescription_score, discharge_score):
        return "Blood Test Report"

    elif prescription_score >= discharge_score:
        return "Prescription"

    else:
        return "Discharge Summary"

 

def extract_medical_terms(text):

    medical_keywords = [
        "hemoglobin",
        "glucose",
        "platelet",
        "creatinine",
        "cholesterol",
        "sodium",
        "potassium",
        "calcium",
        "protein",
        "albumin",
        "bilirubin",
        "thyroid",
        "insulin",
        "cortisol",
        "iron",
        "vitamin"
    ]

    found_terms = []

    lower_text = text.lower()

    for term in medical_keywords:
        if term in lower_text:
            found_terms.append(term.title())

    return list(set(found_terms))



def summarize_report(text):

    try:

        if len(text.split()) > 800:
            text = " ".join(text.split()[:800])

        summary = summarizer(
            text,
            max_length=150,
            min_length=50,
            do_sample=False
        )

        return summary[0]["summary_text"]

    except Exception:
        return "Unable to generate summary."



def ask_report(question, text):
    try:
        if len(text.split()) > 400:
            text = " ".join(text.split()[:400])

        result = qa_model(
            question=question,
            context=text
        )

        return result["answer"]
    except Exception:
        return "Unable to answer the question."



def check_normal_abnormal(text):
    normal_ranges = {
        "hemoglobin": (12.0, 17.5),
        "glucose": (70.0, 100.0),
        "platelet": (150000, 400000),
        "creatinine": (0.6, 1.2),
        "cholesterol": (0, 200.0),
        "sodium": (136.0, 145.0),
        "potassium": (3.5, 5.0),
        "calcium": (8.5, 10.5)
    }

    results = []

    lower_text = text.lower()

    for term, (low, high) in normal_ranges.items():
        if term in lower_text:
            pattern = rf"{term}.*?(\d+\.?\d*)"
            match = re.search(
                pattern,
                lower_text,
                re.IGNORECASE | re.DOTALL
            )
            if match:

                value = float(match.group(1))

                if value < low:
                    status = "⚠️ LOW"
                elif value > high:
                    status = "⚠️ HIGH"
                else:
                    status = "✅ NORMAL"

                results.append({
                    "test": term.upper(),
                    "value": value,
                    "status": status,
                    "normal_range": f"{low} - {high}"
                })

    return results

 

def calculate_risk(results):

    abnormal = 0

    for item in results:
        if (
            "LOW" in item["status"]
            or
            "HIGH" in item["status"]
        ):
            abnormal += 1
    if abnormal == 0:
        return "🟢 LOW RISK"
    elif abnormal <= 2:
        return "🟡 MEDIUM RISK"
    else:
        return "🔴 HIGH RISK"

 

def analyze_report(text):

    report_type = detect_report_type(text)

    medical_terms = extract_medical_terms(text)

    test_results = check_normal_abnormal(text)

    risk = calculate_risk(test_results)

    summary = summarize_report(text)

    return {
        "report_type": report_type,
        "medical_terms": medical_terms,
        "test_results": test_results,
        "risk": risk,
        "summary": summary
    }