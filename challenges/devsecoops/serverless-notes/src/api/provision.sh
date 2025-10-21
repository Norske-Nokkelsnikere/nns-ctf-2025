echo "[provision.sh] waiting for resources"
until kubectl get serviceaccount devsecoops-intern -n devsecoops >/dev/null 2>&1; do
  sleep 0.5
done
until kubectl wait --for=condition=Established crds/notes.nnsctf.no >/dev/null 2>&1; do
  sleep 0.5
done
until kubectl get namespace daddy-only -n devsecoops >/dev/null 2>&1; do
  sleep 0.5
done

echo "[provision.sh] provisioning resources"
token=$(kubectl create token -n devsecoops devsecoops-intern --duration=24h)
kubectl apply -f - <<EOF
apiVersion: nnsctf.no/v1
kind: Note
metadata:
  name: 1cf56255-ce46-4b8a-9555-b6c71c202db5
  namespace: private-notes
spec:
  title: Infrastructure TODO
  content: $token
EOF
kubectl create secret generic -n daddy-only daddys-secret-flag --from-literal=flag="${FLAG:-'NNS{fake_flag}'}"

echo "[provision.sh] resources provisioned"
