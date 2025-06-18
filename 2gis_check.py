from opencage.geocoder import OpenCageGeocode

key = 'c1b748380829472da6641626bba0c129'
geocoder = OpenCageGeocode(key)

query = 'город Томск, ленина 26'
results = geocoder.geocode(query)

if results:
    latitude = results[0]['geometry']['lat']
    longitude = results[0]['geometry']['lng']
    print(f"Координаты: {latitude}, {longitude}")
else:
    print("Адрес не найден.")
