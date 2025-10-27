#!/usr/bin/env python3
import os
import json
from html import escape

FOLDERS = [
    "bbb",
    "bij1",
    "bvnl",
    "cda",
    "d66",
    "denk",
    "fvd",
    "glpvda",
    "ja21",
    "lp",
    "nlplan",
    "nsc",
    "pp",
    "pvdd",
    "pvv",
    "sp",
    "volt",
    "vredevoordieren",
    "vvd",
    "50plus",
    "cu",
]

def parse_views(value):
    """
    Convert the 'views' field to an integer.
    Accepts ints, floats, numeric strings, strings with commas, and k/m suffixes.
    """
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    s = str(value).strip()
    s = s.replace(",", "").replace(" ", "")
    if not s:
        return 0
    low = s.lower()
    try:
        if low.endswith('k'):
            return int(float(low[:-1]) * 1_000)
        if low.endswith('m'):
            return int(float(low[:-1]) * 1_000_000)
        return int(float(low))
    except ValueError:
        return 0

def extract_items(data):
    """
    Normalize supported JSON shapes into a list of {url, views}.
    Supports:
    - List of objects: [{"url": "...", "views": "123"}]
    - Dict with 'items' key: {"items": [ ... ]}
    - Dict with 'data' key similar to above
    """
    items = []
    if isinstance(data, list):
        iterable = data
    elif isinstance(data, dict):
        if isinstance(data.get("items"), list):
            iterable = data["items"]
        elif isinstance(data.get("data"), list):
            iterable = data["data"]
        else:
            return items
    else:
        return items

    for obj in iterable:
        if not isinstance(obj, dict):
            continue
        url = obj.get("url")
        views_raw = obj.get("views")
        if url is None and "link" in obj:
            url = obj.get("link")
        if url is None:
            continue
        items.append({"url": str(url), "views": parse_views(views_raw)})
    return items

def read_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def sum_views_in_folder(folder):
    total = 0
    file_counts = 0
    for root, _, files in os.walk(folder):
        for name in files:
            if not name.lower().endswith(".json"):
                continue
            file_counts += 1
            full = os.path.join(root, name)
            data = read_json_file(full)
            if data is None:
                continue
            for item in extract_items(data):
                total += item["views"]
    return total, file_counts

def main():
    grand_total = 0
    per_folder = {}

    for folder in FOLDERS:
        if not os.path.isdir(folder):
            per_folder[folder] = {"total": 0, "files": 0, "exists": False}
            continue
        subtotal, files = sum_views_in_folder(folder)
        per_folder[folder] = {"total": subtotal, "files": files, "exists": True}
        grand_total += subtotal

    # Print a concise report
    print("Per-folder totals:")
    for folder in FOLDERS:
        info = per_folder[folder]
        status = "OK" if info["exists"] else "MISSING"
        print(f"- {folder}: {info['total']:,} views from {info['files']} files [{status}]")
    print(f"\nGrand total views: {grand_total:,}")

if __name__ == "__main__":
    main()
