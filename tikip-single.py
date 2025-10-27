from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import json, time, re, sys, itertools

inp_path = Path(sys.argv[1])
out_path = inp_path.with_suffix(".json")
log_path = inp_path.with_suffix(".log")

log_file = open(log_path, "w", encoding="utf-8")
def log(msg="", end="\n", flush=True):
    sys.stdout.write(msg + ("" if end == "" else end))
    if flush: sys.stdout.flush()
    log_file.write(msg + ("" if end == "" else end))
    if flush: log_file.flush()

log(f"Input: {inp_path}")
log(f"Output: {out_path}")
log(f"Log: {log_path}")

opts = Options()
opts.add_argument("--headless=new")
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 30)

driver.get("https://tikip.us/")

def username_from_link(link):
    m = re.search(r"tiktok\.com/@([^/?#]+)", link.strip())
    return m.group(1) if m else link.strip().lstrip("@")

def wait_for_results_with_spinner():
    spinner = itertools.cycle("|/-\\")
    start = time.time()
    while True:
        try:
            card = driver.find_element(By.ID, "results-card")
            if card.is_displayed():
                nick = driver.find_element(By.ID, "nickname").text.strip()
                user = driver.find_element(By.ID, "username").text.strip()
                if nick or user:
                    sys.stdout.write("\rLoaded results...           \n")
                    sys.stdout.flush()
                    log("Loaded results...")
                    return
        except:
            pass
        elapsed = int(time.time() - start)
        sys.stdout.write(f"\rWaiting for results {next(spinner)}  {elapsed}s")
        sys.stdout.flush()
        log(f"Waiting for results... {elapsed}s", end="\r")
        time.sleep(0.1)

def txt(eid): return driver.find_element(By.ID, eid).text.strip()
def attr(eid, name): return driver.find_element(By.ID, eid).get_attribute(name) or ""

def normalize_bio_link(href):
    if not href or href.strip() == "" or href.strip() == "https://tikip.us/#":
        return "N/A"
    return href

lines = [ln for ln in inp_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
total = len(lines)
log(f"Found {total} lines")

out = []
for i, line in enumerate(lines, 1):
    uname = username_from_link(line)
    log(f"[{i}/{total}] Processing @{uname}")

    inp = wait.until(EC.presence_of_element_located((By.ID, "username-input")))
    inp.clear()
    inp.send_keys(uname)
    driver.find_element(By.ID, "search-button").click()

    wait_for_results_with_spinner()
    log("Stabilizing 3s...")
    time.sleep(3)  # shortened stabilization [web:98][web:101]

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
    out.append({
        "input_username": uname,
        "profile_header": profile_header,
        "avatar": avatar,
        "bio": bio,
        "profile_details": profile_details,
        "stats": stats
    })
    log(f"[{i}/{total}] Done")

out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
log(f"Wrote {out_path}")
driver.quit()
log_file.close()
