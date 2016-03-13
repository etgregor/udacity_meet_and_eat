# coding=utf-8
import json
from googleclient import GoogleClient
from foursquareclient import FoursquareClient

# #TEST 1 Geocodificar dirección con google
# try:
# 	geocoding = GoogleClient()
# 	searchAddress = 'Colonia Obrera, Mexico City, CP.06800'
# 	location = geocoding.getLocationFromAddress(address=searchAddress)
# 	if location is None:
# 		raise Exception('Direcció no encontrada: %s' % searchAddress)
# 	print location

# 	forsquare = FoursquareClient()
# 	venues =  forsquare.findARestaurantsByLocation('Pizza', location[0], location[1], 3)
# 	if venues is None:
# 		raise Exception('Lugar no encontrado: %s' % searchAddress)
# 	print 'lugares encontrados: %s' % (len(venues)) 
# except Exception as err:
# 	print "Test 1 FAILED: No se puede geocodificar la dirección"
# 	print err.args
# else:
# 	print "Test 1 PASS: Geocodificacion exitosa"


#TEST 2 Encontrar lugar en foursaquare
try:
	forsquare = FoursquareClient()
	venues =  forsquare.findARestaurantsByAddress(mealType='Pizza', address='Mexico City', limit = 2)
	if venues is None:
		raise Exception('Lugar no encontrado: %s' % searchAddress)
	#print json.dumps(venues, default=lambda o: o.__dict__, sort_keys=True, indent=4)
	print 'lugares encontrados: %s' % (len(venues)) 
except Exception as err:
	print "Test 2 FAILED: No se pudo encontrar el lugar"
	print err.args
else:
	print "Test 2 PASS: Lugar encontrado"