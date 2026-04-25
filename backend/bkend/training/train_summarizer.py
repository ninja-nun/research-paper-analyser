"""Fine-tune a summarization model on Kaggle scientific-paper data.

Recommended Kaggle dataset:
    syndri224/arxiv-summary-dataset

Expected columns:
    input/article/document/text/full_text
    target/abstract/summary
"""

from __future__ import annotations

import argparse
from pathlib import Path

import evaluate
import numpy as np
from datasets import load_dataset, load_from_disk
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)


INPUT_COLUMNS = ("article", "document", "text", "full_text", "input")
TARGET_COLUMNS = ("abstract", "summary", "target")


def _find_column(columns: list[str], candidates: tuple[str, ...], label: str) -> str:
    lower_to_original = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate in lower_to_original:
            return lower_to_original[candidate]
    raise ValueError(f"Could not find {label} column. Available columns: {columns}")


def _load_local_dataset(data_dir: Path):
    if (data_dir / "dataset_dict.json").exists():
        return load_from_disk(str(data_dir))

    data_files = {}
    for split in ("train", "validation", "valid", "test"):
        for extension in ("csv", "json", "jsonl"):
            path = data_dir / f"{split}.{extension}"
            if path.exists():
                normalized_split = "validation" if split == "valid" else split
                data_files[normalized_split] = str(path)
                break

    if "train" not in data_files:
        raise FileNotFoundError(
            f"No train.csv/train.json/train.jsonl found in {data_dir}. "
            "Download and extract the Kaggle dataset there first."
        )

    extension = Path(data_files["train"]).suffix.lstrip(".")
    dataset_type = "json" if extension in {"json", "jsonl"} else "csv"
    dataset = load_dataset(dataset_type, data_files=data_files)

    if "validation" not in dataset:
        split = dataset["train"].train_test_split(test_size=0.05, seed=42)
        dataset["train"] = split["train"]
        dataset["validation"] = split["test"]

    return dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/kaggle/arxiv-summary-dataset")
    parser.add_argument("--output-dir", default="training/checkpoints/bart-arxiv")
    parser.add_argument("--model-name", default="sshleifer/distilbart-cnn-12-6")
    parser.add_argument("--max-input-length", type=int, default=1024)
    parser.add_argument("--max-target-length", type=int, default=256)
    parser.add_argument("--train-samples", type=int, default=2000)
    parser.add_argument("--eval-samples", type=int, default=200)
    parser.add_argument("--epochs", type=float, default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    dataset = _load_local_dataset(data_dir)

    columns = dataset["train"].column_names
    input_column = _find_column(columns, INPUT_COLUMNS, "input text")
    target_column = _find_column(columns, TARGET_COLUMNS, "target summary")

    if args.train_samples:
        dataset["train"] = dataset["train"].select(range(min(args.train_samples, len(dataset["train"]))))
    if args.eval_samples:
        dataset["validation"] = dataset["validation"].select(
            range(min(args.eval_samples, len(dataset["validation"])))
        )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)

    def preprocess(batch):
        inputs = [str(value) for value in batch[input_column]]
        targets = [str(value) for value in batch[target_column]]
        model_inputs = tokenizer(
            inputs,
            max_length=args.max_input_length,
            truncation=True,
        )
        labels = tokenizer(
            text_target=targets,
            max_length=args.max_target_length,
            truncation=True,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized = dataset.map(
        preprocess,
        batched=True,
        remove_columns=columns,
    )

    rouge = evaluate.load("rouge")

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        if isinstance(predictions, tuple):
            predictions = predictions[0]

        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_predictions = tokenizer.batch_decode(predictions, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        scores = rouge.compute(
            predictions=decoded_predictions,
            references=decoded_labels,
            use_stemmer=True,
        )
        return {key: round(value, 4) for key, value in scores.items()}

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        generation_max_length=args.max_target_length,
        fp16=False,
        logging_steps=25,
        save_total_limit=2,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        tokenizer=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Saved fine-tuned summarizer to {args.output_dir}")


if __name__ == "__main__":
    main()
