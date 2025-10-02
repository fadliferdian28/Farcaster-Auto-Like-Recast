import requests
import time
import random
import csv
from pathlib import Path

# === CONFIG ===
TOKENS_FILE = "tokens.txt"     # 1 token per baris (boleh "Bearer <tok>" atau "<tok>")
HASHES_FILE = "hashes.txt"     # 1 cast hash per baris
OUTPUT_CSV = "results.csv"

DELAY_MIN = 0.8    # detik minimal antar request
DELAY_MAX = 1.8    # detik maksimal antar request
MAX_RETRIES = 5
BACKOFF_BASE = 1.5  # multiplier untuk exponential backoff

LIKE_URL = "https://client.farcaster.xyz/v2/cast-likes"
RECAST_URL = "https://client.farcaster.xyz/v2/recasts"

# === HELPERS ===
def load_lines(path):
    p = Path(path)
    if not p.exists():
        print(f"File tidak ditemukan: {path}")
        return []
    with p.open("r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    return lines

def normalize_token(line):
    if line.lower().startswith("bearer "):
        return line
    return "Bearer " + line

def make_session(token):
    s = requests.Session()
    s.headers.update({
        "authorization": token,
        "content-type": "application/json",
        "user-agent": "farcaster-bot/1.0"
    })
    return s

def request_with_retries(session, method, url, json_payload):
    attempt = 0
    while attempt <= MAX_RETRIES:
        try:
            resp = session.request(method, url, json=json_payload, timeout=15)
        except requests.RequestException as e:
            # network-ish error, retry
            attempt += 1
            sleep_for = (BACKOFF_BASE ** attempt) * 0.5 + random.random()
            print(f"Network error: {e}. Retry {attempt}/{MAX_RETRIES} after {sleep_for:.1f}s")
            time.sleep(sleep_for)
            continue

        if resp.status_code in (200, 201, 204):
            return resp
        if resp.status_code == 401:
            # Unauthorized: no point retrying many times
            print("401 Unauthorized - token mungkin invalid/expired.")
            return resp
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            # rate-limited or server error: retry with backoff
            attempt += 1
            # if 429, try to respect Retry-After header first
            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                try:
                    sleep_for = float(retry_after) + random.random()
                except:
                    sleep_for = (BACKOFF_BASE ** attempt) + random.random()
            else:
                sleep_for = (BACKOFF_BASE ** attempt) + random.random()
            print(f"{resp.status_code} from server. Retry {attempt}/{MAX_RETRIES} after {sleep_for:.1f}s")
            time.sleep(sleep_for)
            continue
        # other status codes (4xx) -> return
        return resp
    return None

def like_and_recast(session, cast_hash):
    payload = {"castHash": cast_hash}
    # LIKE
    like_resp = request_with_retries(session, "PUT", LIKE_URL, payload)
    # small jitter
    time.sleep(random.uniform(0.08, 0.2))
    # RECAST
    recast_resp = request_with_retries(session, "PUT", RECAST_URL, payload)
    return like_resp, recast_resp

# === MAIN ===
def main():
    raw_tokens = load_lines(TOKENS_FILE)
    if not raw_tokens:
        print("Tidak ada token. Pastikan tokens.txt berisi token (satu per baris).")
        return

    cast_hashes = load_lines(HASHES_FILE)
    if not cast_hashes:
        print("Tidak ada hash. Pastikan hashes.txt berisi cast hash (satu per baris).")
        return

    tokens = [normalize_token(t) for t in raw_tokens]
    sessions = [make_session(t) for t in tokens]

    # Prepare CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["token_index", "token_preview", "cast_hash", "like_status", "recast_status", "note"])

        total_ops = len(sessions) * len(cast_hashes)
        print(f"{len(sessions)} akun × {len(cast_hashes)} hash = {total_ops} operasi (like+recast setiap pasangan).")
        op_count = 0

        # Iterate: untuk setiap token, proses semua hash
        for i, session in enumerate(sessions, start=1):
            token_preview = (tokens[i-1][:12] + "...") if tokens[i-1] else ""
            print(f"\n=== Memakai akun #{i} ({token_preview}) ===")
            for ch in cast_hashes:
                op_count += 1
                print(f"[{op_count}/{total_ops}] token#{i} → hash {ch} ...", end=" ")
                like_resp, recast_resp = like_and_recast(session, ch)

                like_status = like_resp.status_code if like_resp is not None else "no-response"
                recast_status = recast_resp.status_code if recast_resp is not None else "no-response"
                note = ""
                if like_resp is None or recast_resp is None:
                    note = "failed_retries"

                # print short result
                print(f"LIKE {like_status} | RECAST {recast_status}")

                writer.writerow([i, token_preview, ch, like_status, recast_status, note])
                csvfile.flush()

                # Delay between hash operations to avoid rate-limit spikes
                time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    print(f"\nSelesai. Hasil tersimpan di {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
