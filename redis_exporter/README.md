#这是一个关于redis_exporter的说明文档

#redis_exporter的原理是和你要监控的redis服务器进行交互，
#通过交互查询到相关的redis信息，然后一般会在机器的9121端口
#将这些信息暴露给prometheus
#相关的项目地址在 https://github.com/oliver006/redis_exporter
#其中有更详细的说明

#这里用到的版本为redis_exporter-v0.17.1.linux-amd64.tar.gz，更新时
#可以下载你想要的redis_exporter版本来替换本文件夹中redis_exporter文件


