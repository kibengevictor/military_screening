"""resave_pickles.py

Utility to recreate and save scaler and label encoder artifacts from a CSV file.

Usage examples:
    # Fit scaler on feature columns and label encoder on label column
    python resave_pickles.py --csv data/training.csv --features feat1 feat2 feat3 --label target

    # Specify output paths
    python resave_pickles.py --csv data/training.csv --features feat1 feat2 feat3 --label target \
        --scaler-out scaler.pkl --encoder-out label_encoder.pkl

Notes:
 - The script uses joblib to write pickles compatible with scikit-learn.
 - Run this in an environment with the scikit-learn version you plan to use in production.
 - Do NOT run this on untrusted data without checking contents.
"""
import argparse
from pathlib import Path
import sys

try:
    import pandas as pd
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    import joblib
except Exception as e:
    print("Missing dependencies. Ensure pandas, scikit-learn and joblib are installed.")
    raise


def parse_args():
    p = argparse.ArgumentParser(description="Recreate scaler and label encoder from CSV")
    p.add_argument("--csv", required=True, help="Path to training CSV file")
    p.add_argument("--features", required=True, nargs="+", help="List of feature column names")
    p.add_argument("--label", required=True, help="Label/target column name")
    p.add_argument("--scaler-out", default="scaler.pkl", help="Output path for scaler (joblib)")
    p.add_argument("--encoder-out", default="label_encoder.pkl", help="Output path for label encoder (joblib)")
    return p.parse_args()


def main():
    args = parse_args()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        sys.exit(2)

    df = pd.read_csv(csv_path)

    missing = [c for c in args.features + [args.label] if c not in df.columns]
    if missing:
        print(f"Missing columns in CSV: {missing}")
        sys.exit(2)

    X = df[args.features]
    y = df[args.label]

    print(f"Fitting StandardScaler on features: {args.features} (n={len(X)})")
    scaler = StandardScaler()
    scaler.fit(X)

    print(f"Fitting LabelEncoder on label: {args.label} (n={len(y)})")
    le = LabelEncoder()
    le.fit(y)

    print(f"Writing scaler to: {args.scaler_out}")
    joblib.dump(scaler, args.scaler_out)

    print(f"Writing label encoder to: {args.encoder_out}")
    joblib.dump(le, args.encoder_out)

    print("Done. Replace the production pickles with these files and redeploy.")


if __name__ == '__main__':
    main()
