#! usr/bin/env python3
import requests

PATH = "C:\Bard\KRAKEN\AssetPairs"
PAIRS = []

resp = requests.get('https://api.kraken.com/0/public/AssetPairs')
JsonResp = resp.json()

assets = JsonResp['result']

for a in assets:
	base = assets[a]['base']
	quote = assets[a]['quote']
	pair = base + quote
	order_min = assets[a]['ordermin']
	PAIRSTRING = pair + " = { " + "'base':" + "'" + base + "'" + ", " + "'quote':" + "'" + quote + "'" + ", " + "'order_min':" + "'" + order_min + "'" + ", " + "'pair':" + "'" + pair + "'" +  " } "
	if "1" not in pair and "." not in pair:
		PAIRS.append(PAIRSTRING + '\n')

fin = open("AssetPairs", "w")
fin.writelines(PAIRS)
fin.close()
exit(0)
