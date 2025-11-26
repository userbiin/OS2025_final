from transformers import pipeline

# 1) 파이프라인을 앱 시작 시 1회만 로드(캐시)
_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

# 2) 라벨
EMOJI_MAP = {
    "joy": "😄",
    "sadness": "😢",
    "fear": "😟", 
    "anger": "😠",
    "disgust": "🤢",
    "surprise": "😲",
    "neutral": "😐",
}

# 텍스트의 감정을 분류, 이모지 반환
def predict_top(text: str):
    """
    텍스트를 넣으면 (top_label, top_score, probs_dict, emoji) 반환
    probs_dict: {"joy":0.23, "sadness":0.1, ...}
    """
    if not text or not text.strip():
        return ("neutral", 0.0, {}, EMOJI_MAP["neutral"])
    outputs = _classifier(text)[0]  # 전체 라벨 확률 리스트
    # outputs 예: [{'label':'joy','score':0.72}, ...]
    probs = {o["label"]: float(o["score"]) for o in outputs}
    top_label = max(probs, key=probs.get)
    top_score = probs[top_label]
    emoji = EMOJI_MAP.get(top_label, "😐")
    return (top_label, top_score, probs, emoji)
