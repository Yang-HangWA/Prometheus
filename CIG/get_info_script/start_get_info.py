#encoding=utf-8
import os
import time
def start_get_info(get_info):
    command = "sudo nohup python ./get_info_script/" + str(get_info) + "&"
    os.system(command)


if __name__=='__main__':
   time.sleep(4)
   start_get_info("get_disque_info.py")
   time.sleep(3)
   start_get_info("get_pg_info.py")
   time.sleep(3)
   start_get_info("get_host_info.py")
   time.sleep(3)
   start_get_info("get_redis_info.py")
   time.sleep(3)
   start_get_info("get_openresty_info.py")
