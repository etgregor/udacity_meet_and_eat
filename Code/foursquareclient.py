'''
 - Geocodifica direcciones con la api de google
 - @etgregor
 - Marzo, 2016
'''
import json
import httplib2

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

from googleclient import GoogleClient
from foundvenue import FundVenue

class FoursquareClient(object):
	""" Cliente para forsquare """
	apiClientId = ''
	apiClientSecret = ''
	photo_width = 300
	photo_heigth = 300

	def getParamAuth(self):
		authParam = "&client_id=%s&client_secret=%s" % (self.apiClientId, self.apiClientSecret)
		return authParam

	def getAllVenuePhotosInfo(self, venueId):
		#https://api.foursquare.com/v2/venues/43695300f964a5208c291fe3/photos?oauth_token=BM35PLFN2DFOZNMMO3HFL0UC33ZGYWTYWSEDVUJLPOEIR5MQ&v=20160218&limit=2
		authParam = self.getParamAuth()
		photosUri = ('https://api.foursquare.com/v2/venues/%s/photos?%s&v=20160218&limit=1'% (venueId, authParam))
		h = httplib2.Http()
		response,content = h.request(photosUri, "GET")
		jsonResult = json.loads(content)
		photos = jsonResult['response']['photos']
		
		return photos


	def getFistrVenuePhotoInfo(self, venueId):
		#https://api.foursquare.com/v2/venues/43695300f964a5208c291fe3/photos?oauth_token=BM35PLFN2DFOZNMMO3HFL0UC33ZGYWTYWSEDVUJLPOEIR5MQ&v=20160218&limit=2
		allPhotosInfo = self.getAllVenuePhotosInfo(venueId=venueId)
		firstPhoto = None
		if allPhotosInfo['count'] > 0:
			firstPhoto = allPhotosInfo['items'][0]
		
		return firstPhoto


	def getVeueFisrtPhotoUriOfPlace(self, venueId, wsize, hsize):
		#https://irs0.4sqi.net/img/general/300x500/2341723_vt1Kr-SfmRmdge-M7b4KNgX2_PHElyVbYL65pMnxEQw.jpg.
		firstPhoto = self.getFistrVenuePhotoInfo(venueId=venueId)
		photoUri = ""
		if firstPhoto is not None:
			photoUri = "%s%sx%s%s" % (firstPhoto['prefix'],wsize, hsize ,firstPhoto['suffix'])
		
		return photoUri

	def getVenueInfo(self, mealType, lat, lng):
		authParam = self.getParamAuth()
		versionParam = "&v=20130815"
		locationParam = "&ll=%s,%s" % (lat, lng) 
		queryParam = "&query=%s" % (mealType)
		limpitParam = "&limit=1"

		url = ('https://api.foursquare.com/v2/venues/search?%s%s%s%s%s'% (authParam, versionParam, locationParam, queryParam,limpitParam))
		
		h = httplib2.Http()
		response,content = h.request(url, "GET")
		jsonResult = json.loads(content)

		firstVenue = jsonResult['response']['venues'][0]
		return firstVenue


	def findAVenue(self, mealType, address):
		""" Encuentra un lugar """
		geocoding = GoogleClient()
		location = geocoding.getLocationFromAddress(address=address)
		if location is None:
			return None

		lat = location[0]
		lng = location[1]
		venue = self.getVenueInfo(mealType = mealType, lat = lat, lng = lng)

		if venue is None:
			return None

		venueId = venue['id']
		name = venue['name']
		firstPhotoUri = self.getVeueFisrtPhotoUriOfPlace(venueId = venueId, wsize = self.photo_width, hsize = self.photo_heigth)

		address = ""
		full_address = venue['location']['formattedAddress']
		for addres_part in full_address:
			address += addres_part + " "
		
		venue = FundVenue(name = name, address = address, photo = firstPhotoUri, nearvylatlon = '%s,%s' % (lat, lng) )
		return venue

	"""Cliente de foursquare"""
	def __init__(self):
		# Lee el archivo de configuracion para el clientid y el clientsecret
		config  = json.loads(open('config.json', 'r').read())
		self.apiClientId = config['Foursquare']['client_id']
		self.apiClientSecret = config['Foursquare']['client_secret']





	