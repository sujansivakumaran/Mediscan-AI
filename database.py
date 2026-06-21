import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def save_report(report_type, summary, 
                risk_level, medical_terms):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO reports 
            (report_type, summary, risk_level, medical_terms)
            VALUES (%s, %s, %s, %s)
        """
 
        terms_str = ", ".join(medical_terms)
        cursor.execute(query, (
            report_type,
            summary,
            risk_level,
            terms_str
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Database error: {e}")
        return False


def get_all_reports():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM reports
            ORDER BY uploaded_at DESC
        """)

        reports = cursor.fetchall()
        return reports

    except Exception as e:
        print(f"Database error: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()