# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 11:14:29 2025

@author: Destock-afric
"""

from datasets import load_dataset, ClassLabel
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
import pandas as pd
import numpy as np
import torch

import transformers
print(transformers.__file__)
print(transformers.__version__)

# 1. Charger le dataset CSV
data = pd.read_csv("intent_dataset.csv")

# 2. Préparer les labels uniques et créer un mapping label <-> id
labels = data['label'].unique().tolist()
label2id = {l: i for i, l in enumerate(labels)}
id2label = {i: l for l, i in label2id.items()}

data['label_id'] = data['label'].map(label2id)

# 3. Charger un tokenizer pré-entraîné (ici distilbert)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# 4. Tokenizer les textes
encodings = tokenizer(list(data['text']), truncation=True, padding=True)

# 5. Créer un Dataset PyTorch
class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __len__(self):
        return len(self.labels)
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

dataset = IntentDataset(encodings, data['label_id'].tolist())

# 6. Charger le modèle de classification
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id
)

# 7. Définir les arguments d’entraînement
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    # evaluation_strategy="no",  # ligne commentée pour éviter l'erreur
    save_strategy="epoch",
    logging_dir='./logs',
    logging_steps=10,
    load_best_model_at_end=False,
)

# 8. Créer un Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    #eval_dataset=dataset_val (si tu as une validation)
)

# 9. Lancer l’entraînement
trainer.train()
print("⏳ Début de l’entraînement ...")
trainer.train()
print("✅ Entraînement terminé.")



# 10. Sauvegarder le modèle entraîné
trainer.save_model('./intent_classifier_model')
tokenizer.save_pretrained('./intent_classifier_model')

print("✅ Entraînement terminé et modèle sauvegardé dans './intent_classifier_model'")
