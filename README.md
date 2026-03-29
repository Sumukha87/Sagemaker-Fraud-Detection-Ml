# Fraud Detection ML Pipeline

A complete, end-to-end machine learning system that detects fraudulent credit card transactions in real time — built entirely on local infrastructure using Docker, Python, and AWS-compatible APIs.

---

## What This System Does

 The bank needs a system that:

1. Ingests raw transaction records (amount, time, merchant, cardholder features) into S3
2. Engineers features from raw data — handles nulls, encodes categories, scales numbers, addresses class imbalance (only ~3% of transactions are fraud)
3. Trains an XGBoost classifier that learns the fraud pattern
4. Tunes the model automatically to find optimal hyperparameters
5. Deploys a real-time endpoint that scores live incoming transactions
6. Monitors the model and raises alarms when fraud patterns drift over time

This is a real production ML architecture that companies build on AWS SageMaker.

---

## Architecture

```
Your Machine (WSL2 / Linux / Mac)
│
├── LocalStack (port 4566)    — emulates: S3, SageMaker, IAM, CloudWatch, Glue, SNS
├── MLflow     (port 5000)    — emulates: SageMaker Experiments + Model Registry
│
└── Python scripts (boto3 + SageMaker SDK)
    ├── Phase 1 — Data ingestion & feature engineering
    ├── Phase 2 — Model training, HPO, model registry
    ├── Phase 3 — Deployment: real-time endpoint, batch transform, pipelines
    └── Phase 4 — Monitoring: drift detection, CloudWatch alarms, IAM hardening
```

All boto3 code is production-identical — only `endpoint_url` points to localhost instead of AWS.

---

## Quick Start

### Prerequisites

```bash
# Docker
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER && newgrp docker

# Python dependencies
pip install -r requirements.txt
```

### Fake AWS credentials (one-time)

```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << 'EOF'
[default]
aws_access_key_id = fake
aws_secret_access_key = fake
EOF

cat > ~/.aws/config << 'EOF'
[default]
region = us-east-1
EOF
```

### Start local infrastructure

**Option A — LocalStack (full-featured, needs free account token)**
```bash
cp .env.example .env
# edit .env and paste your LOCALSTACK_AUTH_TOKEN
docker compose up -d
```

**Option B — Floci (zero account, zero token)**
```bash
docker compose -f docker-compose.floci.yml up -d
```

### Verify everything is running

```bash
python scripts/verify_setup.py
```

### Generate synthetic fraud dataset

```bash
python scripts/generate_data.py
```

---

## Running the Pipeline

Run phases in order — each phase writes a JSON file that the next phase reads.

```bash
# Phase 1 — Data
python src/phase1_data/01_s3_ingestion.py        # uploads data to S3, writes data/s3_uris.json
python src/phase1_data/02_feature_engineering.py  # transforms features, updates s3_uris.json
python src/phase1_data/03_bias_detection.py       # checks class imbalance and bias metrics

# Phase 2 — Training
python src/phase2_training/01_train_xgboost.py         # trains model, writes data/training_results.json
python src/phase2_training/02_hyperparameter_tuning.py  # HPO with Optuna, updates training_results.json
python src/phase2_training/03_model_registry.py         # registers best model in MLflow registry

# Phase 3 — Deployment
python src/phase3_deploy/01_realtime_endpoint.py  # creates endpoint, writes data/deployment_info.json
python src/phase3_deploy/02_batch_transform.py    # scores batch of transactions
python src/phase3_deploy/03_pipeline.py           # wires phases into a SageMaker Pipeline

# Phase 4 — Monitoring
python src/phase4_monitor/01_monitoring_security.py  # Evidently drift detection
python src/phase4_monitor/02_cloudwatch_alarms.py    # CloudWatch alarm → SNS retraining trigger
python src/phase4_monitor/03_iam_deep_dive.py        # IAM roles and least-privilege policies
```

Or use make:

```bash
make phase1   # run all phase 1 scripts
make phase2   # run all phase 2 scripts
make all      # run entire pipeline
```

---

## Project Structure

```
fraud-detection-pipeline/
│
├── docker-compose.yml          — LocalStack + MLflow
├── docker-compose.floci.yml    — Floci + MLflow (no auth token)
├── Makefile
├── requirements.txt
├── .env.example                — copy to .env, add your LocalStack token
├── .gitignore
│
├── scripts/
│   ├── generate_data.py        — generates 5,000-row synthetic fraud dataset
│   └── verify_setup.py         — checks LocalStack + MLflow are alive
│
├── src/
│   ├── phase1_data/            — Data ingestion and preparation
│   │   ├── 01_s3_ingestion.py
│   │   ├── 02_feature_engineering.py
│   │   └── 03_bias_detection.py
│   │
│   ├── phase2_training/        — Model training and evaluation
│   │   ├── 01_train_xgboost.py
│   │   ├── 02_hyperparameter_tuning.py
│   │   └── 03_model_registry.py
│   │
│   ├── phase3_deploy/          — Deployment and orchestration
│   │   ├── 01_realtime_endpoint.py
│   │   ├── 02_batch_transform.py
│   │   └── 03_pipeline.py
│   │
│   └── phase4_monitor/         — Monitoring, alerting, security
│       ├── 01_monitoring_security.py
│       ├── 02_cloudwatch_alarms.py
│       └── 03_iam_deep_dive.py
│
├── data/                       — generated at runtime (gitignored)
│   ├── fraud_dataset.csv
│   ├── s3_uris.json            — written by phase1, read by phase2
│   ├── training_results.json   — written by phase2, read by phase3
│   └── deployment_info.json    — written by phase3, read by phase4
│
└── notebooks/
    └── exam_concepts.md        — concept reference cheat sheet
```

---

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| AWS emulation | LocalStack | Full S3/SageMaker/IAM/CloudWatch API compatibility |
| Experiment tracking | MLflow | Tracks runs, metrics, model versions |
| ML framework | XGBoost | Industry-standard gradient boosting for tabular fraud data |
| HPO | Optuna | Bayesian hyperparameter optimization |
| Feature engineering | pandas + scikit-learn | Standard preprocessing pipeline |
| Drift detection | Evidently AI | Production-grade data drift and model quality monitoring |
| Formatting | black + isort | Auto-applied on every file save |

---

## Data Schema

Each row represents one credit card transaction:

| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | string | Unique transaction identifier |
| `amount` | float | Transaction amount in USD |
| `time_of_day` | int | Hour of day (0–23) |
| `day_of_week` | int | Day (0 = Monday) |
| `merchant_category` | string | MCG code category (retail, food, travel, etc.) |
| `cardholder_age` | int | Age of cardholder |
| `num_transactions_1h` | int | Transactions by this card in last 1 hour |
| `distance_from_home` | float | Distance of transaction from home location (km) |
| `is_fraud` | int | Target label: 1 = fraud, 0 = legitimate |

Class balance: ~97% legitimate, ~3% fraud.
