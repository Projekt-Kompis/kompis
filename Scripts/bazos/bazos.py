#!/bin/python
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup
from collections import OrderedDict
from fuzzywuzzy import fuzz
from datetime import datetime
import unidecode
import re

def loadListing(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	information = OrderedDict()
	title_tag = soup.find('h1', attrs = {'class' : 'nadpis'})
	date_tag = title_tag.find_next_sibling('span', attrs = {'class' : 'velikost10'})
	datetimeobject = datetime.strptime(date_tag.text.split("[")[1].split("]")[0], '%d.%m. %Y')
	description = soup.find('div', attrs = {'class' : 'popisdetail'}).text
	table = soup.find('td', attrs = {'class': 'listadvlevo'}).find('table')
	table_rows = table.find_all('tr')
	for row in table_rows:
		table_columns = row.find_all('td')
		information[table_columns[0].text.strip()] = table_columns[1]

	listing = OrderedDict()
	listing['name'] = title_tag.text
	listing['author'] = information['Jméno:'].text.strip()
	listing['price'] = information['Cena:'].text.strip().split(" Kč")[0].replace(" ","")
	try:
		listing['price'] = int(listing['price'])
	except:
		listing['price'] = 0
	listing['store_url'] = url
	listing['description'] = description
	listing['location'] = information['Lokalita:'].find_next_sibling('td').text
	listing['time_created'] = datetimeobject.strftime('%Y-%m-%d %H:%M:%S')
	searchable = unidecode.unidecode(listing['name'].lower() + listing['description'].lower()) #unidecode removes diacritics
	if "koupim" in searchable or "prodano" in searchable or "vymenim" in searchable:
		return False
	if ("nove" in searchable or "novy" in searchable or "nova" in searchable or "novou" in searchable or "nerozbalen" in searchable) and not "jako nov" in searchable:
		listing['item_condition'] = 'new'
	elif "zánovní" in searchable:
		listing['item_condition'] = 'unpacked'
	else:
		listing['item_condition'] = 'used'
	return listing

def scrapePage(url):
	listings = []
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	tables = soup.find_all('table', attrs = {'class' : 'inzeraty'})
	for row in tables:
		link = row.find('a', href=True)
		if not link:
			continue
		url = f"https://pc.bazos.cz{link['href']}"
		listings.append(url)
	return listings

def getAllCPUModels():
	cursor = connection.cursor()
	cursor.execute("SELECT id, model FROM part WHERE type = 'cpu'")
	models = cursor.fetchall()
	return models

def getAllCPUSockets():
	cursor = connection.cursor()
	cursor.execute("SELECT cpu_socket FROM `part_cpu` GROUP BY cpu_socket")
	models = cursor.fetchall()
	return models

def getAllGPUModels():
	cursor = connection.cursor()
	cursor.execute("SELECT id, model FROM part WHERE type = 'gpu'")
	models = cursor.fetchall()
	return models

def getMatchingModelID(title, description, models):
	finalratio = 0
	currentmodel = 0
	currentmodelname = ""
	for model in models:
		ratio = (fuzz.partial_ratio(model[1], title) * 4) + fuzz.partial_ratio(model[1], description)
		if ratio > finalratio:
			finalratio = ratio
			currentmodel = model[0]
			currentmodelname = model[1]
	print(f"{title} - {currentmodelname} - {finalratio}")
	if(finalratio < 400):
		return False
	return currentmodel

def getMatchingCPUSocket(title, description, sockets):
	#TODO: chipset based socket detection
	searchable = unidecode.unidecode(title.lower() + description.lower())
	for socket in sockets:
		if socket[0] in searchable:
			return socket[0]
	return 0

def getMatchingDDRVersion(title, description):
	#TODO: group by searching so it can find the most frequent ddr version if its not mentioned in the listing
	searchable = unidecode.unidecode(title.lower() + description.lower())
	for x in range(5):
		if f"ddr{x}" in searchable:
			return x
	return 4

def getRAMSize(title):
	title = title.lower()
	m = re.search('[0-9]*x[0-9]*', title)
	multiplier = 1
	size = 0
	if m:
		found = m.group(0)
		split = found.split("x")
		try:
			size = int(split[0]) * int(split[1])
		except:
			size = 0
	if "gb" in title:
		multiplier = 1024
		unit = "gb"
	elif "mb" in title:
		unit = "mb"
	else:
		print("Unable to determine RAM size")
		return 0
	if size == 0:
		m = re.search(r'\d+', title.split(unit)[0].strip())
		if m:
			try:
				size = int(m.group(0))
			except:
				return 0
	return size * multiplier

def getOpticalType(title, description):
	searchable = unidecode.unidecode(title.lower() + " " + description.lower())
	m = re.search(r'br[a-z\-]*|hddvd[a-z\-]*|hd-dvd[a-z\-]*|dvd[a-z\-]*', searchable)
	if m:
		return m.group(0)
	return False

def getMatchingRAMSpeed(title, ddr_version):
	title = title.lower()
	speed = 0
	if "mhz" in title:
		m = re.search(r'\d+$', re.sub(r'[^0-9 ]', '', title.split("mhz")[0].strip())) #TODO: improve this regex so we don't end up with 283200 MHz when the source says 2x8GB3200MHz
		if m:
			try:
				speed = int(m.group(0))
			except:
				return 0
	elif f"ddr{ddr_version}" in title:
		splitresult = title.split(f"ddr{ddr_version}")
		if len(splitresult) <= 1:
			return 0
		m = re.search('[0-9]+', splitresult[1].strip())
		if m:
			try:
				speed = int(m.group(0))
			except:
				return 0
	if(speed < 400):
		return 0
	return speed

def insertListing(listing):
	print(f"Inserting: {listing['name']}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO listing (store, item_condition, price, author, location, name, description, store_url, part_id, time_created) VALUES ('bazos', %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE part_id = VALUES(part_id), description = VALUES(description), price = VALUES(price)"
	sqlVAL = listing['item_condition'], listing['price'], listing['author'], listing['location'], listing['name'], listing['description'], listing['store_url'], listing['part_id'], listing['time_created']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()

def insertPart(part):
	print(f"Inserting: {part['model']}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part (model, brand, type) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE model = VALUES(model), brand = VALUES(brand), id=LAST_INSERT_ID(id)"
	sqlVAL = part['model'], part['brand'], part['type']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def insertPartMotherboard(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_motherboard (motherboard_form_factor, cpu_socket, ddr_version, part_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE motherboard_form_factor = VALUES(motherboard_form_factor), cpu_socket = VALUES(cpu_socket), ddr_version = VALUES(ddr_version), id=LAST_INSERT_ID(id)"
	sqlVAL = part['motherboard_form_factor'], part['cpu_socket'], part['ddr_version'], part['part_id']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def insertPartRAM(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_ram (ddr_version, speed, size, part_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE ddr_version = VALUES(ddr_version), speed = VALUES(speed), id=LAST_INSERT_ID(id)"
	sqlVAL = part['ddr_version'], part['speed'], part['size'], part['part_id']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def insertPartOS(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_os (invoice, part_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE invoice = VALUES(invoice), id=LAST_INSERT_ID(id)"
	sqlVAL = part['invoice'], part['part_id']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def insertPartOptical(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_optical (optical_type, part_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE optical_type = VALUES(optical_type), id=LAST_INSERT_ID(id)"
	sqlVAL = part['optical_type'], part['part_id']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def isListingPresent(url):
	cursor = connection.cursor()
	sqlIN = "SELECT count(*) FROM listing WHERE store_url = %s"
	sqlVAL = [url]
	cursor.execute(sqlIN, sqlVAL)
	total = cursor.fetchone()
	if total[0] > 0:
		return True
	return False

def isOSWithInvoice(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	return "faktur" in searchable and not "bez faktur" in searchable

def isOpticalDrive(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	return ("mechanik" in searchable or "vypalovack" in searchable) and "disket" not in searchable

def scrapeCPUs():
	models = getAllCPUModels()
	page = 0;
	while True:
		listings = scrapePage(f"https://pc.bazos.cz/procesor/{page}/")
		if not listings:
			return
		for listing in listings:
			if isListingPresent(listing):
				return
			listing_details = loadListing(listing)
			if not listing_details:
				continue
			listing_details['part_id'] = getMatchingModelID(listing_details['name'], listing_details['description'], models)
			if not listing_details['part_id']:
				continue
			insertListing(listing_details)
		page += 20

def scrapeGPUs():
	models = getAllGPUModels()
	page = 0;
	while True:
		listings = scrapePage(f"https://pc.bazos.cz/graficka/{page}/")
		if not listings:
			return
		for listing in listings:
			if isListingPresent(listing):
				return
			listing_details = loadListing(listing)
			if not listing_details:
				continue
			listing_details['part_id'] = getMatchingModelID(listing_details['name'], listing_details['description'], models)
			if not listing_details['part_id']:
				continue
			insertListing(listing_details)
		page += 20

def scrapeMotherboards():
	sockets = getAllCPUSockets()
	page = 0;
	while True:
		listings = scrapePage(f"https://pc.bazos.cz/motherboard/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_motherboard = OrderedDict();
			if isListingPresent(listing):
				return
			listing_details = loadListing(listing)
			if not listing_details:
				continue
			part['model'] = listing_details['name']
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'motherboard'
			part_motherboard['motherboard_form_factor'] = 'ATX'
			part_motherboard['cpu_socket'] = getMatchingCPUSocket(listing_details['name'], listing_details['description'], sockets)
			part_motherboard['ddr_version'] = getMatchingDDRVersion(listing_details['name'], listing_details['description'])
			listing_details['part_id'] = part_motherboard['part_id'] = insertPart(part)
			insertPartMotherboard(part_motherboard)
			insertListing(listing_details)
		page += 20

def scrapeRAMs():
	#TODO: filter out flash disks
	#TODO: deal with laptop ram
	#TODO: ddr400 is not ddr4
	sockets = getAllCPUSockets()
	page = 0;
	while True:
		listings = scrapePage(f"https://pc.bazos.cz/pamet/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_ram = OrderedDict();
			if isListingPresent(listing):
				return
			listing_details = loadListing(listing)
			if not listing_details:
				continue
			part['model'] = listing_details['name']
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'ram'
			part_ram['size'] = getRAMSize(listing_details['name'])
			if part_ram['size'] == 0:
				continue
			part_ram['ddr_version'] = getMatchingDDRVersion(listing_details['name'], listing_details['description'])
			part_ram['speed'] = getMatchingRAMSpeed(listing_details['name'], part_ram['ddr_version'])
			print(f"{part_ram['speed']} MHz === {listing_details['name']}")
			listing_details['part_id'] = part_ram['part_id'] = insertPart(part)
			insertPartRAM(part_ram)
			insertListing(listing_details)
		page += 20

def scrapeOSes():
	#TODO: filter out listings with no license 
	sockets = getAllCPUSockets()
	page = 0;
	while True:
		listings = scrapePage(f"https://pc.bazos.cz/software/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_os = OrderedDict();
			if isListingPresent(listing):
				return
			listing_details = loadListing(listing)
			if not listing_details:
				continue
			if "windows " not in listing_details['name'].lower():
				continue
			part['model'] = listing_details['name']
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'os'
			part_os['invoice'] = isOSWithInvoice(listing_details['name'], listing_details['description'])
			listing_details['part_id'] = part_os['part_id'] = insertPart(part)
			insertPartOS(part_os)
			insertListing(listing_details)
		page += 20

def scrapeOptical():
	sockets = getAllCPUSockets()
	page = 0;
	while True:
		listings = scrapePage(f"https://pc.bazos.cz/cd/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_optical = OrderedDict();
			if isListingPresent(listing):
				return
			listing_details = loadListing(listing)
			if not listing_details or not isOpticalDrive(listing_details['name'], listing_details['description']):
				continue
			part['model'] = listing_details['name']
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'optical'
			part_optical['optical_type'] = getOpticalType(listing_details['name'], listing_details['description'])
			listing_details['part_id'] = part_optical['part_id'] = insertPart(part)
			insertPartOptical(part_optical)
			insertListing(listing_details)
		page += 20


try:
	connection = mysql.connector.connect(host = credentials.dbhost, \
	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
except:
    print("No connection to Database")
    sys.exit(0)
print("Connection successful!")

scrapeCPUs()
scrapeGPUs()
scrapeMotherboards()
scrapeRAMs()
scrapeOSes()
scrapeOptical()