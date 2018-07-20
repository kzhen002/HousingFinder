import sys
import json
import csv
import requests
import datetime
from bs4 import BeautifulSoup

class listing(object):
	def __init__(self,url):
		self.url=url
		self.price=0
		self.address="None"
		self.latitude=0
		self.longitude=0
		self.mapUrl="None"
		self.avgTime=""
		self.avgDistance=""
		#self.imageUrls=list()
		self.datePosted="None"
	# For debugging
	def display(self):
		print("===============================================================================================")
		print("URL: "+self.url)
		print("Price: "+self.price)
		print("Address: "+self.address)
		print("Latitude: "+self.latitude)
		print("Longitude: "+self.longitude)
		print("Google Maps: "+self.mapUrl)
		print("Average Travel Time: "+str(self.avgTime))
		print("Average Distance: "+str(self.avgDistance))
		#print(self.imageUrls)
		print("Date: "+self.datePosted)
		print("===============================================================================================")

def getAvgTravelTimeAndDistance(origin,destinations,GOOGLE_API_KEY):
	time=0
	distance=0
	for destination in destinations:
		distanceMatrixRequestUrl="https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+origin+"&destinations="+destination+"&key="+GOOGLE_API_KEY
		distanceMatrix=requests.get(distanceMatrixRequestUrl)
		distanceMatrixJson=distanceMatrix.json()
		#print(distanceMatrixRequestUrl)
		#print(json.dumps(distanceMatrixJson, indent=3))
		#THe value is always in meters even though I asked for imperial wtf
		distance+=distanceMatrixJson['rows'][0]['elements'][0]['distance']['value']
		time+=distanceMatrixJson['rows'][0]['elements'][0]['duration']['value']
	return "{0:.2f}".format(time/len(destinations)/60),"{0:.2f}".format(distance/len(destinations)/1609)

def writeToFile(listings):
	filename=datetime.datetime.today().strftime('%m-%d-%Y')+"_CraigsList.csv"
	csvfile = open(filename,"w",newline='')
	outfile = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
	outfile.writerow(['Date','Price','avgDistance','avgTime','Address','CraigsList','Google Maps'])
	for key,val in listings.items():
		row=[val.datePosted,val.price,val.avgDistance,val.avgTime,val.address,val.url,val.mapUrl]
		outfile.writerow(row)
	csvfile.close()

GOOGLE_API_KEY="INSERT_API_KEY_HERE"
UCSD_COORD="32.8800604,-117.2362022"
DAYBREAK_COORD="32.9903121,-117.0818057"
DESTINATION_ARRAY=["32.8800604,-117.2362022","32.9903121,-117.0818057"]
listings = {}
# Create custom filtering later. For now its hard coded
searchUrl='https://sandiego.craigslist.org/search/apa?postedToday=1&search_distance=30&postal=92122&max_price=3300&min_bedrooms=3&max_bedrooms=3&availabilityMode=0&pets_dog=1&sale_date=all+dates'
source = requests.get(searchUrl)
soup = BeautifulSoup(source.text,'html.parser')

# Grab all urls from the initial search page
resultRows = soup.find_all('li', attrs={'class':'result-row'})
for result in resultRows:
	url = result.find('a',attrs={'class':'result-title'})['href']
	listings[url] = listing(url)
	listings[url].price=result.find('span', attrs={'class':'result-price'}).text
	listings[url].datePosted=result.find('time',attrs={'class':'result-date'})['datetime']
# Grab data for each listing we found
for key,val in listings.items():
	print(key)
	source = requests.get(key)
	soup = BeautifulSoup(source.text,'html.parser')
	listings[key].latitude = soup.find('div',attrs={'class':'viewposting'})['data-latitude']
	listings[key].longitude = soup.find('div',attrs={'class':'viewposting'})['data-longitude']
	address = soup.find('div',attrs={'class':'mapaddress'})
	# Address is not always provided
	if address != None:
		listings[key].address = address.text
	else:
		listings[key].address="Address was not provided."
	listings[key].mapUrl = soup.find('p',attrs={'class':'mapaddress'}).find('small').find('a')['href']
	origin=listings[key].latitude+","+listings[key].longitude
	listings[key].avgTime,listings[key].avgDistance=getAvgTravelTimeAndDistance(origin,DESTINATION_ARRAY,GOOGLE_API_KEY)	
	listings[key].display()

writeToFile(listings)