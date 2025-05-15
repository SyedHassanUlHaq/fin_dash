import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSONS_DIR = BASE_DIR / 'JSONS'

def get_available_categories():
    return [d.name for d in JSONS_DIR.iterdir() if d.is_dir()]

def get_equity_tickers_by_category(category):
    category_dir = JSONS_DIR / category
    if not category_dir.exists():
        return []
    return [
        f.name.split('_')[0]  # Extract "ADBE" from "ADBE_investor_relations_sec.json"
        for f in category_dir.glob('*.json')
    ]

def load_json_data(category, ticker):
    category_dir = JSONS_DIR / category
    for json_file in category_dir.glob(f'{ticker}_*.json'):
        with open(json_file) as f:
            return json.load(f)
    return None