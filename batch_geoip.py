import geoip2.database
import sys

mmdb_path = r'c:/Users/HomePC/Downloads/GeoLite2-City_20260403/GeoLite2-City_20260403/GeoLite2-City.mmdb'
ips_file = sys.argv[1] if len(sys.argv) > 1 else 'ip_list.txt'
output_file = sys.argv[2] if len(sys.argv) > 2 else 'geoip_results.csv'

with open(ips_file) as f:
    ips = [line.strip() for line in f if line.strip()]

with geoip2.database.Reader(mmdb_path) as reader, open(output_file, 'w', encoding='utf-8') as out:
    out.write('ip,country_iso,country_name,city,latitude,longitude\n')
    for ip in ips:
        try:
            response = reader.city(ip)
            out.write(f'{ip},{response.country.iso_code},{response.country.name},{response.city.name},{response.location.latitude},{response.location.longitude}\n')
        except Exception as e:
            out.write(f'{ip},ERROR,ERROR,ERROR,ERROR,ERROR\n')
