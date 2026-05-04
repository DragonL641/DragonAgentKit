# 常见 K8s 故障排查流程

## 目录

1. [Pod CrashLoopBackOff](#1-pod-crashloopbackoff)
2. [Pod Pending](#2-pod-pending)
3. [Pod ImagePullBackOff](#3-pod-imagepullbackoff)
4. [Pod OOMKilled](#4-pod-oomkilled)
5. [Node NotReady](#5-node-notready)
6. [Service 无法访问](#6-service-无法访问)
7. [磁盘压力](#7-磁盘压力)
8. [内存压力](#8-内存压力)
9. [DNS 解析异常](#9-dns-解析异常)
10. [证书过期](#10-证书过期)

---

## 1. Pod CrashLoopBackOff

**症状**：Pod 反复重启，状态为 CrashLoopBackOff

**排查步骤**：
```
1. kubectl describe pod <pod> -n <ns>      # 查看 Last State/Reason
2. kubectl logs <pod> -n <ns> --previous    # 查看上一次崩溃的日志
3. kubectl logs <pod> -n <ns> --tail=200    # 当前日志
4. kubectl get events -n <ns> --sort-by='.lastTimestamp' | grep <pod>
```

**常见原因**：
- 应用启动配置错误（环境变量、配置文件缺失）
- 健康检查失败（liveness probe 配置不合理）
- 依赖服务未就绪（数据库、Redis 等连不上）
- 权限问题（文件/目录权限不足）

---

## 2. Pod Pending

**症状**：Pod 一直处于 Pending 状态，无法调度

**排查步骤**：
```
1. kubectl describe pod <pod> -n <ns>       # 查看 Events 中的调度失败原因
2. kubectl get nodes -o wide                 # 检查节点资源
3. kubectl describe nodes | grep -A5 "Allocated resources"  # 资源分配情况
4. kubectl top nodes                         # 实际资源使用
```

**常见原因**：
- 资源不足（CPU/内存/GPU）
- 节点选择器/亲和性不匹配
- PV 不可用（PVC Pending）
- Taint/Toleration 不匹配
- PodDisruptionBudget 限制

---

## 3. Pod ImagePullBackOff

**症状**：镜像拉取失败

**排查步骤**：
```
1. kubectl describe pod <pod> -n <ns>       # 查看 Events 中的拉取错误
2. 检查镜像名称和 tag 是否正确
3. 检查 imagePullSecrets 是否配置（私有仓库）
4. SSH 到节点检查网络连通性：curl -I <registry-url>
```

---

## 4. Pod OOMKilled

**症状**：Pod 因内存溢出被杀，Last State Reason = OOMKilled

**排查步骤**：
```
1. kubectl describe pod <pod> -n <ns>       # 确认 OOM 和 limits
2. kubectl top pods -n <ns>                 # 查看当前内存使用
3. kubectl logs <pod> -n <ns> --previous    # 查看崩溃前日志
4. 如有 Prometheus：查 container_memory_working_set_bytes 趋势
```

**建议**：
- 调整 resources.limits.memory
- 检查应用是否存在内存泄漏
- 分析 JVM/运行时堆内存配置

---

## 5. Node NotReady

**症状**：节点状态 NotReady

**排查步骤**：
```
1. kubectl describe node <node>              # 查看 Conditions
2. SSH 到节点：
   - uptime                                   # 是否重启过
   - free -h                                  # 内存
   - df -h                                    # 磁盘
   - dmesg -T | tail -50                      # 内核日志（OOM killer 等）
   - journalctl -u kubelet --no-pager -n 100  # kubelet 日志
   - systemctl status kubelet                 # kubelet 状态
```

**常见原因**：
- kubelet 服务异常/挂掉
- 节点磁盘满（DiskPressure）
- 节点内存不足（MemoryPressure）
- 网络分区（节点与 API Server 失联）
- 内核 panic/OOM killer

---

## 6. Service 无法访问

**症状**：Service ClusterIP/NodePort/LB 无法访问

**排查步骤**：
```
1. kubectl get svc <name> -n <ns> -o wide   # 确认类型和端口
2. kubectl get endpoints <name> -n <ns>      # 是否有后端 Pod
3. kubectl get pods -n <ns> -l <selector>    # Pod 是否 Running/Ready
4. kubectl describe svc <name> -n <ns>       # 确认 selector 匹配
5. 从集群内测试：
   kubectl run tmp --image=busybox --rm -it -- wget -qO- <svc>.<ns>.svc.cluster.local:<port>
```

---

## 7. 磁盘压力

**症状**：DiskPressure / Pod Evicted / 磁盘告警

**排查步骤**：
```
1. kubectl describe node <node> | grep -A5 DiskPressure
2. SSH 到节点：
   - df -h
   - du -sh /var/lib/docker/* 2>/dev/null | sort -rh | head -10
   - du -sh /var/lib/containerd/* 2>/dev/null | sort -rh | head -10
   - du -sh /var/log/* | sort -rh | head -10
   - crictl images                                # 检查镜像占用
3. 如有 Prometheus：查 node_filesystem_avail_bytes 趋势
```

---

## 8. 内存压力

**症状**：MemoryPressure / Pod Evicted / OOM 频繁

**排查步骤**：
```
1. kubectl describe node <node> | grep -A5 MemoryPressure
2. kubectl top pods -n <ns> --sort-by=memory
3. SSH 到节点：
   - free -h
   - ps aux --sort=-%mem | head -20
   - dmesg -T | grep -i "oom\|killed"
4. 如有 Prometheus：查 node_memory_MemAvailable_bytes 趋势
```

---

## 9. DNS 解析异常

**症状**：Pod 内无法解析 Service 名称或外部域名

**排查步骤**：
```
1. kubectl get pods -n kube-system -l k8s-app=kube-dns    # CoreDNS 状态
2. kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50
3. 从 Pod 内测试：
   kubectl run tmp --image=busybox --rm -it -- nslookup <svc>.<ns>.svc.cluster.local
   kubectl run tmp --image=busybox --rm -it -- nslookup kubernetes.default
4. 检查 CoreDNS 配置：
   kubectl get cm coredns -n kube-system -o yaml
```

---

## 10. 证书过期

**症状**：TLS handshake error / x509 certificate has expired

**排查步骤**：
```
1. 检查 API Server 证书：
   openssl s_client -connect <api-server>:6443 </dev/null 2>/dev/null | openssl x509 -noout -dates
2. 检查 kubelet 证书（SSH 到节点）：
   openssl x509 -in /var/lib/kubelet/pki/kubelet-client-current.pem -noout -dates
3. 检查 etcd 证书（如可访问）：
   openssl x509 -in /etc/kubernetes/pki/etcd/server.crt -noout -dates
```
