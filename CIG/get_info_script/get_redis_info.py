#encoding=utf-8
import redis
import time
from influxdb import InfluxDBClient

def collect_redis_info(passwd,port,host, db):
    con = redis.Redis(host=host,port=port,db=db,password=passwd)
    return con.info()

if __name__=='__main__':
   passwd = 'penetration'
   port = 6379
   host = 'localhost'
   db = 0
   db_client = InfluxDBClient('localhost',8086,'root','root','')
   data_list = db_client.get_list_database()
   #若果没有redis_db,则创建redis_db
   database_list = []
   for name_dict in data_list:
      for key,value in name_dict.items():
          database_list.append(value)
       
   if 'metric_db' not in database_list:
       db_client.create_database('metric_db') #创建redis存放数据的db
   db_client.close()
   while True:
      time.sleep(1)
      try:
        info = collect_redis_info(passwd,port,host,db)
        db_client = InfluxDBClient('localhost',8086,'root','root','metric_db')
        json_body = [
        {
        "measurement" : "redis_maxmemory",
        "fields" :{
          "value" : info['maxmemory']
        }
        },
        {
        "measurement" : "redis_used_memory",
        "fields" :{
          "value" : info['used_memory']
        }
        },
        {
        "measurement" : "redis_uptime_in_days",
        "fields" :{
          "value" : info['uptime_in_days']
        }
        },
        {
        "measurement" : "redis_connected_clients",
        "fields" :{
          "value" : info['connected_clients']
        }
        },
        {
        "measurement" : "redis_blocked_clients",
        "fields" :{
          "value" : info['blocked_clients']
        }
        },
        {
        "measurement" : "redis_total_net_output_bytes",
        "fields" :{
          "value" : info['total_net_output_bytes']
        }
        },
        {
        "measurement" : "redis_total_net_input_bytes",
        "fields" :{
          "value" : info['total_net_input_bytes']
        }
        },
        {
        "measurement" : "redis_instantaneous_ops_per_sec",
        "fields" :{
          "value" : info['instantaneous_ops_per_sec']
        }
        },
        {
        "measurement" : "redis_db0_keys",
        "fields" :{
          "value" : info['db0']["keys"]
        }
        },
        {
        "measurement" : "redis_db0_expires",
        "fields" :{
          "value" : info['db0']["expires"]
        }
        }
        ]
        db_client.write_points(json_body)
      except Exception,e:
        print str(e)

