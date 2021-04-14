#!/usr/bin/python3
import sys
import requests
import json
import mysql.connector
import credentials
from bs4 import BeautifulSoup
from collections import OrderedDict
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta
import unidecode
import re

global lastListings
lastListings = []

#TODO: ability to run the script and only update one category of parts
def printTime(start):
	end = datetime.now()
	tdelta = end - start
	print(start)
	print(end)
	print(tdelta)

def doCommonNameReplacements(string):
	return string.lower().replace("-"," ").replace("ti", " ti").replace("super"," super").replace("  "," ").replace("pen tium","pentium").strip()

def getItemCondition(searchable):
	if ("nove" in searchable or "novy" in searchable or "nova" in searchable or "novou" in searchable or "nerozbalen" in searchable) and not "jako nov" in searchable:
		return 'new'
	elif "zánovní" in searchable:
		return 'unpacked'
	else:
		return 'used'

def containsBlacklisted(searchable):
	blacklist = ['koupim', 'prodano', 'vymenim', 'nefunkcn', 'rozbit', 'poskozen', 'shanim', 'hledam', 'objednam', 'vadna', 'diskstation', 'nahradni dil']
	for word in blacklist:
		if word in searchable:
			return True
	return False

def loadListing(listing, store):
	if store == "bazos":
		return loadListingBazos(listing)
	elif store == "hyperinzerce":
		return loadListingHyperinzerce(listing)
	elif store == "bazarcz":
		return loadListingBazarcz(listing)
	return False

def loadListingBazos(url):
	print(url)
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	if "<b>Inzerát byl vymazán.</b>" in str(page.content.decode('utf-8')):
		return False;

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
	if listing['price'] < 10 or listing['price'] == 1234: #assuming negotiated price ("cena dohodou")
		listing['price'] = 0
	listing['store_url'] = url
	listing['description'] = description
	listing['location'] = information['Lokalita:'].find_next_sibling('td').text
	listing['time_created'] = datetimeobject.strftime('%Y-%m-%d %H:%M:%S')
	listing['store'] = 'bazos'
	searchable = unidecode.unidecode(listing['name'].lower() + listing['description'].lower()) #unidecode removes diacritics
	if containsBlacklisted(searchable):
		return False
	m = re.search(r'cena.*v eur', searchable)
	if m:
		listing['price'] = int(listing['price'] * 26.1)
	listing['item_condition'] = getItemCondition(searchable)
	return listing

def scrapePageBazos(url):
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

def loadListingHyperinzerce(url):
	print(url)
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	if "Stránka, kterou hledáte, bohužel již nebo ještě neexistuje!" in str(page.content.decode('utf-8')):
		return False

	information = OrderedDict()
	try:
		title_tag = soup.find('h1', attrs = {'class' : 'mb-0'})
		info_row = soup.find('div', attrs = {'class' : 'inz_info_nav border-bottom border-light'})
		date_tag = info_row.find('span', attrs = {'class': 'text-light'})
		datetimeobject = datetime.strptime(date_tag.text, '%d.%m.%Y %H:%M')
		description = soup.find('div', attrs = {'class' : 'col-12 inz_description'}).text
	except:
		return False

	listing = OrderedDict()
	listing['name'] = title_tag.text.strip()
	contact_info = soup.find('div', {'class':'col-md-5 contact_info'})
	listing['author'] = contact_info.find('a', href=True).text.strip()
	listing['price'] = soup.find('span', attrs = {'class': 'price'}).text.strip().split(" Kč")[0].replace(" ","")
	try:
		listing['price'] = int(listing['price'])
	except:
		listing['price'] = 0
	if listing['price'] < 10 or listing['price'] == 1234: #assuming negotiated price ("cena dohodou")
		listing['price'] = 0
	listing['store_url'] = url
	listing['description'] = description.strip()
	table = soup.find('div', attrs = {'class': 'row inz_bottom_table'})
	location_head = soup.find('div', text='Oblast inzerce: ')
	location_tag = location_head.find_next_sibling('div')
	listing['location'] = location_tag.text.strip()
	listing['time_created'] = datetimeobject.strftime('%Y-%m-%d %H:%M:%S')
	listing['store'] = 'hyperinzerce'
	searchable = unidecode.unidecode(listing['name'].lower() + listing['description'].lower()) #unidecode removes diacritics
	if containsBlacklisted(searchable):
		return False
	m = re.search(r'cena.*v eur', searchable)
	if m:
		listing['price'] = int(listing['price'] * 26.1)
	listing['item_condition'] = getItemCondition(searchable)
	return listing

def scrapePageHyperinzerce(url):
	listings = []
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	tables = soup.find_all('div', attrs = {'class' : 'inzerat__text'})
	for row in tables:
		link = row.find('a', href=True)
		if not link:
			continue
		url = link['href']
		if "https://pocitace.hyperinzerce.cz" not in url:
			continue
		listings.append(url)
	global lastListings
	if listings == lastListings:
		return []
	lastListings = listings
	return listings

def loadListingBazarcz(url):
	print(url)
	listing = OrderedDict()
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	if "Požadovaný inzerát nenalezen. Prohlédněte si podobné nabídky na našem bazaru." in str(page.content.decode('utf-8')):
		return False;

	information = OrderedDict()
	json_tag = soup.find('script', attrs = {'type' : 'application/ld+json'})
	json_string = json_tag.string.replace("\n","").replace("\r","").replace("\t","")
	json_content = json.loads(json_string)['mainEntity']
	listing['name'] = json_content['name']
	listing['author'] = soup.find('div', attrs = {'class' : 'ico seller'}).text
	listing['price'] = json_content['offers']['price']
	if json_content['offers']['priceCurrency'] != "CZ":
		return False
	try:
		listing['price'] = int(listing['price'])
	except:
		listing['price'] = 0
	if listing['price'] < 10 or listing['price'] == 1234: #assuming negotiated price ("cena dohodou")
		listing['price'] = 0
	listing['store_url'] = url
	description_soup = BeautifulSoup(json_content['description'], 'html.parser')
	listing['description'] = description_soup.text.strip()
	listing['location'] = json_content['offers']['availableAtOrFrom']['name'].strip()
	listing['store'] = 'bazarcz'

	try: #Bazar.cz has an issue where the html code for the description sometimes cuts out midway through which causes our table to be unparseable even though it's present
		table = soup.find('table', attrs = {'class': 'ad_attribs'})
		date_tag_th = table.find('th', text = 'Vložen:')
		date_tag = date_tag_th.find_next_sibling('td')
		datetimeobject = datetime.strptime(date_tag.text, '%d.%m.%Y')
		listing['time_created'] = datetimeobject.strftime('%Y-%m-%d %H:%M:%S')
	except:
		print("Error while determining time created")
		listing['time_created'] = '0000-00-00'

	searchable = unidecode.unidecode(listing['name'].lower() + listing['description'].lower()) #unidecode removes diacritics
	if containsBlacklisted(searchable):
		return False
	m = re.search(r'cena.*v eur', searchable)
	if m:
		listing['price'] = int(listing['price'] * 26.1)
	listing['item_condition'] = getItemCondition(searchable)
	return listing

def scrapePageBazarcz(url):
	listings = []
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	if "Nenalezen žadný inzerát." in soup.text:
		return []
	tables = soup.find_all('div', attrs = {'class' : 'sale-item'})
	for row in tables:
		link = row.find('a', href=True)
		if not link:
			continue
		url = link['href']
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
	finallength = 0
	currentmodel = 0
	currentmodelname = ""
	for model in models:
		ratio = (fuzz.partial_ratio(doCommonNameReplacements(model[1]), doCommonNameReplacements(title)) * 4) + fuzz.partial_ratio(doCommonNameReplacements(model[1]), doCommonNameReplacements(description))
		if ratio > finalratio or (ratio == finalratio and len(model[1]) > finallength):
			finalratio = ratio
			currentmodel = model[0]
			currentmodelname = model[1]
			finallength = len(model[1])
	print(f"{title} - {currentmodelname} - {finalratio}")
	if(finalratio < 400):
		return False
	return currentmodel

def getMatchingCPUSocket(title, description, sockets):
	#TODO: chipset based socket detection
	searchable = unidecode.unidecode(title.lower() + description.lower())
	for socket in sockets:
		if socket[0].lower() in searchable and len(socket[0]) > 2:
			return socket[0]
	return 0

def getMatchingDDRVersion(title, description):
	#TODO: group by searching so it can find the most frequent ddr version if its not mentioned in the listing
	searchable = unidecode.unidecode(title.lower() + description.lower())
	if "ddr400" in searchable:
		return 1
	for x in range(5):
		if f"ddr{x}" in searchable:
			return x
	return 3

def getRAMSize(title):
	title = title.lower()
	size = 0
	multiplier = 1
	if "mb" in title:
		unit = "mb"
	elif "gb" in title:
		multiplier = 1024
		unit = "gb"
	else:
		print("Unable to determine RAM size")
		return 0
	try:
		size = int(re.findall(r'\d+', title.split(unit)[0].strip())[-1])
	except:
		size = 0
	if size == 0:
		m = re.search('[0-9]x[0-9]*', title)
		if m:
			found = m.group(0)
			split = found.split("x")
			try:
				size = int(split[0]) * int(split[1])
			except:
				size = 0
	size = size * multiplier
	if(size > (64*1024)):
		print("RAM size more than 64 GB, assuming invalid")
		return 0
	print(size)
	return size

def getStorageSize(title):
	title = title.lower()
	multiplier = 1
	size = 0
	if "gb" in title:
		multiplier = 1024
		unit = "gb"
	elif "mb" in title:
		unit = "mb"
	elif "tb" in title:
		multiplier = 1024*1024
		unit = "tb"
	else:
		print("Unable to determine storage size")
		return 0
	try:
		return int(re.findall(r'\d+', title.split(unit)[0].strip())[-1]) * multiplier
	except:
		print(f"> {title}")
		print("Unable to determine storage size")
		return 0

def getPSUWattage(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	try:
		if "w" in searchable:
			return int(re.findall(r'\d+', searchable.split("w")[0].strip())[-1])
		else:
			numbers = re.sub(r'[^0-9 ]', '', searchable).split(' ')
			for number in numbers:
				if not number == '' and int(number) > 250 and int(number) < 1500:
					return int(number)
			raise Exception('no wattage')
	except:
		print(f"> {title}")
		print("Unable to determine PSU wattage")
		return 0

def getStorageType(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	if "ssd" in searchable:
		return "ssd"
	if "sshd" in searchable or "hybrid" in searchable:
		return "sshd"
	return "hdd"

def getStorageConnector(title, description):
	searchable =  re.sub(r'[^a-z]', '', unidecode.unidecode(title.lower() + description.lower()))
	if "nvme" in searchable or "pcie" in searchable:
		return "nvme"
	if "m2" in searchable:
		return "m2"
	if "usb" in searchable:
		return "usb"
	if "ide" in searchable:
		return "ide"
	if "nas" in searchable:
		return "nas"
	return "sata"

def getStorageRPM(title, description):
	searchable = re.sub(r'[^0-9]', '', unidecode.unidecode(title.lower() + description.lower()))
	commonspeeds = [5400, 7200, 5900]
	for speed in commonspeeds:
		if str(speed) in searchable:
			return speed
	return 0

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
	if speed < 400 or speed > 4500:
		return 0
	return speed

def insertListing(listing):
	print(f"Inserting: {listing['name']}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO listing (store, item_condition, price, author, location, name, description, store_url, part_id, time_created) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE part_id = VALUES(part_id), description = VALUES(description), price = VALUES(price), is_invalid = 0"
	sqlVAL = listing['store'], listing['item_condition'], listing['price'], listing['author'], listing['location'], listing['name'], listing['description'], listing['store_url'], listing['part_id'], listing['time_created']
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

def insertPartCooler(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_cooler (cpu_socket, part_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE cpu_socket = VALUES(cpu_socket), id=LAST_INSERT_ID(id)"
	sqlVAL = part['cpu_socket'], part['part_id']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def insertPartRAM(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_ram (ddr_version, speed, size, part_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE ddr_version = VALUES(ddr_version), speed = VALUES(speed), size = VALUES(size), id=LAST_INSERT_ID(id)"
	sqlVAL = part['ddr_version'], part['speed'], part['size'], part['part_id']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def insertPartStorage(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_storage (storage_type, connector, rpm, size, part_id) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE storage_type = VALUES(storage_type), connector = VALUES(connector), rpm = VALUES(rpm), size = VALUES(size), id=LAST_INSERT_ID(id)"
	sqlVAL = part['storage_type'], part['connector'], part['rpm'], part['size'], part['part_id']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def insertPartCase(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_case (motherboard_form_factor, psu_form_factor, part_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE motherboard_form_factor = VALUES(motherboard_form_factor), psu_form_factor = VALUES(psu_form_factor), id=LAST_INSERT_ID(id)"
	sqlVAL = part['motherboard_form_factor'], part['psu_form_factor'], part['part_id']
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return cursor.lastrowid

def insertPartPSU(part):
	print(f"Inserting: {str(part['part_id'])}")
	cursor = connection.cursor()
	sqlIN = "INSERT INTO part_psu (wattage, psu_form_factor, part_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE wattage = VALUES(wattage), psu_form_factor = VALUES(psu_form_factor), id=LAST_INSERT_ID(id)"
	sqlVAL = part['wattage'], part['psu_form_factor'], part['part_id']
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

def setListingInvalid(store_url):
	print(f"Marking {store_url} as invalid")
	cursor = connection.cursor()
	sqlIN = "UPDATE listing SET is_invalid = 1 WHERE store_url = %s"
	sqlVAL = [store_url]
	cursor.execute(sqlIN, sqlVAL)
	connection.commit()
	return True

def isOSWithInvoice(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	return "faktur" in searchable and not "bez faktur" in searchable

def isCaseListing(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	return "case" in searchable or "skrin" in searchable or "define r" in searchable

def isPSUListing(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	return ("zdroj" in searchable and not "sada hrebinku" in searchable and not "server ibm" in searchable)

def isOpticalDrive(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	return ("mechanik" in searchable or "vypalovack" in searchable) and "disket" not in searchable

def isGPUCooler(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	return "vodni blok" in searchable

def isRAMInvalid(title, description):
	searchable = unidecode.unidecode(title.lower() + description.lower())
	return "flash" in searchable or "sodimm" in searchable or "so-dimm" in searchable or "karta" in searchable or "fleska" in searchable

def scrapeCPUs(store):
	models = getAllCPUModels()
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/procesor/{bazosPage}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/procesory/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/procesory/{page}/")
		if not listings:
			return
		for listing in listings:
			if isListingPresent(listing) and not doUpdate:
				return
			listing_details = loadListing(listing, store)
			if not listing_details:
				continue
			listing_details['part_id'] = getMatchingModelID(listing_details['name'], listing_details['description'], models)
			if not listing_details['part_id']:
				continue
			insertListing(listing_details)
		page += 1

def scrapeGPUs(store):
	models = getAllGPUModels()
	page = 1;
	while True:
		if store == "bazos":
			listings = scrapePageBazos(f"https://pc.bazos.cz/graficka/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/graficke-karty/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/graficke-karty/{page}/")

		if not listings:
			return
		for listing in listings:
			if isListingPresent(listing) and not doUpdate:
				return
			listing_details = loadListing(listing, store)
			if not listing_details or isGPUCooler(listing_details['name'], listing_details['description']):
				continue
			listing_details['part_id'] = getMatchingModelID(listing_details['name'], listing_details['description'], models)
			if not listing_details['part_id']:
				continue
			insertListing(listing_details)
		page += 1

def scrapeMotherboards(store):
	sockets = getAllCPUSockets()
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/motherboard/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/motherboardy/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/zakladni-desky/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_motherboard = OrderedDict();
			if isListingPresent(listing) and not doUpdate:
				return
			listing_details = loadListing(listing, store)
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
		page += 1

def scrapeRAMs(store):
	#TODO: filter out flash disks
	#TODO: deal with laptop ram
	#TODO: ddr400 is not ddr4
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/pamet/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/pameti/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/pameti/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_ram = OrderedDict();
			if isListingPresent(listing) and not doUpdate:
				return
			listing_details = loadListing(listing, store)
			if not listing_details or isRAMInvalid(listing_details['name'], listing_details['description']):
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
		page += 1

def scrapeOSes(store):
	#TODO: filter out listings with no license 
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/software/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/operacni-systemy/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/operacni-systemy/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_os = OrderedDict();
			if isListingPresent(listing) and not doUpdate:
				return
			listing_details = loadListing(listing, store)
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
		page += 1

def scrapeOptical(store):
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/cd/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/opticke-mechaniky/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/cd-mechaniky/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_optical = OrderedDict();
			if isListingPresent(listing) and not doUpdate:
				return
			listing_details = loadListing(listing, store)
			if not listing_details or not isOpticalDrive(listing_details['name'], listing_details['description']):
				continue
			part['model'] = listing_details['name']
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'optical'
			part_optical['optical_type'] = getOpticalType(listing_details['name'], listing_details['description'])
			listing_details['part_id'] = part_optical['part_id'] = insertPart(part)
			insertPartOptical(part_optical)
			insertListing(listing_details)
		page += 1

def scrapeStorage(store):
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/hdd/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/harddisky/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/pevne-disky/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_storage = OrderedDict();
			if isListingPresent(listing) and not doUpdate:
				return
			listing_details = loadListing(listing, store)
			if not listing_details:
				continue
			part['model'] = listing_details['name']
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'storage'
			part_storage['size'] = getStorageSize(listing_details['name'])
			if part_storage['size'] < 32000:
				continue
			part_storage['storage_type'] = getStorageType(listing_details['name'], listing_details['description'])
			part_storage['connector'] = getStorageConnector(listing_details['name'], listing_details['description'])
			if part_storage['connector'] == "ide" or part_storage['connector'] == "nas":
				continue
			part_storage['rpm'] = getStorageRPM(listing_details['name'], listing_details['description'])
			print(part)
			print(part_storage)
			print("==================")
			listing_details['part_id'] = part_storage['part_id'] = insertPart(part)
			insertPartStorage(part_storage)
			insertListing(listing_details)
		page += 1

def scrapeCases(store):
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/case/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/pc-skrine-zdroje/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/pocitacove-skrine/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_case = OrderedDict();
			listing_details = loadListing(listing, store)
			if not listing_details or not isCaseListing(listing_details['name'], listing_details['description']):
				continue
			if isListingPresent(listing) and not doUpdate:
				return
			part['model'] = listing_details['name']
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'case'
			part_case['motherboard_form_factor'] = 'ATX'
			part_case['psu_form_factor'] = 'ATX'
			print(part)
			print(part_case)
			print("==================")
			listing_details['part_id'] = part_case['part_id'] = insertPart(part)
			insertPartCase(part_case)
			insertListing(listing_details)
		page += 1

def scrapePSUs(store):
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/case/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/pc-zdroje/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/dily-komponenty-zdroje/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_psu = OrderedDict();
			listing_details = loadListing(listing, store)
			if not listing_details or not isPSUListing(listing_details['name'], listing_details['description']) or isCaseListing(listing_details['name'], listing_details['description']):
				continue
			if isListingPresent(listing) and not doUpdate:
				return
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'psu'
			part_psu['wattage'] = getPSUWattage(listing_details['name'], listing_details['description'])
			if part_psu['wattage'] < 200:
				continue
			part_psu['psu_form_factor'] = 'ATX'
			part['model'] = f"{listing_details['name']} ({part_psu['wattage']} W)"
			print(part)
			print(part_psu)
			print("==================")
			listing_details['part_id'] = part_psu['part_id'] = insertPart(part)
			insertPartPSU(part_psu)
			insertListing(listing_details)
		page += 1

def scrapeCoolers(store):
	sockets = getAllCPUSockets()
	page = 1;
	while True:
		if store == "bazos":
			bazosPage = (page-1)*20
			listings = scrapePageBazos(f"https://pc.bazos.cz/chladic/{page}/")
		elif store == "hyperinzerce":
			listings = scrapePageHyperinzerce(f"https://pocitace.hyperinzerce.cz/vetraky-chladice/{page}/")
		elif store == "bazarcz":
			listings = scrapePageBazarcz(f"https://www.bazar.cz/dily-komponenty-chladice/{page}/")
		if not listings:
			return
		for listing in listings:
			part = OrderedDict();
			part_cooler = OrderedDict();
			if isListingPresent(listing) and not doUpdate:
				return
			listing_details = loadListing(listing, store)
			if not listing_details:
				continue
			part['model'] = listing_details['name']
			part['brand'] = listing_details['name'].split(" ")[0]
			part['type'] = 'cooler'
			part_cooler['cpu_socket'] = getMatchingCPUSocket(listing_details['name'], listing_details['description'], sockets)
			listing_details['part_id'] = part_cooler['part_id'] = insertPart(part)
			insertPartCooler(part_cooler)
			insertListing(listing_details)
		page += 1

def updateAll(store):
	cursor = connection.cursor()
	sqlIN = "SELECT part_id, store_url FROM listing WHERE store = %s AND is_invalid = %s"
	sqlVAL = store, 0
	cursor.execute(sqlIN, sqlVAL)
	listings = cursor.fetchall()
	for listing in listings:
		print(listing)
		part = OrderedDict();
		part_case = OrderedDict();
		listing_details = loadListing(listing[1], store)
		if not listing_details:
			setListingInvalid(listing[1])
			continue
		listing_details['part_id'] = listing[0]
		insertListing(listing_details)

functions = {
	"case": scrapeCases,
	"cooler": scrapeCoolers,
	"cpu": scrapeCPUs,
	"gpu": scrapeGPUs,
	"psu": scrapePSUs,
	"motherboard": scrapeMotherboards,
	"ram": scrapeRAMs,
	"os": scrapeOSes,
	"optical": scrapeOptical,
	"storage": scrapeStorage
}

stores = ["bazos", "hyperinzerce", "bazarcz"]

start = datetime.now()

try:
	connection = mysql.connector.connect(host = credentials.dbhost, \
	user = credentials.user, passwd = credentials.passwd, db = credentials.db, port = credentials.port)
except:
    print("No connection to Database")
    sys.exit(0)
print("Connection successful!")

doUpdate = False;
if "--update" in sys.argv:
	doUpdate = True;

if "--store" in sys.argv:
	stores = [sys.argv[sys.argv.index("--store") + 1]]

if "--force-update" in sys.argv:
	for store in stores:
		updateAll(store)
	printTime(start)
	sys.exit(0)

if "--type" in sys.argv:
	for store in stores:
		functions[sys.argv[sys.argv.index("--type") + 1]](store)
else:
	for func in functions:
		for store in stores:
			functions[func](store)


printTime(start)