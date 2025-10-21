from os import environ
import requests
from playwright.sync_api import sync_playwright
import time

UI_URL = environ["UI_URL"]
API_URL = environ["API_URL"]
FLAG = environ.get("FLAG", "NNS{demo-flag}")

# Wait for API to come online
while True:
    try:
        response = requests.get(f"{API_URL}/openapi.json")
        response.raise_for_status()
    except:
        time.sleep(1)
        continue
    break

print("API online")

# Create user
response = requests.post(f"{API_URL}/users/@me", json={
    "username": "admin",
    "flag": FLAG
})
data = response.json()
access_token = data["token"]


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(UI_URL)
    page.evaluate(f"localStorage.setItem(\"flag\", {repr(FLAG)})")


    username_field = page.locator("#authtoken-input")
    username_field.evaluate(f"el => el.value = {repr(access_token)}") 
    page.wait_for_timeout(1000)

    login_button = page.locator("#auth-submit")
    login_button.click()
    
    print("auth")
    page.wait_for_timeout(1000)

    while True:
        profile_elements = page.locator("enmy-user-profile").all()
        for profile_element in profile_elements:
            profile_element.click()
            print("chose profile")
            page.wait_for_timeout(1000)


            editor_element = page.locator(".ql-editor")
            message = "🔫 Hand over the memes"
            editor_element.evaluate(f"el => el.innerHTML = {repr(message)}")
            print("set content")
            send_element = page.locator("button.send")
            send_element.click()
            print("sent")
            page.wait_for_timeout(1000)
        page.wait_for_timeout(10_000)
