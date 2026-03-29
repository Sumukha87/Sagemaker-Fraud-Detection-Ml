"""
generate_data.py — Creates a synthetic fraud detection dataset.

5,000 credit card transactions with ~3% fraud rate.
Saved to data/fraud_dataset.csv.

Run: python scripts/generate_data.py
"""

import os
import random

import numpy as np
import pandas as pd

SEED = 42
N_ROWS = 5000
FRAUD_RATE = 0.03
OUTPUT_PATH = "data/fraud_dataset.csv"

MERCHANT_CATEGORIES = ["retail", "food", "travel", "entertainment", "gas", "online", "atm"]


def generate_transaction(is_fraud: bool, rng: np.random.Generator) -> dict:
    if is_fraud:
        return {
            "amount": round(rng.exponential(scale=400), 2),  # larger amounts
            "time_of_day": int(rng.choice(range(1, 6))),  # late night / early morning
            "day_of_week": int(rng.integers(0, 7)),
            "merchant_category": rng.choice(["online", "atm", "travel"]),
            "cardholder_age": int(rng.integers(18, 80)),
            "num_transactions_1h": int(rng.integers(5, 20)),  # many transactions in short window
            "distance_from_home": round(rng.uniform(100, 5000), 1),  # far from home
            "is_fraud": 1,
        }
    else:
        return {
            "amount": round(rng.exponential(scale=80), 2),
            "time_of_day": int(rng.integers(8, 22)),
            "day_of_week": int(rng.integers(0, 7)),
            "merchant_category": rng.choice(MERCHANT_CATEGORIES),
            "cardholder_age": int(rng.integers(18, 80)),
            "num_transactions_1h": int(rng.integers(0, 4)),
            "distance_from_home": round(rng.uniform(0, 50), 1),
            "is_fraud": 0,
        }


def main():
    os.makedirs("data", exist_ok=True)
    rng = np.random.default_rng(SEED)

    n_fraud = int(N_ROWS * FRAUD_RATE)
    n_legit = N_ROWS - n_fraud

    rows = [generate_transaction(True, rng) for _ in range(n_fraud)] + [
        generate_transaction(False, rng) for _ in range(n_legit)
    ]

    df = pd.DataFrame(rows)
    df.insert(0, "transaction_id", [f"txn_{i:05d}" for i in range(N_ROWS)])

    # Shuffle so fraud isn't all at the top
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    # Introduce some realistic nulls (~2%) in non-critical columns
    null_mask = rng.random(size=len(df)) < 0.02
    df.loc[null_mask, "distance_from_home"] = np.nan

    df.to_csv(OUTPUT_PATH, index=False)

    fraud_count = df["is_fraud"].sum()
    print(f"Generated {len(df)} transactions → {OUTPUT_PATH}")
    print(f"  Fraud: {fraud_count} ({fraud_count/len(df)*100:.1f}%)")
    print(f"  Legit: {len(df) - fraud_count} ({(len(df) - fraud_count)/len(df)*100:.1f}%)")
    print(f"  Nulls in distance_from_home: {df['distance_from_home'].isna().sum()}")


if __name__ == "__main__":
    main()
