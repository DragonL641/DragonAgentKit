# 常用 PromQL 查询模板

使用前先确认 Prometheus 可用性：

```bash
curl -s "<prometheus_url>/api/v1/query?query=up" | head -100
```

## 查询方式

```bash
# 即时查询
curl -s "<prometheus_url>/api/v1/query?query=<encoded_promql>"

# 范围查询（最近 1 小时，步长 60s）
curl -s "<prometheus_url>/api/v1/query_range?query=<encoded_promql>&start=$(date -d '1 hour ago' +%s)&end=$(date +%s)&step=60"
```

## Node 指标

```promql
# 节点 CPU 使用率
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 节点内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 节点磁盘使用率
(1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes{fstype!~"tmpfs|overlay"})) * 100

# 节点磁盘 IO 等待
rate(node_disk_io_time_seconds_total[5m])

# 节点网络流量
rate(node_network_receive_bytes_total{device!~"lo|cali.*|veth.*|docker.*"}[5m])
rate(node_network_transmit_bytes_total{device!~"lo|cali.*|veth.*|docker.*"}[5m])

# 节点 load
node_load1
node_load5
node_load15
```

## Pod/Container 指标

```promql
# Pod CPU 使用
sum by(pod, namespace) (rate(container_cpu_usage_seconds_total{container!=""}[5m]))

# Pod 内存使用
sum by(pod, namespace) (container_memory_working_set_bytes{container!=""})

# Pod 内存限制使用率
sum by(pod, namespace) (container_memory_working_set_bytes{container!=""})
  / sum by(pod, namespace) (kube_pod_container_resource_limits{resource="memory"})

# Pod CPU 限制使用率
sum by(pod, namespace) (rate(container_cpu_usage_seconds_total{container!=""}[5m]))
  / sum by(pod, namespace) (kube_pod_container_resource_limits{resource="cpu"})

# Pod 重启次数
sum by(pod, namespace) (increase(kube_pod_container_status_restarts_total[1h]))

# Pod 非 Running 状态
kube_pod_status_phase{phase!="Running"}
```

## K8s 资源指标

```promql
# Deployment 副本数
kube_deployment_status_replicas_available / kube_deployment_spec_replicas

# 挂起的 Persistent Volume Claims
kube_persistentvolumeclaim_status_phase{phase="Pending"}

# PVC 磁盘使用率
kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes * 100
```

## 告警查询

```promql
# 当前 firing 的告警
ALERTS{alertstate="firing"}

# 按严重程度分组
count by(alertname, severity) (ALERTS{alertstate="firing"})
```
