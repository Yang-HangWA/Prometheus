dockprom
========

一个监控docker主机和docker容器的方案，用到 [Prometheus](https://prometheus.io/), [Grafana](http://grafana.org/), [cAdvisor](https://github.com/google/cadvisor), 
[NodeExporter](https://github.com/prometheus/node_exporter),[Redis_Exporter]https://github.com/oliver006/redis_exporter , [Postgresql_exporter]
and alerting with [AlertManager](https://github.com/prometheus/alertmanager).

***如果你在寻找Docker Swarm的版本，请到 [stefanprodan/swarmprom](https://github.com/stefanprodan/swarmprom)***

## Install

克隆这个知识库到你的docker主机上, cd进dockprom里面，然后运行docker compose的命令，操作如下:



```bash
git clone https://github.com/stefanprodan/dockprom
cd dockprom

ADMIN_USER=admin ADMIN_PASSWORD=admin docker-compose up -d
```

命令中ADMIN_USER=admin ADMIN_PASSWORD=admin是设置里面的用户和账户密码，在caddy中用到了这两个输入，作为一些监控端口认证，防止被恶意访问。
你可以在运行时，设定成你想要的用户名和密码。


预先需要的环境:

* Docker Engine >= 1.13
* Docker Compose >= 1.11


容器介绍:

* Prometheus (指标面板，prometheus检测数据查询) `http://<host-ip>:9090`
* AlertManager (报警管理页面)                  `http://<host-ip>:9093`
* Grafana (指标可视化)                         `http://<host-ip>:3000`
* NodeExporter (主机信息收集器)
* cAdvisor (容器信息收集器)
* Caddy (反向代理和给prometheus和alertmanager提供基本的账户登录，类似于nginx的服务器，可查看维基百科学习相关资料：https://zh.wikipedia.org/wiki/Caddy) 

## 安装Grafana

在浏览器中输入 `http://<host-ip>:3000` 并用你在开始启动设置的账号密码进行登录认证，如果你开始没有设置，则默认   账号：admin  密码：admin  
你可以通过改变配置文件中的认证账户密码，相应的位置为docker-compose.yml文件中关于grafana这个容器的设置，
即参数中的：
* environment:
*      - GF_SECURITY_ADMIN_USER=${ADMIN_USER:-admin}
*      - GF_SECURITY_ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin}

或者开始运行docker-compose up命令时提供ADMIN_USER和ADMIN_PASSWORD的方式重设密码.

Grafana提前设置好了仪表板，并配置好了Prometheus最为默认数据来源:

* Name: Prometheus
* Type: Prometheus
* Url: http://prometheus:9090
* Access: proxy

***Docker Host Dashboard***

![Host](https://raw.githubusercontent.com/stefanprodan/dockprom/master/screens/Grafana_Docker_Host.png)

Docker主机仪表板展示了监控你启动的服务占用的计算机资源相关的并且比较重要的数据，主要并且重要的指标数据：

* Server uptime, CPU idle percent（CPU空闲占比）, number of CPU cores（CPU的核数）, available memory（有效内存）, swap and storage（交换和存储）
* System load average graph（系统平均负载图）, running and blocked by IO processes graph（由IO进程运行和阻塞图）, 
* interrupts graph（中断图）
* CPU usage graph by mode (guest, idle, iowait, irq, nice, softirq, steal, system, user)（CPU的使用率，按照各种模式划分的）
* Memory usage graph by distribution (used, free, buffers, cached)（内存使用情况图分布）
* IO usage graph (read Bps, read Bps and IO time)（IO使用情况图）
* Network usage graph by device (inbound Bps, Outbound Bps) （设备的网络使用情况图）
* Swap usage and activity graphs （交换使用情况和活动​​图）

对于存储，特别是Free Storage graph（空闲存储图），你需要在grafana的fstype(文件类型)进行特别说明，

你可以在文件 `grafana/dashboards/docker_host.json` 480行找到 :

      "expr": "sum(node_filesystem_free{fstype=\"btrfs\"})",
      
我是工作在BTRFS上, 所以我必须把 `aufs` 改为 `btrfs`.

你可以通过Prometheus `http://<host-ip>:9090`找到你系统的fstype值，输入：

      node_filesystem_free

***Docker Containers Dashboard***

![Containers](https://raw.githubusercontent.com/stefanprodan/dockprom/master/screens/Grafana_Docker_Containers.png)

The Docker Containers Dashboard shows key metrics for monitoring running containers:

* Total containers CPU load, memory and storage usage
* Running containers graph, system load graph, IO usage graph
* Container CPU usage graph
* Container memory usage graph
* Container cached memory usage graph
* Container network inbound usage graph
* Container network outbound usage graph

Note that this dashboard doesn't show the containers that are part of the monitoring stack.

***Monitor Services Dashboard***

![Monitor Services](https://raw.githubusercontent.com/stefanprodan/dockprom/master/screens/Grafana_Prometheus.png)

The Monitor Services Dashboard shows key metrics for monitoring the containers that make up the monitoring stack:

* Prometheus container uptime, monitoring stack total memory usage, Prometheus local storage memory chunks and series
* Container CPU usage graph
* Container memory usage graph
* Prometheus chunks to persist and persistence urgency graphs
* Prometheus chunks ops and checkpoint duration graphs
* Prometheus samples ingested rate, target scrapes and scrape duration graphs
* Prometheus HTTP requests graph
* Prometheus alerts graph

I've set the Prometheus retention period to 200h and the heap size to 1GB, you can change these values in the compose file.

```yaml
  prometheus:
    image: prom/prometheus
    command:
      - '-storage.local.target-heap-size=1073741824'
      - '-storage.local.retention=200h'
```

Make sure you set the heap size to a maximum of 50% of the total physical memory. 

## Define alerts

I've setup three alerts configuration files:

* Monitoring services alerts [targets.rules](https://github.com/stefanprodan/dockprom/blob/master/prometheus/targets.rules)
* Docker Host alerts [host.rules](https://github.com/stefanprodan/dockprom/blob/master/prometheus/host.rules)
* Docker Containers alerts [containers.rules](https://github.com/stefanprodan/dockprom/blob/master/prometheus/containers.rules)

You can modify the alert rules and reload them by making a HTTP POST call to Prometheus:

```
curl -X POST http://admin:admin@<host-ip>:9090/-/reload
```

***Monitoring services alerts***

Trigger an alert if any of the monitoring targets (node-exporter and cAdvisor) are down for more than 30 seconds:

```yaml
ALERT monitor_service_down
  IF up == 0
  FOR 30s
  LABELS { severity = "critical" }
  ANNOTATIONS {
      summary = "Monitor service non-operational",
      description = "{{ $labels.instance }} service is down.",
  }
```

***Docker Host alerts***

Trigger an alert if the Docker host CPU is under hight load for more than 30 seconds:

```yaml
ALERT high_cpu_load
  IF node_load1 > 1.5
  FOR 30s
  LABELS { severity = "warning" }
  ANNOTATIONS {
      summary = "Server under high load",
      description = "Docker host is under high load, the avg load 1m is at {{ $value}}. Reported by instance {{ $labels.instance }} of job {{ $labels.job }}.",
  }
```

Modify the load threshold based on your CPU cores.

Trigger an alert if the Docker host memory is almost full:

```yaml
ALERT high_memory_load
  IF (sum(node_memory_MemTotal) - sum(node_memory_MemFree + node_memory_Buffers + node_memory_Cached) ) / sum(node_memory_MemTotal) * 100 > 85
  FOR 30s
  LABELS { severity = "warning" }
  ANNOTATIONS {
      summary = "Server memory is almost full",
      description = "Docker host memory usage is {{ humanize $value}}%. Reported by instance {{ $labels.instance }} of job {{ $labels.job }}.",
  }
```

Trigger an alert if the Docker host storage is almost full:

```yaml
ALERT hight_storage_load
  IF (node_filesystem_size{fstype="aufs"} - node_filesystem_free{fstype="aufs"}) / node_filesystem_size{fstype="aufs"}  * 100 > 85
  FOR 30s
  LABELS { severity = "warning" }
  ANNOTATIONS {
      summary = "Server storage is almost full",
      description = "Docker host storage usage is {{ humanize $value}}%. Reported by instance {{ $labels.instance }} of job {{ $labels.job }}.",
  }
```

***Docker Containers alerts***

Trigger an alert if a container is down for more than 30 seconds:

```yaml
ALERT jenkins_down
  IF absent(container_memory_usage_bytes{name="jenkins"})
  FOR 30s
  LABELS { severity = "critical" }
  ANNOTATIONS {
    summary= "Jenkins down",
    description= "Jenkins container is down for more than 30 seconds."
  }
```

Trigger an alert if a container is using more than 10% of total CPU cores for more than 30 seconds:

```yaml
 ALERT jenkins_high_cpu
  IF sum(rate(container_cpu_usage_seconds_total{name="jenkins"}[1m])) / count(node_cpu{mode="system"}) * 100 > 10
  FOR 30s
  LABELS { severity = "warning" }
  ANNOTATIONS {
    summary= "Jenkins high CPU usage",
    description= "Jenkins CPU usage is {{ humanize $value}}%."
  }
```

Trigger an alert if a container is using more than 1,2GB of RAM for more than 30 seconds:

```yaml
ALERT jenkins_high_memory
  IF sum(container_memory_usage_bytes{name="jenkins"}) > 1200000000
  FOR 30s
  LABELS { severity = "warning" }
  ANNOTATIONS {
      summary = "Jenkins high memory usage",
      description = "Jenkins memory consumption is at {{ humanize $value}}.",
  }
```

## Setup alerting

The AlertManager service is responsible for handling alerts sent by Prometheus server. 
AlertManager can send notifications via email, Pushover, Slack, HipChat or any other system that exposes a webhook interface. 
A complete list of integrations can be found [here](https://prometheus.io/docs/alerting/configuration).

You can view and silence notifications by accessing `http://<host-ip>:9093`.

The notification receivers can be configured in [alertmanager/config.yml](https://github.com/stefanprodan/dockprom/blob/master/alertmanager/config.yml) file.

To receive alerts via Slack you need to make a custom integration by choose ***incoming web hooks*** in your Slack team app page. 
You can find more details on setting up Slack integration [here](http://www.robustperception.io/using-slack-with-the-alertmanager/).

Copy the Slack Webhook URL into the ***api_url*** field and specify a Slack ***channel***.

```yaml
route:
    receiver: 'slack'

receivers:
    - name: 'slack'
      slack_configs:
          - send_resolved: true
            text: "{{ .CommonAnnotations.description }}"
            username: 'Prometheus'
            channel: '#<channel>'
            api_url: 'https://hooks.slack.com/services/<webhook-id>'
```

![Slack Notifications](https://raw.githubusercontent.com/stefanprodan/dockprom/master/screens/Slack_Notifications.png)
