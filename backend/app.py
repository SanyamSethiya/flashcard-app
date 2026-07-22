import os
import time
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import Error
from spaced_repetition import calculate_next_review

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# ---------- Database Connection ----------
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "mysql_db"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "rootpassword"),
        database=os.environ.get("DB_NAME", "flashcards_db")
    )
    return connection


def ensure_schema():
    """
    Self-healing schema check: creates any missing tables even if the
    MySQL data volume already existed (init.sql only runs on a brand-new
    volume, so upgrades to the app need this to add new tables safely).
    Retries on startup since MySQL may take a few seconds to be ready.
    """
    for attempt in range(10):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category VARCHAR(100) DEFAULT 'General',
                    repetitions INT DEFAULT 0,
                    ease_factor FLOAT DEFAULT 2.5,
                    interval_days INT DEFAULT 1,
                    next_review_date DATETIME NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_log (
                    review_date DATE PRIMARY KEY
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("Schema check passed — all tables present.")
            return
        except Error as e:
            print(f"DB not ready yet (attempt {attempt + 1}/10): {e}")
            time.sleep(3)
    print("WARNING: could not verify schema after 10 attempts.")


ensure_schema()


def get_streak(cursor):
    """Count consecutive days (ending today) that have at least one review."""
    cursor.execute("SELECT review_date FROM review_log ORDER BY review_date DESC")
    dates = [row["review_date"] for row in cursor.fetchall()]
    if not dates:
        return 0

    streak = 0
    expected = date.today()
    for d in dates:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif d == expected + timedelta(days=1):
            # covers case where "today" hasn't been reviewed yet but yesterday was
            continue
        else:
            break
    return streak


# ---------- Routes ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_card():
    if request.method == "POST":
        question = request.form.get("question")
        answer = request.form.get("answer")
        category = request.form.get("category", "General")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO flashcards
               (question, answer, category, repetitions, ease_factor, interval_days, next_review_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (question, answer, category, 0, 2.5, 1, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("dashboard", toast="Card added — it's due for review right away."))

    return render_template("add_card.html")


@app.route("/edit/<int:card_id>", methods=["GET", "POST"])
def edit_card(card_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        question = request.form.get("question")
        answer = request.form.get("answer")
        category = request.form.get("category", "General")
        cursor.execute(
            "UPDATE flashcards SET question=%s, answer=%s, category=%s WHERE id=%s",
            (question, answer, category, card_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("dashboard", toast="Card updated."))

    cursor.execute("SELECT * FROM flashcards WHERE id=%s", (card_id,))
    card = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("edit_card.html", card=card)


@app.route("/delete/<int:card_id>", methods=["POST"])
def delete_card(card_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flashcards WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("dashboard", toast="Card deleted."))


@app.route("/review")
def review():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM flashcards WHERE next_review_date <= %s ORDER BY next_review_date ASC LIMIT 1",
        (datetime.now(),)
    )
    card = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("review.html", card=card)


@app.route("/review/submit", methods=["POST"])
def submit_review():
    card_id = request.form.get("card_id")
    quality = int(request.form.get("quality"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM flashcards WHERE id = %s", (card_id,))
    card = cursor.fetchone()

    if card:
        repetitions, ease_factor, interval, next_review_date = calculate_next_review(
            quality, card["repetitions"], card["ease_factor"], card["interval_days"]
        )
        cursor.execute(
            """UPDATE flashcards
               SET repetitions=%s, ease_factor=%s, interval_days=%s, next_review_date=%s
               WHERE id=%s""",
            (repetitions, ease_factor, interval, next_review_date, card_id)
        )
        # Log today's review for streak tracking (ignore if already logged today)
        cursor.execute(
            "INSERT IGNORE INTO review_log (review_date) VALUES (%s)", (date.today(),)
        )
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for("review"))


@app.route("/dashboard")
def dashboard():
    selected_category = request.args.get("category", "all")
    toast = request.args.get("toast")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if selected_category and selected_category != "all":
        cursor.execute(
            "SELECT * FROM flashcards WHERE category=%s ORDER BY next_review_date ASC",
            (selected_category,)
        )
    else:
        cursor.execute("SELECT * FROM flashcards ORDER BY next_review_date ASC")
    cards = cursor.fetchall()

    cursor.execute("SELECT DISTINCT category FROM flashcards ORDER BY category ASC")
    categories = [row["category"] for row in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) as due_count FROM flashcards WHERE next_review_date <= %s", (datetime.now(),))
    due_count = cursor.fetchone()["due_count"]

    cursor.execute("SELECT COUNT(*) as total_count FROM flashcards")
    total = cursor.fetchone()["total_count"]

    streak = get_streak(cursor)

    now = datetime.now()

    cursor.close()
    conn.close()
    return render_template(
        "dashboard.html",
        cards=cards,
        due_count=due_count,
        total=total,
        categories=categories,
        selected_category=selected_category,
        streak=streak,
        toast=toast,
        now=now
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    # Note: in production, Gunicorn runs the app (see Dockerfile CMD).
    # This block only runs if you execute `python app.py` directly for local testing.
    app.run(host="0.0.0.0", port=5000, debug=False)
