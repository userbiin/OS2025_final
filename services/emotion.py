from transformers import pipeline

_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

EMOJI_MAP = {
    "joy": "😄",
    "sadness": "😢",
    "fear": "😟", 
    "anger": "😠",
    "disgust": "🤢",
    "surprise": "😲",
    "neutral": "😐",
}

def predict_top(text: str):
    if not text or not text.strip():
        return ("neutral", 0.0, {}, EMOJI_MAP["neutral"])
    outputs = _classifier(text)[0]  # 전체 라벨 확률 리스트
    probs = {o["label"]: float(o["score"]) for o in outputs}
    top_label = max(probs, key=probs.get)
    top_score = probs[top_label]
    emoji = EMOJI_MAP.get(top_label, "😐")
    return (top_label, top_score, probs, emoji)
