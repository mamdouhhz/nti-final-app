import os
import time
from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "appdb")
DB_USER = os.environ.get("DB_USER", "appuser")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    for attempt in range(10):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            return
        except Error:
            time.sleep(3)
    raise RuntimeError("Could not connect to database after 10 attempts")


@app.route("/api/visits", methods=["GET"])
def visits():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO visits () VALUES ()")
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM visits")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify(visit_count=count)


@app.route("/health")
def health():
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)