import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

edgerc = EdgeRc('.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

result = s.get(urljoin(baseurl, '/diagnostic-tools/v2/ghost-locations/available'))
if result.status_code == 200:
	for valor in result.json()['locations']:
		print (valor['id'], "---->", valor['value'])
else:
	print ("Error: ", result.status_code)
