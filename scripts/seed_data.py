"""Data setup and validation script."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def validate_data():
    print("Validating synthetic datasets...")
    synth_dir = DATA_DIR / "synthetic"
    files = ["referrals.json", "patients.json", "providers.json", "specialists.json"]

    for fn in files:
        fp = synth_dir / fn
        if not fp.exists():
            print(f"FAILED: {fn} missing!")
            return False
        with open(fp, "r") as f:
            data = json.load(f)
            print(f"✓ {fn}: {len(data)} records loaded.")

    print("All synthetic datasets validated successfully!")
    return True


if __name__ == "__main__":
    validate_data()
