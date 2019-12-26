#encoding=utf-8
import psutil
import time 
from influxdb import InfluxDBClient

class mem_info_type(object):
      def __init__(self,total,free,used):
          self.total = total
          self.free = free
          self.used = used

class swap_info_type(object):
      def __init__(self,total,used):
          self.total = total
          self.used = used

class cpu_info_type(object):
      def __init__(self,cpu_lcount,cpu_wcount,user_times,system_times,idle_times):
          self.cpu_lcount = cpu_lcount
          self.cpu_wcount = cpu_wcount
          self.user_times = user_times 
          self.system_times = system_times
          self.idle_times = idle_times

class net_info_type(object):
      def __init__(self,bytes_sent,bytes_recv,error_in,error_out, packets_sent, packets_recv):
          self.bytes_sent = bytes_sent
          self.bytes_recv = bytes_recv
          self.error_in  = error_in
          self.error_out = error_out
          self.packets_sent = packets_sent
          self.packets_recv = packets_recv

class disk_info_type(object):
      def __init__(self,read_count,write_count,read_bytes,
                        write_bytes,total,used,free,percent):
          self.read_count = read_count
          self.write_count = write_count
          self.read_bytes = read_bytes
          self.write_bytes = write_bytes
          self.total = total 
          self.used = used
          self.free = free
          self.percent = percent

def get_mem_info(): 
    mem = psutil.virtual_memory()
    total_memory = mem.total
    free_memory = mem.free
    used_memory = mem.used
    return mem_info_type(total_memory,free_memory,used_memory)

def get_swap_info(): 
    total_swap = psutil.swap_memory().total
    used_swap = psutil.swap_memory().used
    return swap_info_type(total_swap,used_swap)

def get_cpu_info():
    cpu_lcount = psutil.cpu_count()    #逻辑个数 
    cpu_wcount = psutil.cpu_count(logical=False) #物理个数
    cpu_times = psutil.cpu_times()
    user_times = cpu_times.user
    system_times = cpu_times.system
    idle_times = cpu_times.idle
    return cpu_info_type(cpu_lcount,cpu_wcount,user_times,system_times,idle_times)

def get_net_info():
    net_total = psutil.net_io_counters()
    bytes_sent = net_total.bytes_sent
    bytes_recv = net_total.bytes_recv
    error_in = net_total.errin
    error_out = net_total.errout
    packets_sent = net_total.packets_sent
    packets_recv = net_total.packets_recv
    return net_info_type(bytes_sent,bytes_recv,error_in,error_out, packets_sent, packets_recv)

def get_disk_info():
    disk_total = psutil.disk_io_counters()
    read_count = disk_total.read_count
    write_count = disk_total.write_count
    read_bytes = disk_total.read_bytes
    write_bytes = disk_total.write_bytes
    disk_usage = psutil.disk_usage('/') 
    total = disk_usage.total
    used = disk_usage.used
    free = disk_usage.free
    percent = disk_usage.percent
    return disk_info_type(read_count,write_count,read_bytes,write_bytes,
                          total,used,free,percent) 

if __name__=='__main__':
   while True:
         time.sleep(1)
         try:
             mem_info = get_mem_info()
             swap_info = get_swap_info()
             cpu_info = get_cpu_info()
             net_info = get_net_info()
             disk_info = get_disk_info()
             db_client = InfluxDBClient('localhost',8086,'root','root','metric_db')
             json_body = [
             #memory
             { "measurement" : "host_total_memory","fields" :{"value": mem_info.total}},
             { "measurement" : "host_free_memory","fields" :{"value": mem_info.free}},
             { "measurement" : "host_used_memory","fields" :{"value": mem_info.used}},
             #swap
             { "measurement" : "host_total_swap","fields" :{"value": swap_info.total}},
             { "measurement" : "host_used_swap","fields" :{"value": swap_info.used}},
             #cpu
             { "measurement" : "host_cpu_lcount","fields" :{"value": cpu_info.cpu_lcount}},
             { "measurement" : "host_cpu_wcount","fields" :{"value": cpu_info.cpu_wcount}},
             { "measurement" : "host_cpu_user_times","fields" :{"value": cpu_info.user_times}},
             { "measurement" : "host_cpu_system_times","fields" :{"value": cpu_info.system_times}},
             { "measurement" : "host_cpu_idle_times","fields" :{"value": cpu_info.idle_times}},
             #net
             { "measurement" : "host_net_bytes_sent","fields" :{"value": net_info.bytes_sent}},
             { "measurement" : "host_net_bytes_recv","fields" :{"value": net_info.bytes_recv}},
             { "measurement" : "host_net_error_in","fields" :{"value": net_info.error_in}},
             { "measurement" : "host_net_error_out","fields" :{"value": net_info.error_out}},             
             { "measurement" : "host_net_packets_sent","fields" :{"value": net_info.packets_sent}},
             { "measurement" : "host_net_packets_recv","fields" :{"value": net_info.packets_recv}},
             #disk
             { "measurement" : "host_disk_read_count","fields" :{"value": disk_info.read_count}},
             { "measurement" : "host_disk_write_count","fields" :{"value": disk_info.write_count}},
             { "measurement" : "host_disk_read_bytes","fields" :{"value": disk_info.read_bytes}},
             { "measurement" : "host_disk_write_bytes","fields" :{"value": disk_info.write_bytes}}, 
             { "measurement" : "host_disk_total","fields" :{"value": disk_info.total}},
             { "measurement" : "host_disk_used","fields" :{"value": disk_info.used}}, 
             { "measurement" : "host_disk_used_precent","fields" :{"value": disk_info.percent}},           
             { "measurement" : "host_disk_free","fields" :{"value": disk_info.free}},
             ]
             db_client.write_points(json_body)
         except Exception,e:
             print str(e) 
