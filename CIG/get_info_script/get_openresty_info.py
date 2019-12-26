#encoding=utf-8
import subprocess
import os 
import re
import time
from influxdb import InfluxDBClient
#import datetime 
def get_logs():
    command="sudo docker logs --since 1s --tail 1000  openresty"
    output = os.popen(command, 'r')
    res_str = output.readlines()
    access_log_list = []
    for item in res_str:
        match_ =  re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",item.split(' ')[0])
        if match_:
            access_log_list.append(item)
    logs = access_log_list
    #print len(res_str),len(access_log_list)
    return  logs

def parse_logs(logs): 
    correct_dict = {}
    error_dict = {}
    #count用于统计总的api请求数，cor_count用于统计200的，err_count用于统计大于400的
    count = 0
    cor_count = 0
    err_count = 0
    for item in logs:
       count += 1
       name_str = item.split('HTTP/1.1"')[0].split('.json?')[0].split('api/')[1]
       log_type = item.split('HTTP/1.1"')[1].split(' ')[1]
       if str(log_type) == "200":
          cor_count  += 1
          if name_str in correct_dict.keys():
             correct_dict[name_str] += 1
          else:
             correct_dict[name_str] = 1
       elif log_type >= "400":
          err_count += 1
          if name_str in error_dict.keys():
             error_dict[name_str] += 1
          else:
             error_dict[name_str] = 1
    return correct_dict,error_dict,count,cor_count,err_count

if __name__=='__main__':
   db_client = InfluxDBClient('localhost',8086,'root','root','')
   data_list = db_client.get_list_database()
   database_list = []
   while True:
       # since_time = datetime.datetime().now().strftime("%Y-%m-%d %H:%M:%S")
       time.sleep(1)
       try:
         logs = get_logs()
         correct_dict, error_dict,count,cor_count,err_count = parse_logs(logs)
         db_client = InfluxDBClient('localhost',8086,'root','root','metric_db')
         json_body = []
         count_dict = {}

         #将api名拼接到字典字符串，然后再将字符串转为字典数据
         for key in correct_dict.keys():
             str_data = " { 'measurement' : '" + str(key)+"eq200"+"','fields' :{'value': " + str(correct_dict[key])+"}}"
             dict_data = eval(str_data)
             json_body.append(dict_data)
         for key in error_dict.keys():
             err_data = " { 'measurement' : '" + str(key)+"bt400"+"','fields' :{'value': " + str(error_dict[key])+"}}"
             dict_data = eval(err_data)
             json_body.append(dict_data)
         count_dict['cor_count'] = cor_count
         count_dict['err_count'] = err_count
         count_dict['count'] = count 
         for key in count_dict.keys():
             str_data = " { 'measurement' : '" + str(key) +"','fields' :{'value': " + str(count_dict[key])+"}}" 
             dict_data = eval(str_data) 
             json_body.append(dict_data)
         
         #将数据写入数据库
         db_client.write_points(json_body)

       except Exception,e:
         print str(e)
