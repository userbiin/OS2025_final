from flask import Flask, render_template, request, jsonify, abort
import json, os, sqlite3
from datetime import datetime
import random
from services.emotion import predict_top

app = Flask(__name__)

DB_PATH = os.path.join("data", "diary.db")
os.makedirs("data", exist_ok=True)

EMPATHY_MESSAGES = {
    "joy": [
        "오늘처럼 기쁜 하루를 보내신 당신께 축하드립니다! 그 기쁨이 내일도 이어지기를 응원합니다.",
        "당신의 기쁨은 세상에서 가장 아름다운 에너지예요. 스스로에게 그 행복을 선물해 준 당신이 자랑스럽습니다.",
        "당신이 느낀 벅찬 기쁨은 결코 사소한 것이 아닙니다. 그 소중한 감정을 충분히 만끽하고, 오래도록 기억하세요.",
        "오늘 하루를 기쁨으로 가득 채운 당신의 긍정적인 힘이 정말 대단합니다. 스스로를 칭찬해 주세요!",
        "오늘 느낀 기쁨의 순간들이 앞으로 당신이 나아갈 길에 밝은 이정표가 되어줄 거예요. 잘하셨습니다!",
        "삶은 이런 소중한 기쁨의 순간들로 채워집니다. 지금 이 행복한 감사를 놓치지 마세요.",
        "당신의 기쁨은 전염성이 강합니다. 그 미소와 행복한 에너지를 주변 사람들과도 마음껏 나누며, 오늘 하루를 빛내세요!"
    ],

    "sadness": [
        "오늘 하루 슬펐다면, 충분히 슬퍼해도 괜찮습니다. 당신의 감정을 존중하고, 아낌없이 안아주고 싶어요.",
        "힘든 하루를 무사히 견뎌내 준 것만으로도 당신은 이미 대단한 일을 해냈어요. 정말 고생 많으셨습니다.",
        "슬픔은 잠시 쉬어가라는 신호일 수 있습니다. 오늘은 모든 것을 내려놓고 오직 당신 자신을 돌보는 데 집중하세요.",
        "세상에서 가장 중요한 것은 당신의 마음입니다. 그 마음이 아프다면, 잠시 멈추고 스스로에게 위로의 말을 건네주세요.",
        "지금 이 슬픔이 영원히 지속되지는 않을 거예요. 시간이 당신의 상처를 부드럽게 감싸줄 것입니다.",
        "저는 당신의 슬픔을 있는 그대로 받아들입니다. 혼자 감당하려 하지 말고, 기대어 쉬어도 괜찮아요.",
        "슬픔 뒤에는 언제나 더 단단하고 따뜻해진 당신이 기다리고 있습니다. 이 시간을 통해 당신은 성장하고 있어요."
    ],

    "fear": [
        "두려움을 느꼈음에도 불구하고 오늘 하루를 잘 이겨내셨습니다. 당신이 겪은 두려움보다 당신의 용기가 훨씬 더 큽니다.",
        "두려움은 미지의 것에 대한 자연스러운 반응일 뿐입니다. 당신은 두려움에 잡아먹히지 않고 하루를 살아냈어요. 정말 자랑스럽습니다.",
        "당신이 느낀 두려움의 크기는 그 상황을 얼마나 진지하게 받아들였는지에 대한 증거입니다. 당신은 책임감 있는 사람입니다.",
        "두려움이 당신을 멈추게 하지 못했다는 사실을 기억하세요. 오늘 당신은 두려움과 함께 걸었지만, 결국 끝까지 해냈습니다.",
        "두려움은 당신을 약하게 만드는 것이 아니라, 다음에 더 강해질 기회를 주는 신호입니다. 잠시 숨을 고르세요.",
        "당신이 두려워했던 일은 생각보다 일어나지 않을 수도 있습니다. 지금은 걱정을 잠시 내려놓고 편안한 휴식을 취하세요.",
        "가장 용감한 사람은 두려움을 느끼지 않는 사람이 아니라, 두려움을 느끼면서도 한 발짝 나아가는 사람입니다. 바로 당신처럼요."
    ],

    "anger": [
        "힘든 상황 속에서 감정을 폭발시키지 않고 오늘 하루를 마무리한 것만으로도 대단한 자제력입니다. 스스로를 인정해주세요.",
        "분노는 뜨거운 에너지입니다. 이 에너지를 남에게 돌리기 전에, 잠시 멈추고 자신을 보호하는 데 사용하세요.",
        "화가 난다는 것은 당신이 무엇을 중요하게 생각하는지 알려주는 강력한 신호입니다. 이 감정의 이유를 천천히 돌아보세요.",
        "가끔은 세상이 우리의 기대와 다르게 흘러갈 때가 있습니다. 당신의 잘못이 아닙니다. 이럴 땐 잠깐 쉬어가는 것이 최선입니다.",
        "내일 아침까지 이 무거운 감정을 꼭 끌어안고 있을 필요는 없습니다. 오늘은 털어내고 가볍게 잠드세요.",
        "당신이 느낀 분노의 원인이 무엇이든, 당신은 그 화보다 훨씬 더 크고 소중한 존재입니다.",
        "화가 났던 일은 오늘 하루의 일부일 뿐, 당신의 전부는 아닙니다. 이제 그 하루를 내려놓고 새로운 내일을 맞이할 준비를 합시다."
    ],

    "disgust": [
        "정말 끔찍한 하루를 견뎌내느라 고생 많으셨습니다. 불쾌하고 역겨운 상황에 맞선 당신의 용기에 깊이 감사드립니다.",
        "그 역겨웠던 상황은 당신의 일부가 아닙니다. 깨끗한 물로 손을 씻듯이, 오늘 하루의 더러웠던 감정들을 씻어내세요.",
        "오늘은 그저 재수가 없었던 하루일 뿐입니다. 그 경험을 과거에 두고, 내일은 상쾌하고 깨끗한 시작을 할 수 있습니다.",
        "누군가의 역겨운 행동이나 상황 때문에 당신의 빛이 바래지 않도록 하세요. 당신은 그 불쾌함보다 훨씬 더 크고 강합니다.",
        "따뜻한 물로 샤워를 하거나 좋아하는 향을 맡으며, 오늘 하루 쌓였던 불쾌한 잔여물들을 물리적으로 털어내는 데 집중해 보세요.",
        "이 힘든 하루를 잘 통과해 준 스스로에게 고마워하세요. 당신의 멘탈은 생각보다 강인합니다.",
        "이제 편안하고 안전한 당신만의 공간으로 돌아왔습니다. 모든 걱정을 내려놓고, 당신이 좋아하는 것들로 마음을 정화하세요."
    ],

    "surprise": [
        "오늘 하루, 정말 다이나믹한 경험을 하셨네요! 파란만장한 하루를 무사히 견뎌낸 당신의 적응력에 박수를 보냅니다.",
        "놀라움은 삶이 지루하지 않다는 증거죠. 당신은 오늘, 생동감 넘치는 하루를 온전히 경험했습니다. 축하합니다!",
        "오늘의 놀라운 일들이 당신의 삶에 긍정적인 반전이 되기를 바랍니다. 흥미진진한 이야기의 주인공이 되셨네요.",
        "오늘의 놀라운 경험들은 당신의 시야를 넓혀주었을 겁니다. 새로운 것을 배운 소중한 하루였습니다.",
        "가끔은 이런 놀라운 일들이 우리를 더 깨어있게 만들죠. 이 에너지와 생생한 기억을 소중히 간직하세요.",
        "놀라움으로 가득했던 오늘 하루를 무사히 마무리한 당신께, '참 잘했어요!'라는 칭찬을 드리고 싶습니다.",
        "어떤 일이든 잘 헤쳐나갈 수 있다는 자신감을 오늘 다시 한번 얻으셨을 거예요. 당신은 유연하고 강한 사람입니다."
    ],

    "neutral": [
        "별일 없이 지나간 하루야말로 가장 큰 축복입니다. 그 평온함을 누릴 줄 아는 당신에게 위로와 안정을 전합니다.",
        "큰 파도 없이 잔잔하게 흘러간 하루, 그 평화로움 속에 당신은 쉼과 에너지를 채웠을 겁니다. 정말 잘 쉬셨습니다.",
        "오늘은 소란스러운 사건 대신, 당신의 내면에 귀 기울일 수 있었던 조용한 하루였을 거예요. 그 고요함을 즐기세요.",
        "별일 없는 하루가 주는 선물은 바로 '안전'과 '평화'입니다. 그 귀한 선물을 온전히 받아들이고 감사해하세요.",
        "지나치게 애쓰지 않고, 당신의 삶이 흘러가는 대로 맡길 줄 아는 당신의 여유로움이 멋집니다.",
        "별다른 일이 없다는 것은 모든 것이 제자리를 지키고 있었다는 뜻입니다. 삶의 안정성에 감사하는 밤을 보내세요.",
        "작은 행복을 발견하기 가장 좋은 날이 바로 '별일 없는 날'입니다. 오늘 당신을 미소 짓게 한 아주 작은 순간을 떠올려보세요."
    ],
    
}

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

# 공용 함수 추가
# DB 조회 코드를 함수로 빼두기
# 같은 날 일기 조회 로직을 API 라우트와 HTML 렌더링 라우트에서 공유하기 위해서 작성.
# 이렇게 해두면 나중에 컬럼 구조를 바꾸거나 로직을 바꿔도 한 군데만 고치면 됨.
def fetch_diary(date_str):
    """주어진 날짜의 일기 하나를 dict 형태로 반환. 없으면 None."""
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(
            "SELECT date, text, label, score, emoji, probs FROM diary WHERE date=?",
            (date_str,)
        )
        row = cur.fetchone()

    if not row:
        return None

    d, text, label, score, emoji, probs = row
    return {
        "date": d,
        "text": text,
        "label": label,
        "score": score,
        "emoji": emoji,
        "probs": json.loads(probs or "{}")
    }


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

    diary = fetch_diary(date_str)
    if diary is None:
        return jsonify({"ok": False, "error": "No diary for date"}), 404

    return jsonify({"ok": True, **diary})

#    with sqlite3.connect(DB_PATH) as con:
#        cur = con.execute("SELECT date, text, label, score, emoji, probs FROM diary WHERE date=?", (date_str,))
#        row = cur.fetchone()
#    if not row:
#        return jsonify({"ok": False, "error": "No diary for date"}), 404

#    d, text, label, score, emoji, probs = row
#    return jsonify({
#        "ok": True,
#        "date": d, "text": text, "label": label, "score": score, "emoji": emoji,
#        "probs": json.loads(probs or "{}")
#    })

@app.get("/diary/<date_str>")
def diary_detail_page(date_str):
    """특정 날짜의 일기를 HTML 페이지로 보여주는 라우트"""

    # 1) 날짜 형식 검증
    try:
        _ = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        # 잘못된 URL 형식이면 400
        abort(400, description="Invalid date format")

    # 2) DB에서 해당 날짜 일기 조회
    diary = fetch_diary(date_str)
    if diary is None:
        # 일기 없으면 404
        abort(404, description="No diary for this date")

    label = diary.get("label", "")
    msg_list = EMPATHY_MESSAGES.get(label) or EMPATHY_MESSAGES.get("_default", [])
    empathy_msg = random.choice(msg_list) if msg_list else ""

    dt = datetime.strptime(diary["date"], "%Y-%m-%d")
    display_day = f"{dt.day:02d}"         
    display_month = dt.strftime("%B")      

    # 3) detail.html 템플릿 렌더링
    return render_template("detail.html", diary=diary, empathy_msg=empathy_msg, display_day=display_day, display_month=display_month)
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
