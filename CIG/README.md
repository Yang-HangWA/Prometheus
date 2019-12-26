#   CIG监控系统介绍文档
####                             -By yanghang

概述：CIG监控系统主要有cAdvisor、InfluxDB、Grafana三个组件以及python脚本组成。主要目的是监控公司业务项目，监控其中的docker主机、disque、redis、postgres、openresty等组件。

## 还需要完善的地方
    1.openresty监控内容：目前分析日志能获取api的调用次数，以及200,400之类的数据。需要修改access.log的格式，把需要监控的信息输出出来，才可以用脚本获取相关信息。
    2.报警条件的设置。
    
## 项目地址：
   `https://github.com/Yang-HangWA/CIG`
## Storage7上存放路径为： 
   `/home/yanghang/cAdvisor_InfluxDB_Grafana`

## 用到的镜像为：
        tutum/influxdb:0.9
        google/cadvisor:latest
        grafana/grafana:latest

容器启动的相关端口映射，文件映射，以及环境变量设置情况可以查看docker-compose.yml文件。


## 启动：
```bash
$ bash quick_start.sh
```
启动主要分为两个阶段，第一个阶段是启动文件中docker-compose项目，第二阶段是启动get_info_script中用于获取各个组件数据的python脚本。启动方式用的是nohup ….&方式，所以最后加了个clear。首次启动需要设置数据库，然后才能让导入的监控面板有数据输入。
Storage7上的配置设置都已完成。

### 查看数据（需要查看influxdb时用）：

可以通过8083端口对influxdb进行操作，如下图所示：

![Show_measurements](https://github.com/Yang-HangWA/CIG/blob/master/pic/show_measurements.png) 
    
 Influxdb中的measurements类似于表的概念，通过show measurements命令能看到数据库metric_db中存放的数据项表，这个数据库中的数据都是通过python脚本插入的，是自己定义的，即我们获取的数据项。
如下文所接图示意：

![查询结果](https://github.com/Yang-HangWA/CIG/blob/master/pic/show_measurments_result.png)

除了数据库metric_db之外，还有一个cadvisor数据库用来存放cadvisor获取的docker容器数据，这个是在docker-compose启动时直接设置的，通过command：-storage_driver=influxdb -storage_driver_db=cadvisor -storage_driver_host=influxsrv:8086 将数据存放到influxdb，并设置了主机地址。


##### 设置数据库（首次启动需要）
设置数据库，点击设置按钮，点击Data Sources进行数据库设置：

![add data sorce](https://github.com/Yang-HangWA/CIG/blob/master/pic/add_data_source.png)

点击add data source添加数据库，以添加metric_db为例，第一个Name可以自己定义，一般会与influxdb数据库名保持一致，Type选择influxDB，URL因为在docker-compose设置过，所以URL要写成http://influxsrv:8086 , 
 
![add metric db](https://github.com/Yang-HangWA/CIG/blob/master/pic/add_metric_db.png)

* 勾选Basic Auth,在Basic Auth Details中填写user和Password，这个是在8083端口查看自己的设置，点击设置的小齿轮可以查看和重新设置。

![basic_auth](https://github.com/Yang-HangWA/CIG/blob/master/pic/basic_auth.png)

* 最后在InfluxDB Details的Database添加数据库名metric_db。

## 关闭：
```bash
$ bash quick_stop.sh
```
获取用于获取信息的进程的进程id，然后用sudo kill -9 id将这些获取信息的脚本杀掉，然后用docker-compose down停掉相关容器。Grafana数据存放在了本地新建的卷，influxdb也映射出去了，所以再次运行时数据并不会丢失。

## Python脚本文件介绍：
* get_info_script文件夹下为获取各个组件的脚本，
* get_openresty_info.py 用于获取openresty信息
* get_host_info.py  用于获取主机信息的
* get_pg_info.py    用于获取pg信息的
* get_redis_info.py   用于获取redis信息的
* get_disque_info.py  用于获取disque信息的
* start_get_info.py  用于启动所有的get_info脚本
* stop_get_info.py  用于停止所有的get_info脚本
* disque_client.py  用于连接disque的客户端，该客户端的原项目地址为：
* `https://github.com/ybrs/pydisque` 因为原客户端不支持密码认证，所以手动添加了密码认证，然后将该客户端放在了本地。

#### 脚本简单介绍
* get_openresty_info.py用docker logs获取openresty的日志，然后分析最近一秒产生的日志，然后将日志进行解析，将解析的数据插入到influxdb中。
* get_host_info.py引用了psutil,influxdb包，psutil是python用来获取主机信息的，influxdb包是用来连接influxdb数据库，将获取的数据插进去的。
* get_pg_info.py引用了psycopg2,influxdb包，psycopg2为pg客户端的包，用于连接pg。influxdb的作用与上面相同。
* get_redis_info.py引用了redis，influxdb包，redis包为redis客户端包，influxdb作用相同
* get_disque_info.py引用了改写在本地的disque_client，外加influxdb包。

* 注：引用的包一般可以通过`pip install`进行安装，每个获取信息中基本思想基本一致，导入一个能接入的客户端，然后进行信息获取，然后将信息写入influxdb。需要密码认证的部分还未写入配置文件，直接在各个脚本中进行的赋值。


#### 邮件提醒功能：邮箱已设置，报警条件还未设置
   `grafana.ini`已经配置好了一个申请的搜狐邮箱，可以在3000端口的`grafana主页`的（小铃铛图标）`Alerting`选项中进行通知对象的添加。名字可以自己定义，`type`选择email，然后email address添加自己想接收报警邮件的地址。
 
![add email test](https://github.com/Yang-HangWA/CIG/blob/master/pic/alert_email_test.png)

##### 报警设置
目前grafana只支持`graph`报警设置，所以需要添加的报警内容都需要转化成graph形式进行设置。打开一个监控面板，选择你需要设置报警的graph进行报警编辑，一般是以设置阈值的形式。
 
 ![set alert](https://github.com/Yang-HangWA/CIG/blob/master/pic/alert_set.png)




#### 面板首次启动时自动加载（完成，有难度,5.11号学习https://ops.tips/blog/initialize-grafana-with-preconfigured-dashboards/ 这篇帖子之后完成）  
完成方法：
###### 步骤1
* 修改grafana.ini配置文件
* ########## Paths ###########
* [paths]
* provisioning = conf/provisioning
###### 步骤2
* provision文件设置，分为datasources和dashborads文件夹中进行设置，需要注意的是datasources只能添加一个默认数据库，所以后面需要将获取的数据放入同一个数据库，将外层存放面板json文件的dashboards映射到容器中的/var/lib/grafana/dashboards下

* 目前由于使用两个数据库，所以需要手动添加一个cadvisor数据库，才能让docker监控面板正确显示。

* 之前情况：
*   可参考 http://docs.grafana.org/http_api/dashboard/
* Grafana文件夹下的setup.up脚本文件来源于[dockprom](https://github.com/stefanprodan/dockprom/blob/master/grafana/setup.sh)， 但是通过改动这个脚本还没有成功grafana的dashboards，目前dashboards还无法动态加载，网上资料说是可以通过http api加载的，也就是脚本中的方式，这个还可能和grafana的版本有关，因为如果使用grafana:4.6.3时可以部分加载，但是用grafana:latest是完全无法加载，直接导出的面板的json文件无法直接通过setup.sh直接导入。

##### 手动导入监控面板json文件
目前需要手动将编辑好的dashboards的json文件导入进去，点击“+”号，点击import，将你自己预先编辑好的面板（编辑的面板json文件我一般放在grafana文件夹下的dashboards下）的json贴到图2的1处，或者到grafana dashboard官网https://grafana.com/dashboards 找你需要的面板，然后将dashboard的编号填入图2的2处。
 ![import dashboard](https://github.com/Yang-HangWA/CIG/blob/master/pic/import_dashboards.png)
         
                                    图1
 
 ![import dashboard way](https://github.com/Yang-HangWA/CIG/blob/master/pic/dashboards_import_1_2.png)

                                    图2





#### 3000端口grafana登录
用户密码设置（通过左边的小齿轮进入Server admin）：
注意：一定要设置邮箱，不然密码忘记了之后就再也无法以管理员身份进入grafana，意味着数据就无法修改，之前的数据也无法查看，我之前有过几次这种情况，感觉并不是密码忘记了，也会出现这种问题，所以保险起见，设置email，用于登录不进去时进行密码重置。

#### Storage上设置了两个账号：
    Admin  管理员            `usr : admin       password:admin`
    Watcher 普通查看权限     `usr:watcher       password:watcher`
 
![usr set](https://github.com/Yang-HangWA/CIG/blob/master/pic/set_usr_pass.png)

### Influxdb数据设置自动清除
目前influxdb数据映射在/data/influxdb下：
8083 端口操作influxdb：
命令：`CREATE RETENTION POLICY "clear_data_3d" ON "metric_db" DURATION 3d REPLICATION 1 DEFAULT`
![create retention](https://github.com/Yang-HangWA/CIG/blob/master/pic/creat_petention.png)

### 查看设置：
命令：`SHOW RETENTION POLICIES ON "metric_db"`
 ![show retention](https://github.com/Yang-HangWA/CIG/blob/master/pic/show_retention.png)


### 监控效果展示 3000端口 grafana主页登录可见
* 主机监控
![host monitor](https://github.com/Yang-HangWA/CIG/blob/master/pic/host_monitor.png)

* docker监控
![docker monitor](https://github.com/Yang-HangWA/CIG/blob/master/pic/docker_monitor.png)

* disque监控
![disque monitor](https://github.com/Yang-HangWA/CIG/blob/master/pic/disque_monitor.png)

* postgres监控
![postgres monitor](https://github.com/Yang-HangWA/CIG/blob/master/pic/postgre_monitor.png)

* redis监控
![redis monitor](https://github.com/Yang-HangWA/CIG/blob/master/pic/redis_monitor.png)

* openrestyJ监控
![openresty monitor](https://github.com/Yang-HangWA/CIG/blob/master/pic/openresty_monitor.png)

##InfluxDB_Grafana
python script with influxdb and grafana to monitor the docker server
## start
    You can start the project by `docker-compose up` 
    
## script to catch information of your server
    More work should be done when you want to get infomation of your server or server of docker.
## email 
    If you want to set a alert with email notification,you can change the grafana.ini file. This file is to set a email address to send email.First,this email must have smtp server.
### email conf example
        For example:
        [smtp]
        enabled=true
        host=smtp_host
        user = yourmail_address
        password = yourmail_passwd
        skip_verify=true
        from_address=yourmail_address
        from_name=Grafana 
        [alerting]
        enabled = true
        execute_alerts = true

