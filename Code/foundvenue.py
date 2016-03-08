class FundVenue(object):
	""" Lugar encontrado """
	Name = ''
	Address = ''
	Photo = ''
	NearvyLatLon = ''

	def __init__(self, name, address, photo, nearvylatlon):
		self.Name = name
		self.Address = address
		self.Photo = photo
		self.NearvyLatLon = nearvylatlon