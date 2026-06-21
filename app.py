import os
from flask import Flask, render_template, request, jsonify

from extractor import extract_text_from_pdf
from analyzer import analyze_report, ask_report
from database import save_report, get_all_reports

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")

 

@app.route("/analyze", methods=["POST"])
def analyze():

    # Check file exists
    if "file" not in request.files:
        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]
 
    if file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    # Allow only PDF files
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are allowed"
        }), 400

    try:
        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        text = extract_text_from_pdf(filepath)

        if not text or not text.strip():
            return jsonify({
                "error": "Could not extract text from PDF"
            }), 400

        results = analyze_report(text)

        save_report(
            report_type=results["report_type"],
            summary=results["summary"],
            risk_level=results["risk"],
            medical_terms=results["medical_terms"]
        )

        results["report_text"] = text

        return render_template("dashboard.html",results=results)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

 

@app.route("/ask", methods=["POST"])
def ask():

    try:
        data = request.get_json()

        question = data.get("question", "")
        text = data.get("text", "")
        if not question:
            return jsonify({
                "error": "Question is required"
            }), 400
        if not text:
            return jsonify({
                "error": "Report text is required"
            }), 400
        answer = ask_report(question, text)
        return jsonify({
            "answer": answer
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

 

@app.route("/history")
def history():
    reports = get_all_reports()
    return render_template(
        "history.html",
        reports=reports
    )
 

@app.route("/api/history")
def api_history():
    reports = get_all_reports()
    return jsonify(reports)
 
 

if __name__ == "__main__":
    app.run(debug=True)