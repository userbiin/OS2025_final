import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

BASE_MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"
FINETUNED_DIR = "./finetuned_model_1202" 

base_tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
base_model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL_NAME)

ft_tokenizer = AutoTokenizer.from_pretrained(FINETUNED_DIR)
ft_model = AutoModelForSequenceClassification.from_pretrained(FINETUNED_DIR)

device = "cpu"

base_model.to(device)
ft_model.to(device)

pipe_base = pipeline(
    "text-classification",
    model=base_model,
    tokenizer=base_tokenizer,
    top_k=None,
    device=-1,)

pipe_ft = pipeline(
    "text-classification",
    model=ft_model,
    tokenizer=ft_tokenizer,
    top_k=None,
    device=-1,
)

texts = [
    "Great, another super helpful meeting that could've been an email.",
    "Such a wonderful movie... I slept through half of it.",
    "This coffee tastes amazing, if you enjoy drinking burnt water.",
    "Awesome, my computer crashed right before the deadline. Just perfect.",
    "Yeah, today was definitely the best day ever... totally.",
]

def top_label(result):
    best = max(result, key=lambda x: x["score"])
    return best["label"], best["score"]

for text in texts:

    base_out = pipe_base(text)[0]
    ft_out   = pipe_ft(text)[0]

    base_label, base_score = top_label(base_out)
    ft_label, ft_score = top_label(ft_out)

    print("[BASE]      top emotion: {:10s} ({:.3f})".format(base_label, base_score))
    print("[FINETUNED] top emotion: {:10s} ({:.3f})".format(ft_label, ft_score))
    print("\n\n")