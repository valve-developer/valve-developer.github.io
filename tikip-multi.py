from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json, time, re, sys, threading

inp_path = Path(sys.argv[1])
out_path = inp_path.with_suffix(".json")
log_path = inp_path.with_suffix(".log")

# Thread-safe tee logger to console and file [web:92][web:131]
log_lock = threading.Lock()
log_file = open(log_path, "w", encoding="utf-8")
def log(msg="", end="\n"):
    with log_lock:
        sys.stdout.write(msg + end)
        sys.stdout.flush()
        log_file.write(msg + end)
        log_file.flush()

log(f"Input: {inp_path}")
log(f"Output: {out_path}")
log(f"Log: {log_path}")

def username_from_link(link):
    m = re.search(r"tiktok\\.com/@([^/?#]+)", link.strip())
    return m.group(1) if m else link.strip().lstrip("@")

def normalize_bio_link(href):
    if not href or href.strip() == "" or href.strip() == "https://tikip.us/#":
        return "N/A"
    return href

def scrape_one(uname):
    tid = threading.current_thread().name
    log(f"[{tid}] Start @{uname}")  # per-task start line [web:130]
    opts = Options()
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)
    wait = WebDriverWait(driver, 30)

    driver.get("https://tikip.us/")
    inp = wait.until(EC.presence_of_element_located((By.ID, "username-input")))
    inp.clear()
    inp.send_keys(uname)
    driver.find_element(By.ID, "search-button").click()

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "results-card")))
    WebDriverWait(driver, 30).until(lambda d: d.find_element(By.ID, "nickname").text.strip() != "" or
                                         d.find_element(By.ID, "username").text.strip() != "")
    time.sleep(3)

    def txt(eid): return driver.find_element(By.ID, eid).text.strip()
    def attr(eid, name): return driver.find_element(By.ID, eid).get_attribute(name) or ""

    profile_header = {
        "nickname": txt("nickname"),
        "username": txt("username"),
        "profile_link": attr("profile-link", "href"),
    }
    avatar = {
        "avatar_src": attr("avatar", "src"),
        "download_avatar_link": attr("download-avatar-link", "href"),
    }
    raw_bio_link = attr("bio-link", "href")
    bio = {
        "about": txt("about"),
        "bio_link": normalize_bio_link(raw_bio_link),
    }
    profile_details = {
        "user_id": txt("user-id"),
        "country": txt("country"),
        "language": txt("language"),
        "account_created": txt("created-date"),
        "nickname_modified": txt("nickname-modified"),
        "username_modified": txt("username-modified"),
    }
    stats = {
        "followers": txt("followers"),
        "following": txt("following"),
        "hearts": txt("hearts"),
        "videos": txt("videos"),
        "friends": txt("friends"),
    }

    driver.quit()
    log(f"[{tid}] Done @{uname}")  # per-task end line [web:130]
    return {
        "input_username": uname,
        "profile_header": profile_header,
        "avatar": avatar,
        "bio": bio,
        "profile_details": profile_details,
        "stats": stats
    }

lines = [ln for ln in inp_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
usernames = [username_from_link(ln) for ln in lines]
log(f"Found {len(usernames)} usernames")

out = []
max_workers = 10  # adjust to your machine
with ThreadPoolExecutor(max_workers=max_workers) as ex:
    futures = {ex.submit(scrape_one, u): u for u in usernames}
    for fut in as_completed(futures):
        out.append(fut.result())

# Preserve input order
order = {u: i for i, u in enumerate(usernames)}
out.sort(key=lambda x: order.get(x["input_username"], 10**9))

out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
log(f"Wrote {out_path}")
log_file.close()
