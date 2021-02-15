#!/bin/python
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup

import json
import urllib.request

try:
	connection = mysql.connector.connect(host = credentials.dbhost, \
	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
except:
    print("No connection to Database")
    sys.exit(0)
print("Connection succesfull!")

# AMD's processor table is exported using JavaScript, so we cannot download it programatically. 
# This means it will always have to be downloaded manually from https://www.amd.com/en/partner/processor-specifications first
# Also trademark signs have to be removed from the file before processing
# Also note that the AMD CPU list is very incomplete and only includes recent products
data = f = open('tableExport.json',) 

# parse json object
obj = json.load(data)

sql_select_Query = "SELECT part_cpu.part_id, part.model FROM `part` INNER JOIN part_cpu ON part_cpu.part_id = part.id WHERE part.brand = 'AMD' AND part.type = 'CPU' AND part_cpu.cpu_socket = '0'"
cursor = connection.cursor()
cursor.execute(sql_select_Query)
records = cursor.fetchall()
print("CPUs to update: ", cursor.rowcount)

print("\nUpdating each CPU record")
for row in records:
	model = "AMD " + row[1].replace("TR", "Threadripper")
	print(model)
	cpuinfo = list(filter(lambda x:x["Model"]==model,obj["data"]))
	if not cpuinfo:
		cpuinfo = list(filter(lambda x:x["Model"]==f"{model} Processor (OEM only)",obj["data"]))
		if not cpuinfo:
			continue
	cpuinfo = cpuinfo[0]
	print(cpuinfo["Model"])
	frequency = int(float(cpuinfo["Base Clock"].replace("GHz",""))*1000)
	tdp = cpuinfo["Default TDP / TDP"].replace("W","").replace("+","")
	if tdp.find("-") != -1:
		tdp = tdp.split("-")[1] #assume higher tdp
	cursor = connection.cursor()
	sqlIN = "UPDATE part_cpu SET tdp = %s, cpu_socket = %s, frequency = %s, core_count = %s WHERE part_id = %s"
	print(f'==CPU==\nTDP: {cpuinfo["Default TDP / TDP"]}\nSocket: {cpuinfo["Package"]}\nFrequency: {frequency}\nCore count: {cpuinfo["# of CPU Cores"]}')
	sqlVAL = tdp, cpuinfo["Package"], frequency, cpuinfo["# of CPU Cores"], row[0]
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()