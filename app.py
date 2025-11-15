from flask import Flask, render_template, request, jsonify
import json, os, sqlite3
from datetime import datetime
from services.emotion import predict_top

app = Flask(__name__)

DB_PATH = os.path.join("data", "diary.db")
os.makedirs("data", exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS diary (
                date TEXT PRIMARY KEY,
                text TEXT,
                label TEXT,
                score REAL,
                emoji TEXT,
                probs TEXT
            )
        """)
init_db()
# 주석
@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/diary")
def create_or_update_diary():
    data = request.get_json(force=True)
    date_str = (data.get("date") or "").strip()       # "YYYY-MM-DD"
    text = (data.get("text") or "").strip()

    # 날짜 검증
    try:
        _ = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid date format (YYYY-MM-DD)"}), 400

    # 감정 추론
    label, score, probs, emoji = predict_top(text)

    row = (date_str, text, label, score, emoji, json.dumps(probs, ensure_ascii=False))
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO diary(date, text, label, score, emoji, probs)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
              text=excluded.text,
              label=excluded.label,
              score=excluded.score,
              emoji=excluded.emoji,
              probs=excluded.probs
        """, row)

    return jsonify({"ok": True, "date": date_str, "label": label, "score": score, "emoji": emoji})

@app.get("/api/diary")
def list_diary_month():
    year = request.args.get("year")
    month = request.args.get("month")  # "01"~"12"
    if not (year and month and len(year)==4 and len(month)==2):
        return jsonify({"ok": False, "error": "Query needs ?year=YYYY&month=MM"}), 400

    prefix = f"{year}-{month}-"  # e.g., "2025-11-"
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute("SELECT date, emoji, label FROM diary WHERE date LIKE ?", (prefix+"%",))
        rows = cur.fetchall()
    items = [{"date": d, "emoji": e, "label": l} for (d, e, l) in rows]
    return jsonify({"ok": True, "items": items})

@app.get("/api/diary/<date_str>")
def get_diary(date_str):
    try:
        _ = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid date format"}), 400

    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute("SELECT date, text, label, score, emoji, probs FROM diary WHERE date=?", (date_str,))
        row = cur.fetchone()
    if not row:
        return jsonify({"ok": False, "error": "No diary for date"}), 404

    d, text, label, score, emoji, probs = row
    return jsonify({
        "ok": True,
        "date": d, "text": text, "label": label, "score": score, "emoji": emoji,
        "probs": json.loads(probs or "{}")
    })
@app.route("/diary_chart/<date_str>")
def diary_chart(date_str):

    return render_template("diary_chart.html", date_str=date_str)
if __name__ == "__main__":
    app.run(debug=True)
