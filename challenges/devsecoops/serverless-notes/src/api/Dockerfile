FROM rancher/k3s:v1.31.12-k3s1

RUN mkdir -p /var/lib/rancher/k3s/server/manifests
COPY entrypoint.sh /
COPY provision.sh /
COPY resources /var/lib/rancher/k3s/server/manifests/

ENTRYPOINT ["ash", "/entrypoint.sh"]
