import csv
from jinja2 import Template
import os

# Paths
TEMPLATE_PATH = 'wave3_lure_template.html'
TARGETS_CSV = 'Wave_3_Targets.csv'  # Columns: email,deviceId,phishUrl
OUTPUT_DIR = 'lure_variants'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load HTML template
with open(TEMPLATE_PATH, encoding='utf-8') as f:
    template_str = f.read()

# Jinja2 template (replace $deviceId and $phishUrl)
template = Template(template_str.replace('$($deviceId)', '{{ deviceId }}').replace('$phishUrl', '{{ phishUrl }}'))

# Read targets and generate variants
with open(TARGETS_CSV, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        deviceId = row['deviceId']
        phishUrl = row['phishUrl']
        email = row.get('email', deviceId)
        html = template.render(deviceId=deviceId, phishUrl=phishUrl)
        out_path = os.path.join(OUTPUT_DIR, f'lure_{deviceId}.html')
        with open(out_path, 'w', encoding='utf-8') as outf:
            outf.write(html)
        print(f'Generated: {out_path}')

print('All lure variants generated in', OUTPUT_DIR)
