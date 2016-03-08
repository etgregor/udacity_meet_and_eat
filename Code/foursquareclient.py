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

class FoursquareClient(object):
	""" Cliente para forsquare """
	apiClientId = ''
	apiClientSecret = ''


	def getAllVenuePhotosInfo(self, venueId):
		#https://api.foursquare.com/v2/venues/43695300f964a5208c291fe3/photos?oauth_token=BM35PLFN2DFOZNMMO3HFL0UC33ZGYWTYWSEDVUJLPOEIR5MQ&v=20160218&limit=2
		authParam = "&client_id=%s&client_secret=%s" % (self.apiClientId, self.apiClientSecret)
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
		
		return photoUr

	def getVenueInfo(self, mealType, location):
		
		lat = location[0]
		lng = location[1]

		authParam = "client_id=%s&client_secret=%s" % (self.apiClientId, self.apiClientSecret)
		
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


	def findARestaurant(self, mealType, address):
		# buscar direccion en google
		location = self.getAddressLocation(address)
		

		venueId = firstVenue['id']

		name = firstVenue['name']

		firstPhotoUri = self.getAllVenuePhotosInfo(venueId = venueId)

		address = ""
		full_address = firstVenue['location']['formattedAddress']
		for addres_part in full_address:
			address += addres_part + " "
	
		return (name,address, firstPhotoUri)

	"""Cliente de foursquare"""
	def __init__(self, clientId, clientSecret):
		# apiClientId = clientId
		# apiClientSecret clientSecret	

#apiClientId = "BETQKBURO2NWRHD5FAKD2HPV1G4YCI0WGSRHW2C0XD15WUAN"
#apiClientSecret = "GE04C20GBDZTHSQZHGETEPP05VV4EBDSKNEGOQDOVLO1YPTK"





	