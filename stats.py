#!/usr/bin/env python3
import sys
import json
import os
import html

def to_int(val):
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip()
    # Remove commas and spaces (e.g., "32,439")
    s = s.replace(",", "").replace(" ", "")
    if s == "" or s.lower() == "n/a":
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0

def get(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def generate_html(title, rows, totals):
    # Minimal, clean HTML
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --bg: #0f172a;
    --card: #111827;
    --text: #e5e7eb;
    --muted: #9ca3af;
    --accent: #22c55e;
    --border: #1f2937;
  }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Inter, Helvetica, Arial, sans-serif;
    background: linear-gradient(180deg, #0b1020, #0b1428);
    color: var(--text);
  }}
  .container {{
    max-width: 1000px;
    margin: 40px auto;
    padding: 0 16px;
  }}
  .title {{
    font-size: 28px;
    margin: 0 0 18px 0;
    font-weight: 700;
  }}
  .subtitle {{
    color: var(--muted);
    margin: 0 0 24px 0;
    font-size: 14px;
  }}
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
  }}
  .card {{
    background: rgba(17,24,39,0.6);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    backdrop-filter: blur(6px);
  }}
  .metric {{
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 6px;
  }}
  .value {{
    font-size: 22px;
    font-weight: 700;
    color: var(--accent);
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    background: rgba(17,24,39,0.5);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
  }}
  th, td {{
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    font-size: 14px;
  }}
  thead th {{
    background: rgba(31,41,55,0.6);
    position: sticky;
    top: 0;
  }}
  tbody tr:hover {{
    background: rgba(31,41,55,0.25);
  }}
  .note {{
    margin-top: 14px;
    font-size: 12px;
    color: var(--muted);
  }}
</style>
</head>
<body>
<div class="container">
  <h1 class="title">{html.escape(title)}</h1>
  <p class="subtitle">Combined totals are computed from the stats fields of each entry in this JSON.</p>

  <div class="cards">
    <div class="card">
      <div class="metric">Total Followers</div>
      <div class="value">{totals['followers']:,}</div>
    </div>
    <div class="card">
      <div class="metric">Total Following</div>
      <div class="value">{totals['following']:,}</div>
    </div>
    <div class="card">
      <div class="metric">Total Hearts</div>
      <div class="value">{totals['hearts']:,}</div>
    </div>
    <div class="card">
      <div class="metric">Total Videos</div>
      <div class="value">{totals['videos']:,}</div>
    </div>
    <div class="card">
      <div class="metric">Total Friends</div>
      <div class="value">{totals['friends']:,}</div>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Username</th>
        <th>Nickname</th>
        <th>Followers</th>
        <th>Following</th>
        <th>Hearts</th>
        <th>Videos</th>
        <th>Friends</th>
      </tr>
    </thead>
    <tbody>
"""
    body_rows = []
    for r in rows:
        body_rows.append(
            f"<tr>"
            f"<td>{html.escape(r['username'])}</td>"
            f"<td>{html.escape(r['nickname'])}</td>"
            f"<td>{r['followers']:,}</td>"
            f"<td>{r['following']:,}</td>"
            f"<td>{r['hearts']:,}</td>"
            f"<td>{r['videos']:,}</td>"
            f"<td>{r['friends']:,}</td>"
            f"</tr>"
        )

    foot = f"""    </tbody>
  </table>

  <p class="note">Notes: Missing or non-numeric values are treated as 0. Numbers in the source like "32,439" are parsed correctly.</p>
</div>
</body>
</html>"""
    return head + "\n".join(body_rows) + "\n" + foot

def main():
    if len(sys.argv) < 2:
        print("Drag a JSON file onto this script, or run: python generate_stats_html.py yourfile.json")
        sys.exit(1)

    in_path = sys.argv[1]
    base, ext = os.path.splitext(in_path)
    out_path = base + ".html"

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected the JSON to be a list of profile objects")

    rows = []
    totals = {"followers": 0, "following": 0, "hearts": 0, "videos": 0, "friends": 0}

    for item in data:
        username = get(item, "profile_header", "username", default="") or get(item, "input_username", default="")
        nickname = get(item, "profile_header", "nickname", default="")

        stats = item.get("stats", {}) if isinstance(item, dict) else {}
        followers = to_int(stats.get("followers"))
        following = to_int(stats.get("following"))
        hearts    = to_int(stats.get("hearts"))
        videos    = to_int(stats.get("videos"))
        friends   = to_int(stats.get("friends"))

        rows.append({
            "username": username or "",
            "nickname": nickname or "",
            "followers": followers,
            "following": following,
            "hearts": hearts,
            "videos": videos,
            "friends": friends,
        })

        totals["followers"] += followers
        totals["following"] += following
        totals["hearts"]    += hearts
        totals["videos"]    += videos
        totals["friends"]   += friends

    title = f"Combined statistics for {os.path.basename(in_path)}"
    html_doc = generate_html(title, rows, totals)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
