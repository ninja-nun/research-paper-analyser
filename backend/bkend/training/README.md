# Summarizer Training

Recommended Kaggle dataset:

```powershell
kaggle datasets download -d syndri224/arxiv-summary-dataset -p data/kaggle/arxiv-summary-dataset --unzip
```

Train a small first pass:

```powershell
..\.venv\Scripts\python training\train_summarizer.py --data-dir data\kaggle\arxiv-summary-dataset --train-samples 2000 --eval-samples 200 --epochs 1
```

Use the saved checkpoint by setting:

```powershell
$env:USE_TRANSFORMER_SUMMARY="1"
$env:SUMMARIZER_MODEL="training/checkpoints/bart-arxiv"
```
