import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

torch.manual_seed(42)

base_model = "j-hartmann/emotion-english-distilroberta-base"
tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForSequenceClassification.from_pretrained(base_model)


if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Using MPS")
elif torch.cuda.is_available():
    device = torch.device("cuda")
    print("Using CUDA")
else:
    device = torch.device("cpu")
    print("Using CPU")

model.to(device)


print(model.config.id2label)
id2label = model.config.id2label
label2id = model.config.label2id

trainset = pd.read_csv("Dataset/train.csv") 
testset = pd.read_csv("Dataset/valid.csv")  

trainset["label_id"] = trainset["label"].map(label2id)
testset["label_id"] = testset["label"].map(label2id)


class EmotionDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=128):
        self.texts = df["text"].tolist()
        self.labels = df["label_id"].tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])

        enc = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt",
        )

        item = {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long),
        }
        return item

trainloader = EmotionDataset(trainset, tokenizer)
testloader = EmotionDataset(testset, tokenizer)

trainloader = DataLoader(trainloader, batch_size=16, shuffle=True)
validloader = DataLoader(testloader, batch_size=32, shuffle=False)

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)

epochs = 6 # 10 -> 6

for epoch in range(epochs):
    model.train()
    running_loss = 0.0

    for batch in trainloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )
        loss = outputs.loss
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    scheduler.step()
    avg_train_loss = running_loss / len(trainloader)

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for batch in validloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = outputs.logits.argmax(dim=-1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    acc = correct / total if total > 0 else 0.0

    print(f"[Epoch {epoch+1}] train_loss={avg_train_loss:.4f}, valid_acc={acc:.4f}")

model.save_pretrained("./finetuned_model_1202")
tokenizer.save_pretrained("./finetuned_model_1202")