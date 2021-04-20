"""
/*Obtener facturas*/ 

http --json --body --auth-type edgegrid -a default: ":/invoicing-api/v2/contracts/1-ADEJG/invoices?month=4&year=2021" 
http --json --body --auth-type edgegrid -a default: ":/invoicing-api/v2/contracts/1-ADEJG/invoices/21335000202/files" 
http --json --body --auth-type edgegrid -a default: ":/invoicing-api/v2/contracts/1-ADEJG/invoices/21335000202/files/Akamai_21335000202_1.json" 

"""

import requests, sys, os
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin
from datetime import date
from datetime import datetime
# Para el envio de correos
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.encoders import encode_base64
import smtplib

def enviarCorreo(FicheroA, FicheroB, FicheroC):
    try:
        msg = MIMEMultipart()
        # cabeceras del correo
        msg['From'] = "no_answer@telefonica.com"
        destinatarios = ["ctnt.akamai@telefonica.com", "hugo.gonzalezbengoa@telefonica.com", "victor.castillorubio@telefonica.com"]
        msg['To'] = ", ".join(destinatarios)
        msg['Subject'] = "[RUTINA] End Dates"
        body="<html><body><p>&nbsp&nbsp&nbspVencimiento de productos.<BR><BR>"
        body=body+"<BR><BR>Saludos<BR>CT AKAMAI\n</p>\n</body>\n</html>"
        msg.attach(MIMEText(body, 'html'))

        #Adjuntar archivo pasado como argumento
        if (os.path.isfile(FicheroA)):
            adjunto = MIMEBase('application', 'octet-stream')
            adjunto.set_payload(open(FicheroA, "rb").read())
            encode_base64(adjunto)
            adjunto.add_header ('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(FicheroA))
            msg.attach(adjunto)
        if (os.path.isfile(FicheroB)):
            adjunto = MIMEBase('application', 'octet-stream')
            adjunto.set_payload(open(FicheroB, "rb").read())
            encode_base64(adjunto)
            adjunto.add_header ('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(FicheroB))
            msg.attach(adjunto)
        if (os.path.isfile(FicheroC)):
            adjunto = MIMEBase('application', 'octet-stream')
            adjunto.set_payload(open(FicheroC, "rb").read())
            encode_base64(adjunto)
            adjunto.add_header ('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(FicheroC))
            msg.attach(adjunto)
            
        # Conexion al servidor de correo saliente
        server = smtplib.SMTP('10.51.90.26',25)
        server.sendmail(msg['From'], destinatarios, msg.as_string())
        server.quit()
        print("Correo enviado a: "+msg['To']+"\n")  
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


try:
    edgerc = EdgeRc('.edgerc')
    section = 'default'
    baseurl = 'https://%s' % edgerc.get(section, 'host')

    today = date.today()
    tt = today.timetuple()
    hoy = datetime.now()
    mes = '{:02d}'.format(tt.tm_mon)
    dia = '{:02d}'.format(tt.tm_mday)
    yyear = '{:04d}'.format(tt.tm_year)

    FicheroCSV = "EndDates"+str(yyear)+str(mes)+str(dia)+".csv"
    FicheroCSV30 = "EndDates"+str(yyear)+str(mes)+str(dia)+"_30.csv"
    FicheroCSV60 = "EndDates"+str(yyear)+str(mes)+str(dia)+"_60.csv"
    fechahoy = date(int(yyear), int(mes), int(dia))

    s = requests.Session()
    s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
    todojson = {}
    result = s.get(urljoin(baseurl, '/invoicing-api/v2/contracts/1-ADEJG/invoices/21335000202/files/Akamai_21335000202_1.json'))
    if result.status_code == 200:
        todo = result.json()
        #Cabeceras  
        strcsv="END_CUSTOMER_ACCOUNT_NAME;END_CUSTOMER_ACCOUNT_ID;PRODUCT_ID;PRODUCT;EFFECTIVE_END_DATE;DAYS_TO_END\n"
        strcsv30="END_CUSTOMER_ACCOUNT_NAME;END_CUSTOMER_ACCOUNT_ID;PRODUCT_ID;PRODUCT;EFFECTIVE_END_DATE;DAYS_TO_END\n"
        strcsv60="END_CUSTOMER_ACCOUNT_NAME;END_CUSTOMER_ACCOUNT_ID;PRODUCT_ID;PRODUCT;EFFECTIVE_END_DATE;DAYS_TO_END\n"
        for valor in todo['INVOICE']['END_CUSTOMER']:
            for elemento in valor['INVOICE_LINE']:
                #Calculo de dias hasta EFFECTIVE_END_DATE   
                fecha2 = datetime.strptime(elemento['EFFECTIVE_END_DATE'], '%Y-%m-%d').date()
                dias = fecha2 - fechahoy
                line = valor['END_CUSTOMER_ACCOUNT_NAME']+";"+valor['END_CUSTOMER_ACCOUNT_ID']+";"+\
                    elemento['PRODUCT_ID']+";"+\
                    elemento['PRODUCT']+";"+\
                    elemento['EFFECTIVE_END_DATE']+";"+\
                    str(dias.days)+"\n"
#               print (line)
                caducado = int(str(dias.days))
#                print (caducado, dias.days, str(dias.days))

                if ( caducado >= 60):
                    strcsv60+=line
                else:
                    if (caducado >= 30):
                        strcsv30+=line
                strcsv+=line

        print (strcsv)
        
        fCSV = open (FicheroCSV, "w")
        fCSV30 = open (FicheroCSV30, "w")
        fCSV60 = open (FicheroCSV60, "w")
        
        fCSV30.write(strcsv30)
        fCSV60.write(strcsv60)
        fCSV.write(strcsv)

        fCSV.close()
        fCSV30.close()
        fCSV60.close()
        
        print ("Generado fichero ", FicheroCSV, "\n")
        print ("Generado fichero ", FicheroCSV30, "\n")
        print ("Generado fichero ", FicheroCSV60, "\n")
        
        enviarCorreo(FicheroCSV, FicheroCSV30, FicheroCSV60)
    else:
        print ("Error API: ", result.status_code)

except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

    