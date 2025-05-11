import os
import pandas as pd
import torch
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from torch.utils.data import Dataset

# Optional: Reduce dataset size for quick experimentation
DATA_FRACTION = 1  # Train on 20% of data for faster experimentation

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Dataset path
cleaned_data_path = "Features"
files = [f for f in os.listdir(cleaned_data_path) if f.startswith("features_")]

if not files:
    raise FileNotFoundError(f"No feature files found in {cleaned_data_path}.")

# Load all data
df_list = []
for file in files:
    try:
        temp_df = pd.read_csv(os.path.join(cleaned_data_path, file))
        df_list.append(temp_df)
    except Exception as e:
        print(f"Error reading {file}: {e}")

if not df_list:
    raise ValueError("No valid feature files found.")

data = pd.concat(df_list, ignore_index=True)

# Check required columns
required_columns = {"body", "label"}
missing_cols = required_columns - set(data.columns)
if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")

# Optional: Subsample for faster training
if DATA_FRACTION < 1.0:
    data = data.sample(frac=DATA_FRACTION, random_state=42).reset_index(drop=True)

# Use a smaller, faster model for experimentation
model_name = "prajjwal1/bert-tiny"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Dataset class
class EmailDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long)
        }

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    data['body'], data['label'], test_size=0.2, random_state=42, stratify=data['label']
)

train_dataset = EmailDataset(X_train.tolist(), y_train.tolist(), tokenizer)
test_dataset = EmailDataset(X_test.tolist(), y_test.tolist(), tokenizer)

# Load model
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
model.to(device)

# Training arguments
training_args = TrainingArguments(
    output_dir="bert_model",
    evaluation_strategy="epoch",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    save_strategy="no",
    logging_dir="/mnt/data/logs",
    logging_steps=20,
    load_best_model_at_end=False,
    report_to="none",
    fp16=torch.cuda.is_available()
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Train
train_result = trainer.train()

# Save model & tokenizer
model.save_pretrained("bert_model")
tokenizer.save_pretrained("bert_model")
print("Model trained and saved.")

# Save training logs
history = {"epoch_logs": trainer.state.log_history}
with open("bert_model/training_history.json", "w") as f:
    json.dump(history, f, indent=4)
print("Training history saved.")

# Evaluate
eval_results = trainer.evaluate()
print("Evaluation results:", eval_results)

# Make predictions on test set
predictions = trainer.predict(test_dataset)
predicted_labels = torch.argmax(torch.tensor(predictions.predictions), dim=1).tolist()

# Calculate accuracy
accuracy = accuracy_score(y_test.tolist(), predicted_labels)
print(f"Test Accuracy: {accuracy:.4f}")

# Add accuracy to eval results and save
eval_results["accuracy"] = accuracy
with open("bert_model/evaluation_results.json", "w") as f:
    json.dump(eval_results, f, indent=4)
print("Updated evaluation results saved.")

# Save predicted labels along with true labels for further analysis
results_df = pd.DataFrame({
    "true_label": y_test.tolist(),
    "predicted_label": predicted_labels
})
results_df.to_csv("bert_model/test_predictions.csv", index=False)
print("Test predictions saved.")
