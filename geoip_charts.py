import sys
import geoip2.database
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

geoip_db = sys.argv[1]
ip_file = sys.argv[2]
heatmap_file = sys.argv[3]
barchart_file = sys.argv[4]

ips = [line.strip() for line in open(ip_file)]
reader = geoip2.database.Reader(geoip_db)
cities = []
countries = []
for ip in ips:
    try:
        resp = reader.city(ip)
        cities.append(resp.city.name or "Unknown")
        countries.append(resp.country.name or "Unknown")
    except:
        cities.append("Unknown")
        countries.append("Unknown")
reader.close()

# Bar chart: Top countries
country_counts = Counter(countries)
df = pd.DataFrame(country_counts.items(), columns=["Country", "Hits"])
df = df.sort_values("Hits", ascending=False)
df.plot.bar(x="Country", y="Hits", legend=False)
plt.title("Top Target Countries")
plt.tight_layout()
plt.savefig(barchart_file)
plt.close()

# Heatmap: (for simplicity, just a pie chart of countries)
df.plot.pie(y="Hits", labels=df["Country"], autopct='%1.1f%%')
plt.title("Hit Distribution by Country")
plt.ylabel("")
plt.tight_layout()
plt.savefig(heatmap_file)
plt.close()
