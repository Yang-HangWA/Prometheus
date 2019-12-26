#encoding
import commands
import os,sys,string
import re

def pkill(get_info):
    ps_command = "ps -ef | grep "+ str(get_info)
    p = commands.getoutput(ps_command)
    ids = p.split("\n")
    py_str = "python ./get_info_script/"+str(get_info)
    for id in ids:
        if py_str in id:
            process_id = id.split()[1]
            command = "sudo kill -9 "+str(process_id)
            os.system(command)

if __name__ == '__main__' :
    pkill("get_pg_info")
    pkill("get_redis_info")
    pkill("get_host_info")
    pkill("get_disque_info")
    pkill("get_openresty_info")
