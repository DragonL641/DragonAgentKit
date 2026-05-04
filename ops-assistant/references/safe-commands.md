# 只读命令速查

## kubectl 诊断命令

### Pod 诊断

```bash
# Pod 状态
kubectl get pods -n <ns> [-o wide]
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> [-c <container>] [--tail=100] [--previous]
kubectl top pods -n <ns>

# Events
kubectl get events -n <ns> --sort-by='.lastTimestamp'
kubectl get events --field-selector involvedObject.name=<pod> -n <ns>
```

### Deployment/StatefulSet/DaemonSet 诊断

```bash
kubectl get deploy/sts/ds -n <ns>
kubectl describe deploy/sts/ds <name> -n <ns>
kubectl rollout status deploy/<name> -n <ns>
kubectl rollout history deploy/<name> -n <ns>
```

### Service/Ingress 诊断

```bash
kubectl get svc/ing -n <ns>
kubectl describe svc <name> -n <ns>
kubectl get endpoints <name> -n <ns>
kubectl get ep <name> -n <ns>
```

### Node 诊断

```bash
kubectl get nodes [-o wide]
kubectl describe node <node>
kubectl top nodes
kubectl get nodes -o jsonpath='{.items[*].status.conditions[?(@.type!="Ready")].message}'
```

### 资源/配额

```bash
kubectl top pods/nodes
kubectl get resourcequota -n <ns>
kubectl describe resourcequota -n <ns>
kubectl get limitrange -n <ns>
kubectl describe limitrange -n <ns>
```

### ConfigMap/Secret 查看

```bash
kubectl get cm/secret -n <ns>
kubectl describe cm <name> -n <ns>
# Secret 只看 metadata，不输出 data 内容（安全考虑）
kubectl get secret <name> -n <ns> -o jsonpath='{.data}' | jq 'keys'
```

### NetworkPolicy/PDB

```bash
kubectl get networkpolicy -n <ns>
kubectl describe networkpolicy <name> -n <ns>
kubectl get pdb -n <ns>
kubectl describe pdb <name> -n <ns>
```

## SSH 只读命令（Node 级诊断）

### 系统资源

```bash
uptime
free -h
df -h
du -sh /var/log/* /tmp/* 2>/dev/null | sort -rh | head -20
lscpu
cat /proc/meminfo | head -10
cat /proc/loadavg
```

### 进程

```bash
ps aux --sort=-%mem | head -20
ps aux --sort=-%cpu | head -20
top -bn1 | head -20
```

### 网络

```bash
ss -tlnp
ss -s
ip addr show
ip route show
cat /etc/resolv.conf
```

### 磁盘/IO

```bash
lsblk
iostat -xz 1 3   # 需要 sysstat
cat /proc/diskstats
```

### 内核/系统日志

```bash
dmesg -T | tail -50
journalctl -u kubelet --no-pager -n 50
journalctl -u docker/containerd --no-pager -n 50
tail -100 /var/log/messages 2>/dev/null || tail -100 /var/log/syslog 2>/dev/null
```

### 容器运行时

```bash
crictl ps -a
crictl logs <container-id> --tail=100
# 或
nerdctl ps -a
docker ps -a  # 如果用 docker
```
