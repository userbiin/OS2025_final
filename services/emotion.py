from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch


FINETUNED_DIR = "finetuned_model_1202" 

ft_tokenizer = AutoTokenizer.from_pretrained(FINETUNED_DIR)
ft_model = AutoModelForSequenceClassification.from_pretrained(FINETUNED_DIR)

_classifier = pipeline(
    "text-classification",
    model=ft_model,
    tokenizer=ft_tokenizer,
    top_k=None,
    device=-1,
)

device = "cpu"


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
