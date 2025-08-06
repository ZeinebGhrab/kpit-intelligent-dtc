import pandas as pd
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
from datasets import Dataset

# ==========================
# 1. Dataset loading
# ==========================
df = pd.read_excel("training_dataset_readable.xlsx")  # Training file

dataset = Dataset.from_pandas(df[["Implementation", "Readable_Output"]].rename(
    columns={"Implementation": "input_texts", "Readable_Output": "target_texts"}
))

# Split train/test
dataset = dataset.train_test_split(test_size=0.2)

# ==========================
# 2. Tokenizer and model
# ==========================
model_name = "t5-small"  
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

max_input_length = 128
max_output_length = 256

def preprocess(examples):
    model_inputs = tokenizer(
        examples["input_texts"], 
        max_length=max_input_length, 
        padding="max_length", 
        truncation=True
    )
    labels = tokenizer(
        examples["target_texts"], 
        max_length=max_output_length, 
        padding="max_length", 
        truncation=True
    )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_datasets = dataset.map(preprocess, batched=True)

# ==========================
# 3. Training arguments
# ==========================
training_args = TrainingArguments(
    output_dir="./dtc_t5_finetuned",
    eval_strategy="epoch",
    learning_rate=3e-4,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=6,
    weight_decay=0.01,
    save_total_limit=2,
    logging_dir="./logs",
    logging_steps=50,
    report_to="none"
)

# ==========================
# 4. Trainer
# ==========================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    tokenizer=tokenizer
)

# ==========================
# 5. Training
# ==========================
trainer.train()

# ==========================
# 6. Saving
# ==========================
trainer.save_model("../t5_model")
tokenizer.save_pretrained("../t5_model")

print("✅ Training completed and model saved in ../t5_model")
