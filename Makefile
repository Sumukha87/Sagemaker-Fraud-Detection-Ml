.PHONY: up down phase1 phase2 phase3 phase4 all data verify clean

# ── Infrastructure ──────────────────────────────────────────────────────────

up:
	docker compose up -d
	@echo "LocalStack → http://localhost:4566"
	@echo "MLflow     → http://localhost:5000"

up-floci:
	docker compose -f docker-compose.floci.yml up -d

down:
	docker compose down

# ── Setup ────────────────────────────────────────────────────────────────────

data:
	python scripts/generate_data.py

verify:
	python scripts/verify_setup.py

# ── Pipeline phases ───────────────────────────────────────────────────────────

phase1: data
	python src/phase1_data/01_s3_ingestion.py
	python src/phase1_data/02_feature_engineering.py
	python src/phase1_data/03_bias_detection.py

phase2: phase1
	python src/phase2_training/01_train_xgboost.py
	python src/phase2_training/02_hyperparameter_tuning.py
	python src/phase2_training/03_model_registry.py

phase3: phase2
	python src/phase3_deploy/01_realtime_endpoint.py
	python src/phase3_deploy/02_batch_transform.py
	python src/phase3_deploy/03_pipeline.py

phase4: phase3
	python src/phase4_monitor/01_monitoring_security.py
	python src/phase4_monitor/02_cloudwatch_alarms.py
	python src/phase4_monitor/03_iam_deep_dive.py

all: phase1 phase2 phase3 phase4

# ── Housekeeping ──────────────────────────────────────────────────────────────

clean:
	rm -f data/*.json data/*.csv
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
