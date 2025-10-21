/provision.sh &

exec k3s server \
    --disable-cloud-controller --disable-scheduler --disable-agent --disable-network-policy --disable-kube-proxy --disable-helm-controller --flannel-backend=none \
    --disable=traefik --disable=local-storage --disable=metrics-server --disable=servicelb --disable=runtimes \
    --kube-apiserver-arg=anonymous-auth=true \
    --kube-controller-manager-arg=controllers=deployment-controller,serviceaccount-token-controller,replicaset-controller
