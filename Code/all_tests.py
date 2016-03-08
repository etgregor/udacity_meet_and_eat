# coding=utf-8
from googleclient import GoogleClient
from foursquareclient import FoursquareClient

#TEST 1 Geocodificar dirección con google
try:
	geocoding = GoogleClient()
	searchAddress = 'Colonia Obrera, Mexico City, CP.06800'
	location = geocoding.getLocationFromAddress(address=searchAddress)
	if location is None:
		raise Exception('Direcció no encontrada: %s' % searchAddress)
	print location
except Exception as err:
	print "Test 1 FAILED: No se puede geocodificar la dirección"
	print err.args
else:
	print "Test 1 PASS: Geocodificacion exitosa"


#TEST 2 Encontrar lugar en foursaquare
try:
	forsquare = FoursquareClient()
	venue =  forsquare.findAVenue(mealType='Pizza', address='Mexico City')
	if location is None:
		raise Exception('Direcció no encontrada: %s' % searchAddress)
	print venue
except Exception as err:
	print "Test 2 FAILED: No se pudo encontrar el lugar"
	print err.args
else:
	print "Test 2 PASS: Lugar encontrado"