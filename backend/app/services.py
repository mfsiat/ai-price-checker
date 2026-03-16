import json
from pathlib import Path

PRICING_FILE = Path(__file__).parent / "pricing.json"


def load_pricing():
    with open(PRICING_FILE) as f:
        return json.load(f)
