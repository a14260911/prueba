import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin

edgerc = EdgeRc('.edgerc')
section = 'default'
baseurl = 'https://%s' % edgerc.get(section, 'host')

s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
todojson = {}
result = s.get(urljoin(baseurl, '/invoicing-api/v2/contracts/1-ADEJG/invoices/21335000202/files/Akamai_21335000202_1.json'))
if result.status_code == 200:
	todo = result.json()
	#Cabeceras	
	print ("END_CUSTOMER_ACCOUNT_NAME;END_CUSTOMER_ACCOUNT_ID;PRODUCT_ID;PRODUCT;EFFECTIVE_END_DATE")

	for valor in todo['INVOICE']['END_CUSTOMER']:
#		print (valor['END_CUSTOMER_ACCOUNT_NAME']+" --- "+valor['END_CUSTOMER_ACCOUNT_ID'])
		for elemento in valor['INVOICE_LINE']:
#			print (elemento,"\n")			
			print (valor['END_CUSTOMER_ACCOUNT_NAME']+";"+valor['END_CUSTOMER_ACCOUNT_ID']+";"+ elemento['PRODUCT_ID']+";"+ elemento['PRODUCT']+";"+ elemento['EFFECTIVE_END_DATE'])
	print ("\n")
else:
	print ("Error: ", result.status_code)

