import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin
import json
import datetime, time, os, sys
# Para el envio de correos
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.encoders import encode_base64
import smtplib

# Esta funcion manda un correo con los registros de año en curso

#def enviarCorreo(Registros, FicheroA, FicheroB, FicheroC):
def enviarCorreo(FicheroA):
    msg = MIMEMultipart()
    # cabeceras del correo
    msg['From'] = "no_answer@telefonica.com"
    destinatarios = ["ctnt.akamai@telefonica.com", "hugo.gonzalezbengoa@telefonica.com", "victor.castillorubio@telefonica.com"]
    msg['To'] = ", ".join(destinatarios)
    msg['Subject'] = "[RUTINA] Contract list"
    body="<html><body><p>&nbsp&nbsp&nbspLista de contratos.<BR><BR>"
    body=body+"<BR><BR>Saludos<BR>CT AKAMAI\n</p>\n</body>\n</html>"
    msg.attach(MIMEText(body, 'html'))

    #Adjuntar archivo pasado como argumento
    if (os.path.isfile(FicheroA)):
        adjunto = MIMEBase('application', 'octet-stream')
        adjunto.set_payload(open(FicheroA, "rb").read())
        encode_base64(adjunto)
        adjunto.add_header ('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(FicheroA))
        msg.attach(adjunto)
    # Conexion al servidor de correo saliente
    server = smtplib.SMTP('10.51.90.26',25)
    server.sendmail(msg['From'], destinatarios, msg.as_string())
    server.quit()
    print("Correo enviado a: "+msg['To'])  

try:
	today = datetime.date.today()
	tt = today.timetuple()
	hora = '{:02d}'.format(tt.tm_hour)
	minutos = '{:02d}'.format(tt.tm_min)
	mes = '{:02d}'.format(tt.tm_mon)
	dia = '{:02d}'.format(tt.tm_mday)
	yyear = '{:04d}'.format(tt.tm_year)
	#mes = "12"
	#dia = "18"
	#yyear = "2020"
	fechafichero = str(yyear)+str(mes)+str(dia)
	Fichero = "Contract-list-"+fechafichero+".txt"
#	print (fechafichero+"\n"+Fichero)
	strtxt = ""

	edgerc = EdgeRc('.edgerc')
	section = 'default'
	baseurl = 'https://%s' % edgerc.get(section, 'host')

	s = requests.Session()
	s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

	#result = s.get(urljoin(baseurl, '/diagnostic-tools/v2/ghost-locations/available'))
	result = s.get(urljoin(baseurl, 'identity-management/v1/open-identities/pscuj7x7af3dsgwq/account-switch-keys'))
	if result.status_code == 200:
		todo = result.json()
#		print  (type(todo), todo, "\n\n")
#		print ("accountSwitchKey;accountName;contractID")
		for valor in todo:
			result2 = s.get(urljoin(baseurl, '/contract-api/v1/contracts/identifiers?accountSwitchKey='+str(valor['accountSwitchKey'])))
			if result2.status_code == 200:
				todo2 = result2.json()
				for contrato in todo2:
					print (contrato+","+valor['accountName'])
					strtxt+=str(contrato+","+valor['accountName']+"\n")
				#Contract IDs como una cadena separada por ;
#				Strtodo2 = ";".join(todo2)
#				print (valor['accountName'], ",", Strtodo2)
#				print (valor['accountSwitchKey'], ";", valor['accountName'], ";", Strtodo2)
#				print (type(valor), valor['id'], valor['value'])
#				print (i, "\t", result.json()['locations'][i]['value'])
			else:
				print ("Error en: /contract-api/v1/contracts/identifiers?accountSwitchKey='+str(valor['accountSwitchKey'])\n")
	else:
		print ("Error: ", result.status_code)
	
	fTxt = open (Fichero, "w")
	fTxt.write(strtxt)
	fTxt.close()
	print ("Creado fichero "+Fichero+"\n")
	enviarCorreo(Fichero)
except:
	print("Error inesperado:", sys.exc_info()[0])
	raise
