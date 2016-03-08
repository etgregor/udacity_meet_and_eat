#import sys
#sys.path.insert(0, '../Code')

from googleclient import GoogleClient

geocoding = GoogleClient()
location = geocoding.getLocationFromAddress(address='Colonia Obrera, Mexico City, CP.06800')
print location