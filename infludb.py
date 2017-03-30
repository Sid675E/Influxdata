from __future__ import print_function
import psutil
import influxdb
import argparse
import time
import http.client
import urllib
import json
import socket
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import datetime


# Establishing connec
client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='telegraf')

# The list of databases in influxDB
result = client.get_list_database()
print("Result: {0}".format(result))

#print the cpu measurement put by telegraf
rs = client.query("SELECT * from cpu;")
cpu_points = list(rs.get_points(measurement='cpu'))

#get the Cpu usage
cpuu = psutil.cpu_times(percpu=True)
print(cpuu)


# Convert each namedTuple to a json string
cpuu = [json.dumps(stats._asdict()) for stats in cpuu]
print("Result: {0}".format(cpuu))
print(cpuu)


now = datetime.datetime.today()
timeinterval_min = 5  # create an event every x minutes
series=[]

# creating jsom to enter into telegraf table
for i in range(0,len(cpuu)):
	past_date = now - datetime.timedelta(minutes=1 * timeinterval_min)
	#serching for values
	
	cpuu1 = json.loads(cpuu[i])
	guest=cpuu1.get("guest",0.0)
	guest_nice=cpuu1.get("guest_nice",0.0)
	idle=cpuu1.get("idle",0.0)
	iowait=cpuu1.get("iowait",0.0)
	irq=cpuu1.get("irq",0.0)
	nice=cpuu1.get("nice",0.0)
	softirq=cpuu1.get("softirq",0.0)
	steal=cpuu1.get("steal",0.0)
	system=cpuu1.get("system",0.0)
	user=cpuu1.get("user",0.0)
	
	pointValues = {
            "time": past_date.strftime ("%Y-%m-%d %H:%M:%S"),
            "measurement": "cpu",
            'fields':  {
				'usage_guest': guest,
        	    'usage_guest_nice': guest_nice,
    	        'usage_idle': idle,
                'usage_iowait': iowait,
                'usage_irq': irq,
                'usage_nice': nice,
                'usage_softirq': softirq,
                'usage_steal': steal,
                'usage_system': system,
                'usage_user': user,
			},
            'tags': {
                "host_name": socket.gethostname(),
            }

        }
	series.append(pointValues)


print(series)



print("Create a retention policy")
retention_policy = 'awesome_policy'
client.create_retention_policy(retention_policy, '3d', 3, default=True)

print("Write points #: {0}".format(len(cpuu)))
client.write_points(series, retention_policy=retention_policy)

time.sleep(2)

#Printing telegraf
rs = client.query("SELECT * from cpu;")
cpu_points = list(rs.get_points(measurement='cpu'))
print("Result: {0}".format(cpu_points))