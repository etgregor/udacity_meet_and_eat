# coding=utf-8
from urllib import urlencode
from httplib2 import Http
import json
import sys
import base64

from googleclient import GoogleClient
from foursquareclient import FoursquareClient


print "Corriendo Endpoint Tester....\n"
#address = raw_input("Ingrese la url para realizar las pruebas, \n si no capruta una url las pruebas se realizaran sobre 'http://localhost:5000':   ")
#if address == '':
address = 'http://localhost:5000'

admin_user = 'admin@gmail.com'
admin_pwd = '1234'
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


# #TEST 2 Encontrar lugar en foursaquare
# try:
# 	forsquare = FoursquareClient()
# 	venues =  forsquare.findARestaurantsByAddress(mealType='Pizza', address='Mexico City', limit = 2)
# 	if venues is None:
# 		raise Exception('Lugar no encontrado: %s' % venues)
# 	#print json.dumps(venues, default=lambda o: o.__dict__, sort_keys=True, indent=4)
# 	print 'lugares encontrados: %s' % (len(venues))
# except Exception as err:
# 	print "Test 2 FAILED: No se pudo encontrar el lugar"
# 	print err.args
# else:
# 	print "Test 2 PASS: Lugar encontrado"


# #TEST 3 agregando nuevo usuario
# try:

# 	url = address + '/api/v1/users'
# 	h = Http()
# 	# agregar credenciales cuando ya existe un usuario
# 	#h.add_credentials('gregoriomarciano@gmail.com', '1234')
# 	data = dict(email = admin_user, password = admin_pwd, name = "Gregor admin", picture = "https://pbs.twimg.com/profile_images/1198085304/avatar_GMA_400x400.png")
# 	data = json.dumps(data)
# 	resp, content = h.request(url,'POST', body = data, headers = {"Content-Type": "application/json"})
# 	if resp['status'] != '201' and resp['status'] != '200':
# 		raise Exception('Se recibio un codigo de error %s' % resp['status'])

# except Exception as err:
# 	print "Test 3 FAIL: No se puede crear un nuevo usuario"
# 	print err.args
# 	sys.exit()
# else:
# 	print "Test 3 PASS: Usuario creado"


# #TEST 4: Obteniendo token de acceso
# try:

# 	url = address + '/token'
# 	h = Http()
# 	h.add_credentials(admin_user, admin_pwd)
# 	resp, content = h.request(url,'GET')
# 	if resp['status'] != '200':
# 		raise Exception('Se recibio un codigo de error %s' % resp['status'])
# except Exception as err:
# 	print "Test 4 FAIL: No se pudo obtener el token"
# 	print err.args
# 	sys.exit()
# else:
# 	print "Test 4 PASS: Obtener Token"


# #TEST 5: Obteniendo perfil
# try:

# 	url = address + '/api/v1/me'
# 	h = Http()
# 	h.add_credentials(admin_user, admin_pwd)
# 	resp, content = h.request(url,'GET')
# 	if resp['status'] != '200':
# 		raise Exception('Se recibio un codigo de error %s' % resp['status'])
# except Exception as err:
# 	print "Test 5 FAIL: No se pudo obtener el perfil"
# 	print err.args
# 	sys.exit()
# else:
# 	print "Test 5 PASS: Perfil de usuario autenticado ok"


# #TEST 6: Todos los usuarios
# try:

# 	url = address + '/api/v1/users'
# 	h = Http()
# 	h.add_credentials(admin_user, admin_pwd)
# 	resp, content = h.request(url,'GET')
# 	if resp['status'] != '200':
# 		raise Exception('Se recibio un codigo de error %s' % resp['status'])
# except Exception as err:
# 	print "Test 6 FAIL: No se pudo obtener el listado de usuarios"
# 	print err.args
# 	sys.exit()
# else:
# 	print "Test 6 PASS: Listado de usuarios"


# #TEST 7: Todos los usuarios
# try:

# 	url = address + '/api/v1/users/' + admin_user
# 	h = Http()
# 	h.add_credentials(admin_user, admin_pwd)
# 	resp, content = h.request(url,'GET')
# 	if resp['status'] != '200':
# 		raise Exception('Se recibio un codigo de error %s' % resp['status'])
# except Exception as err:
# 	print "Test 7 FAIL: No se pudo obtener un usuario por su correo"
# 	print err.args
# 	sys.exit()
# else:
# 	print "Test 7 PASS: Obtener usuario"

# #TEST 8: Actualizando perfil
# try:

# 	url = address + '/api/v1/me'
# 	h = Http()
	
# 	h.add_credentials(admin_user, admin_pwd)
# 	data = dict(name = "Gregor admin reloaded", picture = "https://pbs.twimg.com/profile_images/1198085304/avatar_GMA_400x400.png")
# 	data = json.dumps(data)
# 	resp, content = h.request(url,'PUT', body = data, headers = {"Content-Type": "application/json"})
# 	if resp['status'] != '201' and resp['status'] != '200':
# 		raise Exception('Se recibio un codigo de error %s' % resp['status'])
# except Exception as err:
# 	print "Test 8 FAIL: No se pudo actualizar el perfil"
# 	print err.args
# 	sys.exit()
# else:
# 	print "Test 8 PASS: Perfil de usuario actualizado"


#TEST 9: Borrando usuario
try:

	url = address + '/api/v1/users'
	h = Http()
	
	h.add_credentials(admin_user, admin_pwd)
	data = dict(email = "userd@gmail.com", password = "1234", name = "Gregor admin", picture = "https://pbs.twimg.com/profile_images/1198085304/avatar_GMA_400x400.png")
	data = json.dumps(data)
	resp, content = h.request(url,'POST', body = data, headers = {"Content-Type": "application/json"})
	if resp['status'] != '201' and resp['status'] != '200':
		raise Exception('Se recibio un codigo de error al crear usuario para luego borrarlo %s' % resp['status'])

	url = address + '/api/v1/users'
	h = Http()
	h.add_credentials(admin_user, admin_pwd)
	data = dict(email = "userd@gmail.com")
	data = json.dumps(data)
	resp, content = h.request(url,'DELETE', body = data, headers = {"Content-Type": "application/json"})
	if resp['status'] != '201' and resp['status'] != '200':
		raise Exception('Se recibio un codigo de error %s' % resp['status'])
except Exception as err:
	print "Test 9 FAIL: No se puede eliminar al usuario"
	print err.args
	sys.exit()
else:
	print "Test 9 PASS: Usuario eliminado"

