# coding=utf-8
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
from restaurant import Restaurant


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
        # https://api.foursquare.com/v2/venues/43695300f964a5208c291fe3/photos?oauth_token=BM35PLFN2DFOZNMMO3HFL0UC33ZGYWTYWSEDVUJLPOEIR5MQ&v=20160218&limit=2
        authParam = self.getParamAuth()
        photosUri = ('https://api.foursquare.com/v2/venues/%s/photos?%s&v=20160218&limit=1' % (venueId, authParam))
        h = httplib2.Http()
        response, content = h.request(photosUri, "GET")
        jsonResult = json.loads(content)
        photos = jsonResult['response']['photos']

        return photos

    def getFistrVenuePhotoInfo(self, venueId):
        # https://api.foursquare.com/v2/venues/43695300f964a5208c291fe3/photos?oauth_token=BM35PLFN2DFOZNMMO3HFL0UC33ZGYWTYWSEDVUJLPOEIR5MQ&v=20160218&limit=2
        allPhotosInfo = self.getAllVenuePhotosInfo(venueId=venueId)
        firstPhoto = None
        if allPhotosInfo['count'] > 0:
            firstPhoto = allPhotosInfo['items'][0]

        return firstPhoto

    def getVenues(self, mealType, lat, lng, limit=1):
        authParam = self.getParamAuth()
        versionParam = "&v=20130815"
        locationParam = "&ll=%s,%s" % (lat, lng)
        queryParam = "&query=%s" % (mealType)
        limpitParam = "&limit=%s" % (limit)

        url = ('https://api.foursquare.com/v2/venues/search?%s%s%s%s%s' % (
        authParam, versionParam, locationParam, queryParam, limpitParam))

        h = httplib2.Http()
        response, content = h.request(url, "GET")
        jsonResult = json.loads(content)

        venues = jsonResult['response']['venues']

        return venues

    def completeRestaurantInfo(self, venue):
        if venue is None:
            return None

        venueId = ""
        name = ""
        photoUri = ""
        photoPrefix = ""
        photoSufix = ""

        venueId = venue['id']
        name = venue['name']
        firstPhoto = self.getFistrVenuePhotoInfo(venueId=venueId)

        if firstPhoto is not None:
            photoUri = "%s%sx%s%s" % (firstPhoto['prefix'], self.photo_width, self.photo_heigth, firstPhoto['suffix'])
            photoPrefix = firstPhoto['prefix']
            photoSufix = firstPhoto['suffix']

        address = ""
        full_address = venue['location']['formattedAddress']
        for addres_part in full_address:
            address += addres_part + " "

        latitude = venue['location']['lat']
        longitude = venue['location']['lng']

        restaurant = Restaurant(name=name, address=address, photo=photoUri, photoPrefix=photoPrefix,
                                photoSufix=photoSufix, latitude=latitude, longitude=longitude)
        return restaurant

    def findARestaurantsByLocation(self, mealType, latitude, longitude, limit):
        """ Encuentra un restaurant por la coordenadas geográficas"""
        venues = self.getVenues(mealType=mealType, lat=latitude, lng=longitude, limit=limit)

        restaurants = []

        for venue in venues:
            restaurant = self.completeRestaurantInfo(venue)
            if restaurant is not None:
                restaurants.append(restaurant)

        return restaurants

    def findARestaurantsByAddress(self, mealType, address, limit):
        """ Encuentra un re """
        geocoding = GoogleClient()
        location = geocoding.getLocationFromAddress(address=address)
        if location is None:
            return None

        lat = location[0]
        lng = location[1]
        restaurants = self.findARestaurantsByLocation(mealType, lat, lng, limit)
        return restaurants

    """Cliente de foursquare"""

    def __init__(self):
        # Lee el archivo de configuracion para el clientid y el clientsecret
        config = json.loads(open('config.json', 'r').read())
        self.apiClientId = config['Foursquare']['client_id']
        self.apiClientSecret = config['Foursquare']['client_secret']
