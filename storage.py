# storage.py

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

BASE = Path(__file__).parent

# CSV Paths
GROCERY_CSV = BASE / "groceries.csv"
RECIPE_CSV = BASE / "recipes.csv"
PURCHASES_CSV = BASE / "user_purchases.csv"  # created/updated by app

DATE_FMT = "%Y-%m-%d"


def load_groceries() -> Dict[str, int]:
    """Return mapping item -> shelf_life_days"""
    d = {}
    if not GROCERY_CSV.exists():
        return d

    with open(GROCERY_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            item = r["item"].strip().lower()
            try:
                d[item] = int(r["shelf_life_days"])
            except Exception:
                continue
    return d


def load_recipes() -> Dict[str, List[str]]:
    """Return mapping recipe_name -> list of ingredients"""
    recipes = {}
    if not RECIPE_CSV.exists():
        return recipes

    with open(RECIPE_CSV, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            name = row[0].strip()
            ingredients = [
                c.strip().lower()
                for c in row[1:7]
                if c and c.strip()
            ]
            recipes[name] = ingredients
    return recipes



def save_user_purchase(item: str, purchase_date: str):
    """Append a single purchase row. purchase_date: YYYY-MM-DD"""
    new_file = not PURCHASES_CSV.exists()

    with open(PURCHASES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item", "purchase_date"])
        if new_file:
            writer.writeheader()
        writer.writerow({
            "item": item.lower(),
            "purchase_date": purchase_date
        })


def load_user_purchases() -> Dict[str, datetime]:
    """
    Returns dict: item -> most recent purchase datetime.
    If item purchased multiple times, keep latest date.
    """
    if not PURCHASES_CSV.exists():
        return {}

    items = {}

    with open(PURCHASES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            item = r["item"].strip().lower()
            try:
                dt = datetime.strptime(r["purchase_date"], DATE_FMT)
            except Exception:
                continue

            if item not in items or dt > items[item]:
                items[item] = dt

    return items



def get_expiring_items(check_date: datetime,
                       groceries: Dict[str, int],
                       purchases: Dict[str, datetime],
                       within_days: int = 2
                       ) -> Tuple[List[Tuple[str, datetime]],
                                  List[Tuple[str, datetime]]]:
    """
    Returns:
    - expiring: list of (item, expiry_date)
    - expired: list of (item, expiry_date)

    Expired items are NOT included in expiring list.
    """

    expiring = []
    expired = []

    for item, p_date in purchases.items():
        shelf = groceries.get(item)
        if shelf is None:
            continue

        expiry = p_date + timedelta(days=shelf)

        if expiry < check_date:
            # Already expired
            expired.append((item, expiry))

        elif check_date <= expiry <= check_date + timedelta(days=within_days):
            # Expiring soon
            expiring.append((item, expiry))

    expiring.sort(key=lambda x: x[1])
    expired.sort(key=lambda x: x[1])

    return expiring, expired



def find_recipes_using_items(expiring_items: List[str],
                             expired_items: List[str],
                             user_items: List[str],
                             recipes: Dict[str, List[str]]
                             ) -> Tuple[List[Dict], List[Dict]]:
    """
    Returns (possible_recipes, recipes_need_buy)

    possible_recipes: recipes where:
        - ALL ingredients are available
        - At least ONE ingredient is expiring soon
        - NO ingredient is expired

    recipes_need_buy: recipes that could be cooked (use at least one expiring item)
                      but user is missing some fresh ingredients.
    """

    possible = []
    need_buy = []

    user_set = set(i.lower() for i in user_items)
    exp_set = set(i.lower() for i in expiring_items)
    expired_set = set(i.lower() for i in expired_items)

    for rname, ings in recipes.items():

        # Skip recipes that include ANY expired ingredient
        if expired_set.intersection(ings):
            continue

        # Only consider recipes using at least one expiring ingredient
        if not exp_set.intersection(ings):
            continue

        missing = [i for i in ings if i not in user_set]

        if not missing:
            possible.append({"recipe": rname, "ingredients": ings})
        else:
            need_buy.append({
                "recipe": rname,
                "ingredients": ings,
                "missing": missing
            })

    return possible, need_buy
