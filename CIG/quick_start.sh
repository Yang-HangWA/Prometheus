sudo docker-compose up -d
ti1=`date +%s`    #获取时间戳  
ti2=`date +%s`  
i=$(($ti2 - $ti1 ))  
  
while [[ "$i" -ne "3" ]]  
do  
    ti2=`date +%s`  
    i=$(($ti2 - $ti1 ))  
done  
sudo python ./get_info_script/start_get_info.py
ti1=`date +%s`    #获取时间戳  
ti2=`date +%s`  
i=$(($ti2 - $ti1 ))  
  
while [[ "$i" -ne "3" ]]  
do  
    ti2=`date +%s`  
    i=$(($ti2 - $ti1 ))  
done  
clear
