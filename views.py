#!/usr/bin/env python3
import os
import json
from glob import glob
from html import escape

def parse_views(value):
    """
    Convert the 'views' field to an integer.
    Accepts ints, floats, numeric strings, and strings with commas or k/m suffixes.
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
    # suffixes like '1.4m', '25k'
    low = s.lower()
    try:
        if low.endswith('k'):
            return int(float(low[:-1]) * 1_000)
        if low.endswith('m'):
            return int(float(low[:-1]) * 1_000_000)
        return int(float(low))
    except ValueError:
        return 0

def load_items_from_json(filepath):
    """
    Expect a JSON array of objects like:
    [{"views": "181600", "url": "https://..."}]
    Returns a list of dicts { "url": str, "views": int, "source": filename }.
    """
    items = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return items

    if not isinstance(data, list):
        return items

    base = os.path.basename(filepath)
    for obj in data:
        if not isinstance(obj, dict):
            continue
        url = obj.get("url")
        views_raw = obj.get("views")
        if not url:
            continue
        views = parse_views(views_raw)
        items.append({"url": str(url), "views": views, "source": base})
    return items

def build_html(total_views, items, top_n=100):
    """
    Build an HTML overview showing the total and the most viewed links.
    """
    rows = []
    for i, it in enumerate(items[:top_n], start=1):
        rows.append(
            f"<tr>"
            f"<td>{i}</td>"
            f"<td><a href=\"{escape(it['url'])}\" target=\"_blank\" rel=\"noopener noreferrer\">{escape(it['url'])}</a></td>"
            f"<td>{it['views']:,}</td>"
            f"<td>{escape(it['source'])}</td>"
            f"</tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>TikTok Overview</title>
<style>
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 2rem; }}
  h1, h2 {{ margin: 0.5rem 0; }}
  .total {{ font-size: 1.25rem; margin: 1rem 0; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; }}
  th {{ background: #f5f5f5; text-align: left; }}
  tr:nth-child(even) {{ background: #fafafa; }}
  .muted {{ color: #666; font-size: 0.9rem; }}
</style>
</head>
<body>
  <h1>TikTok Overview</h1>
  <div class="total">Total views across all JSON files: <strong>{total_views:,}</strong></div>

  <h2>Most viewed links</h2>
  <p class="muted">Top {min(top_n, len(items))} by view count.</p>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>URL</th>
        <th>Views</th>
        <th>Source file</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>"""
    return html

def main():
    # Pick up every .json file in the current directory
    json_files = sorted(glob("*.json"))

    all_items = []
    for fp in json_files:
        all_items.extend(load_items_from_json(fp))

    total_views = sum(it["views"] for it in all_items)
    all_items.sort(key=lambda x: x["views"], reverse=True)

    html = build_html(total_views, all_items, top_n=100)
    out_path = "overview.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote {out_path} with total views = {total_views:,} and {len(all_items)} entries.")

if __name__ == "__main__":
    main()
