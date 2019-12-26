#coding=utf-8
import time
from disque_client import Client
from influxdb import InfluxDBClient


def showDBNames(client):    
        result = client.query('show measurements;') # 显示数据库中的表
        print("Result: {0}".format(result)) 

def  collect_disque_info(passwd):  
    disque_client = Client(["127.0.0.1:7711"])
    disque_client.connect(passwd)
    #info
    info = disque_client.info()
    #queue length
    ngx2php = disque_client.qlen("work_queue_ngx2php")
    eventhandle = disque_client.qlen("work_queue_eventhandle")
    heartbeats = disque_client.qlen("work_queue_heartbeats")
    soft_violations_audit_distr_list = disque_client.qlen("soft_violations_audit_distr_list")
    return info,ngx2php,eventhandle,heartbeats,soft_violations_audit_distr_list
 
if __name__=='__main__':
   #connect
   passwd = "penetration"
   db_client = InfluxDBClient('localhost',8086,'root','root','') 
   data_list = db_client.get_list_database()
   #若果没有disque_db,则创建disque_db
   database_list = []
   for name_dict in data_list:
      for key,value in name_dict.items():
          database_list.append(value)
   
   if 'metric_db' not in database_list:
       db_client.create_database('metric_db') #创建disque存放数据的db
   db_client.close()
   #循环获取并写入数据到Influxdb，间隔时间为1秒
   while True:
       time.sleep(1)
       try:
         db_client = InfluxDBClient('localhost',8086,'root','root','metric_db')
         info,ngx2php,eventhandle,heartbeats,soft_violations_audit_distr_list = collect_disque_info(passwd)
         json_body = [
         {   
         "measurement" : "disque_used_memory",
         "fields" :{
            "value": info['used_memory']
         }
         },
         {
         "measurement" : "disque_uptime_in_days",
         "fields" :{
         "value": info['uptime_in_days']
         }
         },
         {           
         "measurement" : "disque_connected_clients",
         "fields" :{
         "value": info['connected_clients']
         }
         },
         {           
         "measurement" : "disque_blocked_clients",
         "fields" :{
         "value": info['blocked_clients']
         }
         },
         {           
         "measurement" : "disque_total_net_output_bytes",
         "fields" :{
         "value": info['total_net_output_bytes']
         }
         },
         {           
         "measurement" : "disque_total_net_input_bytes",
         "fields" :{
         "value": info['total_net_input_bytes']
         }
         },
         {           
         "measurement" : "disque_instantaneous_ops_per_sec",
         "fields" :{
         "value": info['instantaneous_ops_per_sec']
         }
         },
         {           
         "measurement" : "disque_registered_queues",
         "fields" :{
         "value": info['registered_queues']
         } 
         },
         {           
         "measurement" : "disque_registered_jobs",
         "fields" :{
         "value": info['registered_jobs']
         }
         },
         {           
         "measurement" : "disque_ngx2php_queue",
         "fields" :{
         "value": ngx2php
         }
         },
          {
         "measurement" : "disque_eventhandle_queue",
         "fields" :{
         "value": eventhandle
         }
         },
         {
         "measurement" : "disque_heartbeats_queue",
         "fields" :{
         "value": heartbeats
         }
         },
          {
         "measurement" : "disque_soft_violations_audit_distr_list_queue",
         "fields" :{
         "value": soft_violations_audit_distr_list
         }
         }
         ]
         db_client.write_points(json_body)
       except Exception,e:
         print str(e)
     
