docker-compose up -d
nohup ./redis_exporter/redis_exporter  -redis.password penetration -redis.addr  redis://localhost:6379  > /dev/null &
docker run --name pg_exporter --net=host -e DATA_SOURCE_NAME="postgres://postgres:postgres@localhost:5432/?sslmode=disable" wrouesnel/postgres_exporter  > /dev/null &

ti1=`date +%s`
ti2=`date +%s`
i=$(($ti2 - $ti1 ))
while [[ "$i" -ne 3 ]]
do 
    ti2=`date +%s`
    i=$(($ti2 - $ti1 ))
done
clear
