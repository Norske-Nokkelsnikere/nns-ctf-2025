# Linktea Writeup

The primary issue here is the `Link` header during loading of avatar URL.
Take a look at [CR-bug#415810136](https://issues.chromium.org/issues/415810136)

Set the avatar URL to a server you control, return an image with a `Link` header with `referrerpolicy="unsafe-url"`.
You will then get an OAuth code in the `Referer`.
Exchange this code in `/idp/exchange`, you do not need to supply `client_secret` or some other PKCE.
Make sure to not answer the image request before the you have exchanged - then the client will exchange it before you.

After editing the top variables in the solver (`DOMAIN` and `INSTANCE_DOMAIN`), you can run it like this:

```bash
bun i
bun run index.ts
```
