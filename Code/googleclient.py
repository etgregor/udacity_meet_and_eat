'''
 - Geocodifica direcciones con la api de google
 - @etgregor
 - Marzo, 2016
'''
import httplib2
import json

class GoogleClient(object):
	"""Ciente de google"""
	apikey  = ''

	def getGeocodeLocation(self, searchaddress):
		""" Geocodifica una direccion """

		apikey_param = ''
		if self.apikey is not '':
			apikey_param = '&key=%s' % self.apikey

		searchaddress = searchaddress.replace(" ", "+")
		url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s%s'% (searchaddress, apikey_param))
		h = httplib2.Http()
		response,content = h.request(url, "GET")
		result = json.loads(content)
		return result 
 

	def getLocationFromAddress(self, address):
		"""Obtiene las coordenadas de una direccion"""
		result = self.getGeocodeLocation(address)
		#print result
		location = None
		if result['results'][0] is not None:
			latitude = result['results'][0]['geometry']['location']['lat']
			longitude = result['results'][0]['geometry']['location']['lng']
			location = (latitude, longitude)
		return (latitude, longitude)


	def __init__(self):
		#Lee el archivo config.json para obtener el apikey de google
		config  = json.loads(open('config.json', 'r').read())
		apikey = config['Google']['GeocodeKey']