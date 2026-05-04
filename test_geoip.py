import geoip2.database

mmdb_path = r'c:/Users/HomePC/Downloads/GeoLite2-City_20260403/GeoLite2-City_20260403/GeoLite2-City.mmdb'

with geoip2.database.Reader(mmdb_path) as reader:
    ip = '128.101.101.101'  # You can change this to any IP you want to look up
    response = reader.city(ip)
    print('Country ISO code:', response.country.iso_code)
    print('Country name:', response.country.name)
    print('City name:', response.city.name)
    print('Latitude:', response.location.latitude)
    print('Longitude:', response.location.longitude)
