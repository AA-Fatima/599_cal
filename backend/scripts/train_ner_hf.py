#!/usr/bin/env python3
"""
Train Hugging Face NER model for dish and ingredient entity extraction.

Expects labeled data in JSONL format with the following structure:
{
  "text": "I want fajita with extra tomatoes",
  "entities": [
    {"start": 7, "end": 13, "label": "DISH"},
    {"start": 25, "end": 33, "label": "ING"}
  ]
}

Usage:
    python train_ner_hf.py --data data/ner_labeled.jsonl --output models/ner_hf
"""
import argparse
import json
from pathlib import Path
from typing import List, Dict
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification
)
from datasets import Dataset


LABELS = ["O", "B-DISH", "I-DISH", "B-ING", "I-ING"]
LABEL_TO_ID = {label: i for i, label in enumerate(LABELS)}
ID_TO_LABEL = {i: label for i, label in enumerate(LABELS)}


def load_labeled_data(path: str) -> List[Dict]:
    """Load labeled NER data from JSONL file."""
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def align_labels_with_tokens(text: str, entities: List[Dict], tokenizer, label_all_tokens=True):
    """Convert character-level entity spans to token-level BIO labels."""
    # Tokenize
    tokenized = tokenizer(text, truncation=True, return_offsets_mapping=True)
    offset_mapping = tokenized["offset_mapping"]
    
    # Initialize labels as "O"
    labels = ["O"] * len(offset_mapping)
    
    # Map entities to tokens
    for entity in entities:
        start_char = entity["start"]
        end_char = entity["end"]
        label_type = entity["label"]  # DISH or ING
        
        # Find tokens that overlap with entity
        entity_tokens = []
        for idx, (token_start, token_end) in enumerate(offset_mapping):
            if token_start == token_end:  # Special tokens
                continue
            if token_start >= start_char and token_end <= end_char:
                entity_tokens.append(idx)
            elif token_start < end_char and token_end > start_char:
                # Partial overlap
                entity_tokens.append(idx)
        
        # Assign BIO labels
        for i, token_idx in enumerate(entity_tokens):
            if i == 0:
                labels[token_idx] = f"B-{label_type}"
            else:
                labels[token_idx] = f"I-{label_type}"
    
    # Convert to IDs
    label_ids = [LABEL_TO_ID.get(label, 0) for label in labels]
    
    return label_ids


def prepare_dataset(data: List[Dict], tokenizer):
    """Prepare dataset for training."""
    examples = []
    
    for item in data:
        text = item["text"]
        entities = item.get("entities", [])
        
        # Tokenize
        tokenized = tokenizer(
            text,
            truncation=True,
            padding=False,
            return_offsets_mapping=True
        )
        
        # Align labels
        labels = align_labels_with_tokens(text, entities, tokenizer)
        
        # Remove offset_mapping (not needed for training)
        tokenized.pop("offset_mapping")
        tokenized["labels"] = labels
        
        examples.append(tokenized)
    
    return Dataset.from_list(examples)


def compute_metrics(eval_pred):
    """Compute F1 score for evaluation."""
    predictions, labels = eval_pred
    predictions = predictions.argmax(axis=-1)
    
    # Remove padding (-100)
    predictions = predictions[labels != -100].flatten()
    labels = labels[labels != -100].flatten()
    
    # Simple accuracy
    accuracy = (predictions == labels).mean()
    
    return {"accuracy": accuracy}


def train_ner_model(
    data_path: str,
    output_dir: str,
    base_model: str = "distilbert-base-uncased",
    epochs: int = 3,
    batch_size: int = 16
):
    """Train NER model."""
    print("=" * 60)
    print("Training Hugging Face NER Model")
    print("=" * 60)
    
    # Load data
    print(f"\nLoading data from {data_path}...")
    data = load_labeled_data(data_path)
    print(f"  Loaded {len(data)} examples")
    
    # Split train/eval (90/10)
    split_idx = int(len(data) * 0.9)
    train_data = data[:split_idx]
    eval_data = data[split_idx:]
    print(f"  Train: {len(train_data)}, Eval: {len(eval_data)}")
    
    # Load tokenizer
    print(f"\nLoading tokenizer from {base_model}...")
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    
    # Prepare datasets
    print("Preparing datasets...")
    train_dataset = prepare_dataset(train_data, tokenizer)
    eval_dataset = prepare_dataset(eval_data, tokenizer)
    
    # Load model
    print(f"\nLoading model from {base_model}...")
    model = AutoModelForTokenClassification.from_pretrained(
        base_model,
        num_labels=len(LABELS),
        id2label=ID_TO_LABEL,
        label2id=LABEL_TO_ID
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
    )
    
    # Data collator
    data_collator = DataCollatorForTokenClassification(tokenizer)
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )
    
    # Train
    print("\n" + "=" * 60)
    print("Training...")
    print("=" * 60)
    trainer.train()
    
    # Save final model
    print(f"\nSaving model to {output_dir}...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Model saved to: {output_dir}")
    print(f"To use: set HF_NER_MODEL={output_dir} in .env")


def main():
    parser = argparse.ArgumentParser(description="Train HF NER model for dish/ingredient extraction")
    parser.add_argument(
        "--data",
        type=str,
        default="data/ner_labeled.jsonl",
        help="Path to labeled JSONL data"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/ner_hf",
        help="Output directory for trained model"
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="distilbert-base-uncased",
        help="Base model to fine-tune"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Training batch size"
    )
    
    args = parser.parse_args()
    
    # Check if data exists
    if not Path(args.data).exists():
        print(f"Error: Data file not found: {args.data}")
        print("\nExpected format (JSONL):")
        print('{"text": "I want fajita with tomatoes", "entities": [{"start": 7, "end": 13, "label": "DISH"}, {"start": 19, "end": 27, "label": "ING"}]}')
        return
    
    # Train
    train_ner_model(
        data_path=args.data,
        output_dir=args.output,
        base_model=args.base_model,
        epochs=args.epochs,
        batch_size=args.batch_size
    )


if __name__ == '__main__':
    main()
