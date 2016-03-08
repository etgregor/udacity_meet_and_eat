class FundVenue(object):
	""" Lugar encontrado """
	Name = ''
	Address = ''
	Photo = ''
	PhotoPrefix = ''
	PhotoSufix = ''
	Latitude = 0
	Longitude = 0

	def __init__(self, name, address, photo, photoPrefix, photoSufix, latitude, longitude):
		self.Name = name
		self.Address = address
		self.Photo = photo
		self.PhotoPrefix = photoPrefix
		self.PhotoSufix = photoSufix
		self.Latitude = latitude
		self.Longitude = longitude