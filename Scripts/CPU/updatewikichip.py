#!/bin/python
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup

import json
import requests
import time

def loadwiki(pagetitle):
	response = requests.get('https://en.wikichip.org/w/api.php', params={'action':'parse', 'page':pagetitle, 'prop':'wikitext', 'format':'json'})
	if response.status_code != 200:
		print(f"SERVER ERROR {response.status_code}, WAITING")
		time.sleep(2)
		print("RETRYING")
		return loadwiki(pagetitle)
	obj = json.loads(response.text)
	if "error" in obj:
		return -1
	wikitext = obj["parse"]["wikitext"]["*"]
	if wikitext.replace(" ","").find("#REDIRECT") != -1:
		wikitext = loadwiki(wikitext.split("[[")[1].split("]]")[0])
		if wikitext == -1:
			return -1
	return wikitext

try:
	connection = mysql.connector.connect(host = credentials.dbhost, \
	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
except:
    print("No connection to Database")
    sys.exit(0)
print("Connection succesfull!")

sql_select_Query = "SELECT part_cpu.part_id, part.model FROM `part` INNER JOIN part_cpu ON part_cpu.part_id = part.id WHERE part.type = 'CPU' AND part_cpu.cpu_socket = '0'"
cursor = connection.cursor()
cursor.execute(sql_select_Query)
records = cursor.fetchall()
print("CPUs to update: ", cursor.rowcount)

print("\nUpdating each CPU record")
for row in records:
	print(f"CPU: {row[1]}")
	wikitext = loadwiki(row[1])
	if wikitext == -1:
		continue
	if wikitext.find("{{chip") == -1:
		continue
	chipinfobox = wikitext.replace("\n","").split("{{chip|")[1].split("}}")[0].split("|")
	chipinfobox = dict(s.split('=') for s in chipinfobox)
	if not all (k in chipinfobox for k in ("tdp", "frequency", "core count")):
		continue
	if "package module 1" in chipinfobox:
		packagemodule = chipinfobox['package module 1'].split("{{")[1]
		wikitext = loadwiki(f'template:{packagemodule}')
		if wikitext == -1:
			continue
		if wikitext.find("[[socket::") != -1:
			socket = wikitext.split("[[socket::")[1].split("]]")[0].split("|")[0].replace("-", "").replace("Socket ","")
		elif wikitext.find("[[package::") != -1:
			socket = wikitext.split("[[package::")[1].split("]]")[0].split("|")[0].replace("-", "").replace("Package ","")
		else:
			continue
	elif "package name 1" in chipinfobox:
		socket = chipinfobox['package name 1'].split(",")[1].replace("_","").replace("fclga","LGA")
	else:
		continue
	frequency = chipinfobox['frequency'].replace(",", "").replace(" ", "")
	if frequency.find("GHz") != -1:
		frequency = int(frequency.split("GHz")[0]) * 1000
	elif frequency.find("MHz") != -1:
		frequency = int(frequency.split("MHz")[0])
	else:
		continue
	tdp = chipinfobox['tdp'].split(" ")[0]
	cursor = connection.cursor()
	sqlIN = "UPDATE part_cpu SET tdp = %s, cpu_socket = %s, frequency = %s, core_count = %s WHERE part_id = %s"
	print(f"==CPU==\nTDP: {tdp}\nSocket: {socket}\nFrequency: {frequency}\nCore count: {chipinfobox['core count']}")
	sqlVAL = tdp, socket, frequency, chipinfobox['core count'], row[0]
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()

	

	# model = "AMD " + row[1].replace("TR", "Threadripper")
	# print(model)
	# cpuinfo = list(filter(lambda x:x["Model"]==model,obj["data"]))
	# if not cpuinfo:
	# 	cpuinfo = list(filter(lambda x:x["Model"]==f"{model} Processor (OEM only)",obj["data"]))
	# 	if not cpuinfo:
	# 		continue
	# cpuinfo = cpuinfo[0]
	# print(cpuinfo["Model"])
	# frequency = int(float(cpuinfo["Base Clock"].replace("GHz",""))*1000)
	# tdp = cpuinfo["Default TDP / TDP"].replace("W","").replace("+","")
	# if tdp.find("-") != -1:
	# 	tdp = tdp.split("-")[1] #assume higher tdp
	# cursor = connection.cursor()
	# sqlIN = "UPDATE part_cpu SET tdp = %s, cpu_socket = %s, frequency = %s, core_count = %s WHERE part_id = %s"
	# print(f'==CPU==\nTDP: {cpuinfo["Default TDP / TDP"]}\nSocket: {cpuinfo["Package"]}\nFrequency: {frequency}\nCore count: {cpuinfo["# of CPU Cores"]}')
	# sqlVAL = tdp, cpuinfo["Package"], frequency, cpuinfo["# of CPU Cores"], row[0]
	# cursor.execute(sqlIN, sqlVAL)
	# connection.commit()