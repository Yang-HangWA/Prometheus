#encoding=utf-8
import time
import psycopg2
import sys
from influxdb import InfluxDBClient
# Try to connect
def postgres(host, dbname, user, password, dbname_postgres):
	try:
	    conn=psycopg2.connect(host=host, dbname=dbname_postgres, user=user, password=password)
	except:
	    print "I am unable to connect to the database."
	else:
		cur = conn.cursor()
		db = {}

		try:
		    cur.execute("""SELECT * FROM pg_stat_replication;""")
		except:
		    print "I can't SELECT * FROM pg_stat_replication;"
 
		rows = cur.fetchall()
		replic_ip = []
		replic_pid = []
		replic_usesysid = []
		replica_lags = []
		replic_status = []
		replic_stat = len(rows)
		db.update({'replic_status': replic_stat})		
		for row in rows:
			replic_ip.append(row[4])
			replic_pid.append(row[0])
			replic_usesysid.append(row[1])
			try:
			    cur.execute("select greatest(0,pg_xlog_location_diff(pg_current_xlog_location(), replay_location)) from pg_stat_replication where client_addr = %s", (row[4],))
			except:
			    print "I can't select greatest(0,pg_xlog_location_diff(pg_current_xlog_location(), replay_location)) ..."

			rows = cur.fetchall()
			replica_lags.append(float(rows[0][0]))
			
			db.update({'replic_pid': replic_pid, 'replic_usesysid': replic_usesysid, 'replic_ip': replic_ip, 'replica_lags': replica_lags})
	###DB_Size		
		try:
		    cur.execute("""SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;""")
		except:
 	 	    print "I can't SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS ...."

		rows = cur.fetchall()
		for row in rows:
			if row[0] == dbname:
	 			db.update({'db_name': row[0], 'db_size': float(row[1][:-2])})   
	##Deadlocks
		try:
		    cur.execute("""SELECT sum(deadlocks) from pg_stat_database;""")
		except:
		    print "I can't SELECT deadlocks"

		rows = cur.fetchall()
		for row in rows:
                    db.update({'db_deadlocks':float(row[0])})
        
        ##connection
		try:
		    cur.execute("""select count(*) from pg_stat_activity;""")
		except:
		    print "I can't select count(*) from pg_stat_activity;"

		rows = cur.fetchall()
		for row in rows:
			db.update({'total_connections': float(row[0])})
	###MAX Connection
		try:
		    cur.execute("""SHOW max_connections;""")
		except:
		    print "I can't SHOW max_connections"

		rows = cur.fetchall()
		for row in rows:
			db.update({'max_connections': float(row[0])})

		end_connections = db['max_connections'] - db['total_connections']
		db.update({'left_connections': end_connections})
		
		cur.close()
		conn.close()
 	 	return db


      

if __name__ == '__main__':
    host = "127.0.0.1"
    dbname = "postgres"
    user = "postgres"
    password = "postgres"
    dbname_postgres = "postgres"
    
    #connect
    db_client = InfluxDBClient('localhost',8086,'root','root','')
    data_list = db_client.get_list_database()
    database_list = []
    for name_dict in data_list:
      for key,value in name_dict.items():
          database_list.append(value)
    if 'metric_db' not in database_list:
       db_client.create_database('metric_db') 
    db_client.close()

    while True:
    	time.sleep(1)
        try:
    	  get_db = postgres(host, dbname, user, password, dbname_postgres)
          json_body = [ 
          {
          "measurement" : "pg_total_connection",
          "fields" : {
             "value" : int(get_db["total_connections"])
          }
          },
          {
          "measurement" : "pg_max_connections",
          "fields" : {
             "value" : int(get_db["max_connections"])
          }
          },
          {
          "measurement" : "pg_db_deadlocks",
          "fields": {
            "value" : int(get_db["db_deadlocks"])
           }
           },
           {
           "measurement" : "pg_db_size",
           "fields": {
              "value" : int(get_db["db_size"]) 
           }
           }
         # }
          ]
          db_client = InfluxDBClient('localhost',8086,'root','root','metric_db')
          db_client.write_points(json_body)
        except Exception,e:
          print "error:"+str(e)
