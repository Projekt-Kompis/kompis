#!/bin/python
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup

def loadCPU(name):
	data = loadCPUFull(f"Intel {row[1]} Processor")
	if not data:
		data = loadCPUFull(f"Intel {row[1].replace('Pentium', 'Pentium Processor').replace('Core2 Duo','Core2 Duo Processor').replace('Celeron','Celeron Processor').replace('Atom', 'Atom Processor')}")
	return data


def loadCPUFull(model):
	print(f"> {model}")
	for cpu in obj:
		cpuinfo = obj[cpu]
		if model in cpuinfo['name']:
			return cpuinfo
	return False

try:
	connection = mysql.connector.connect(host = credentials.dbhost, \
	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
except:
    print("No connection to Database")
    sys.exit(0)
print("Connection succesfull!")

response = requests.get('https://raw.githubusercontent.com/divinity76/intel-cpu-database/master/databases/intel_cpu_database.json')

obj = json.loads(response.text)

sql_select_Query = "SELECT part_cpu.part_id, part.model FROM `part` INNER JOIN part_cpu ON part_cpu.part_id = part.id WHERE part.brand = 'Intel' AND part.type = 'CPU' AND part_cpu.cpu_socket = '0'"
cursor = connection.cursor()
cursor.execute(sql_select_Query)
records = cursor.fetchall()
print("CPUs to update: ", cursor.rowcount)

print("\nUpdating each CPU record")
for row in records:
	cpuinfo = loadCPU(row[1])
	if not cpuinfo or not all (k in cpuinfo['Performance'] for k in ("TDP", "Processor Base Frequency", "# of Cores")) or not 'Sockets Supported' in cpuinfo['Package Specifications']:
		continue
	print(f"> {cpuinfo['name']}")
	tdp =  cpuinfo['Performance']['TDP'].split(" ")[0]
	cpu_socket = cpuinfo['Package Specifications']['Sockets Supported'].replace("FCLGA","LGA")
	frequency = int(float(cpuinfo['Performance']['Processor Base Frequency'].split(" ")[0])*1000)
	core_count = cpuinfo['Performance']['# of Cores'] 
	cursor = connection.cursor()
	sqlIN = "UPDATE part_cpu SET tdp = %s, cpu_socket = %s, frequency = %s, core_count = %s WHERE part_id = %s"
	print(f'==CPU==\nTDP: {tdp}\nSocket: {cpu_socket}\nFrequency: {frequency}\nCore count: {core_count}')
	sqlVAL = tdp, cpu_socket, frequency, core_count, row[0]
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()