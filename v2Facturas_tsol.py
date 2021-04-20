#
# Programa para generar un informe sobre los costes mensuales de akamai asociados a las subactividades de TSOL
#
# Realizado por Alberto Jose Sanchez Cezon el 23 de Octubre de 2020
#

# Constantes y diferentes parametros que definiran las busquedas que vamos a usar.

servicios=[55,390]
tipos_fijos=['P','F','A','S']
tipos_variables=['B','U']
tipos=[tipos_fijos,tipos_variables]
origen="1875070"
naturaleza="TROE"

#Consultas SQL
sql={}
sql['55']=""
sql['390']=""
sql['P']=""
sql['CLIENTES']="""SELECT A.NIF,B.C_CLI FROM 
(SELECT DISTINCT NIF,ID_CTA FROM akamaifac.t12_CLI_NIF) A,
akamaifac.t01_IDCTA_CLI B 
WHERE 
A.ID_CTA=B.ID_CTA;"""
sql['SA']="""SELECT DISTINCT A.NIF,A.ID_SERVICIO AS SERVICIO,CASE WHEN C.ID_CFV IS NOT NULL THEN TRUE ELSE FALSE END AS VARIABLE,A.CODIGO_ACTIVIDAD AS SUBACTIVIDAD,B.CODIGO_ACTIVIDAD AS ACTIVIDAD_PRINCIPAL,A.NOMBRE_LARGO  
FROM 
akamaifac.t13_NIF_AP_SA A 
LEFT OUTER JOIN akamaifac.t13_NIF_AP_SA B ON A.ACTIVIDAD_PRINCIPAL=B.SUBACTIVIDAD 
LEFT OUTER JOIN akamaifac.t15_AP_SA_CFV C ON A.SUBACTIVIDAD=C.SUBACTIVIDAD 
WHERE 
A.CODIGO_ACTIVIDAD<>B.CODIGO_ACTIVIDAD AND A.NIF=\'"""
sql['COSTES']="""SELECT SUM(B.TOTAL_SIN_IMPUESTOS) 
FROM 
akamaifac.t12_CLI_NIF A,
akamaifac.t18_PROD_FACT B,
akamaifac.t17_TIPO_PRODUCTO C  
WHERE 
A.ID_CTA=B.ID_CTA AND C.ID_PRO=B.ID_PRO AND B.ID_PRO NOT IN (SELECT DISTINCT ID_PRO FROM akamaifac.t19_PRODS_50PC) AND """
sql['COSTES_50PC']="""SELECT SUM(B.TOTAL_SIN_IMPUESTOS) 
FROM 
akamaifac.t12_CLI_NIF A,
akamaifac.t18_PROD_FACT B,
akamaifac.t17_TIPO_PRODUCTO C  
WHERE 
A.ID_CTA=B.ID_CTA AND C.ID_PRO=B.ID_PRO AND B.ID_PRO IN (SELECT DISTINCT ID_PRO FROM akamaifac.t19_PRODS_50PC) AND """
sql['FECHAFIN_PTTI']="""SELECT PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_CODIGO, 
PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_CODIGO_AP, 
PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_FECHA_INICIO,
PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_FECHA_FIN,
PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_CLIENTE_FUNC_DES,
PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_NOMBRE,
PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_ANYO, 
PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_MES
FROM 
PTTI.V_TSOL_ACT_INDICADORES_GESTION 
WHERE  """
#PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_CODIGO = 4217609 AND PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_ANYO = 2021 AND PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_MES = 3"""

import BDsCNCE as bd
import utils
from datetime import datetime,timedelta,date
import pandas
import sys

# Funcion para dejar un log del inicio

def inicio():
    print("INICIO")
    print(datetime.now())

# Funcion para dejar un log si todo ha ido bien

def despedida():
    print("CORRECTO")
    print(datetime.now())

# Funcion que extrae todos los clientes que tratamos

def ListadoClientes(BD):
    BD.consultar(sql['CLIENTES'])
    fila=BD.leerLinea()
    clientes={}
    while fila!=False:
        clientes[fila[0]]={}
        clientes[fila[0]]["NOMBRE"]=fila[1]
        fila=BD.leerLinea()
    return clientes

# Funcion que extrae las SAs de un cliente concreto

def SAsxCliente(BD,cliente):
    BD.consultar(sql['SA']+cliente+"';")
#    print ("Dentro de SAsxCliente", cliente, '\n')
    fila=BD.leerLinea()
#    print (fila)
    SAs={}
    while fila!=False:
        if fila[1] not in SAs:
            SAs[fila[1]]={}
        if fila[2] not in SAs[fila[1]]:
            SAs[fila[1]][fila[2]]={}
        if fila[3] not in SAs[fila[1]][fila[2]]:
            SAs[fila[1]][fila[2]][fila[3]]={}
        SAs[fila[1]][fila[2]][fila[3]]['SUBACTIVIDAD']=fila[3]
        SAs[fila[1]][fila[2]][fila[3]]['ACTIVIDAD_PRINCIPAL']=fila[4]
        SAs[fila[1]][fila[2]][fila[3]]['NOMBRE']=fila[5]
        fila=BD.leerLinea()
#       print (fila)
    return SAs

# Funcion que extrae los costes de Akamai de una subactividad

def CostesAkamai(BD,cliente,tipo,servicio,anio="",mes=""):
    if mes=="":
        mes="MONTH(NOW())"
    if anio=="":
        anio="YEAR(NOW())"
    BD.consultar(sql['COSTES']+"A.NIF='"+str(cliente)+"' AND C.TIPO='"+str(servicio)+"' AND B.TIPO='"+str(tipo)+"' AND B.FECHA_FACT LIKE CONCAT("+str(anio)+",CONCAT('-',CONCAT("+str(mes)+",'-%'))) GROUP BY B.ID_CTA;")
    fila=BD.leerLinea()
    if fila==False:
        return 0
    else:
        return(fila[0])

# Funcion que extrae los costes de los productos que hay que repartir los costes al 50%

def Costes50pcAkamai(BD,cliente,tipo,servicio,anio="",mes=""):
    if mes=="":
        mes="MONTH(NOW())"
    if anio=="":
        anio="YEAR(NOW())"    
    BD.consultar(sql['COSTES_50PC']+"A.NIF='"+str(cliente)+"' AND C.TIPO='"+str(servicio)+"' AND B.TIPO='"+str(tipo)+"' AND B.FECHA_FACT LIKE CONCAT("+str(anio)+",CONCAT('-',CONCAT("+str(mes)+",'-%'))) GROUP BY B.ID_CTA;")
    fila=BD.leerLinea()
    if fila==False:
        return 0
    else:
        return(fila[0])
    
# Esta funcion genera un excel a partir de un array dado

def GenerarExcel(array_datos,mes,anio,nombre="",columnas=""):
    if columnas=="":
        df=pandas.DataFrame(array_datos)
    else:
        df=pandas.DataFrame(array_datos,columns=columnas)
    if nombre!="":
        archivo=nombre+"_"+str(datetime.now().day)+"_"+str(datetime.now().month)+"_"+str(datetime.now().year)
    else:
        archivo="excel"+"_"+str(datetime.now().day)+"_"+str(datetime.now().month)+"_"+str(datetime.now().year)
    if mes!="MONTH(NOW())":
        archivo=archivo+"-"+str(mes)
    if anio!="YEAR(NOW())":
        archivo=archivo+"-"+str(anio)
#    writer=pandas.ExcelWriter('/data/'+archivo.replace("'",'')+'.xlsx')
    writer=pandas.ExcelWriter('/data/v'+archivo.replace("'",'')+'.xlsx')
    df.to_excel(writer, 'Hoja de datos', index=False)
    writer.save()

#def FechaFinPTTI(Anyo, AP):
def FechaFinPTTI(CODIGO_ACTIVIDAD, mmes, yyear):
    bdPTTI=bd.basedatos("EXADATA")
    print ("Dentro de FechaFinPTTI, buscando: ", CODIGO_ACTIVIDAD, mmes, yyear, "\n")
    bdPTTI.consultar(sql['FECHAFIN_PTTI'] + "PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_CODIGO = " + str (CODIGO_ACTIVIDAD) + " AND PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_ANYO = " + str(yyear) + " AND PTTI.V_TSOL_ACT_INDICADORES_GESTION.TSOL_ACT_GES_MES = " + str(mmes))
    fila=bdPTTI.leerLinea()
    if fila != False:
        print ("Dentro de FechaFinPTTI, valor de fila: --->>>", fila, "\n")
        print ("Dentro de FechaFinPTTI, valor fila[3]: --->>>", fila[3], type(fila[3]), "\n")
    print ("\n")

    return False

"""    
    i = 0
    while fila!=False:
        fila=bdPTTI.leerLinea()
        print (fila)
        i = i + 1
        print ("\n\n")
        print ("Dentro de FechaFinPTTI, valor de fila: --->>>", fila, "\n\n")
        
    print ("Despues de bucle leerLinea\nRegistros: ", i)
    print ("\n\n")
"""   
    
# Funcion principal, inicio del programa

def main():
    inicio()
    # El informe puede ser del mes actual si no se indica nada o del mes y año que se indique por parametros.
    
    if len(sys.argv) <= 1:
        today = date.today()
        tt = today.timetuple()
        hoy = datetime.now()
        mes = str('{:02d}'.format(tt.tm_mon))
        dia = str('{:02d}'.format(tt.tm_mday))
        anio = str('{:04d}'.format(tt.tm_year))
#        FicheroCSV = "EndDates"+str(yyear)+str(mes)+str(dia)+".csv"
    else:
        if len(sys.argv) == 3:
            mes = str('{:02d}'.format(int(sys.argv[1])))
            dia = str('{:02d}'.format(1))
            anio = str('{:04d}'.format(int(sys.argv[2])))
#           FicheroCSV = "EndDates"+str(yyear)+str(mes)+".csv"
        else:
            print("Los parametros opcionales son 'python3 sys.argv[0] mes anio'")
            despedida()
            exit()
            
    #print ("Dia: "+dia+" Mes: "+mes+" Año: "+yyear)

    fechahoy = date(int(anio), int(mes), int(dia))

    # BD CDS
    bdCDS=bd.basedatos("CNCE")
    # Extraemos los clientes
    Clientes=ListadoClientes(bdCDS)
    lineas_excel=[]
    
    for cliente in Clientes:
        # Extraemos todas las subactividades de cada cliente
#        print ('*****', Clientes[cliente]['NOMBRE'], '******\n')
        Clientes[cliente]['SAs']=SAsxCliente(bdCDS,cliente)
#       Inicializamos valores
#       print (cliente, Clientes[cliente]['NOMBRE'], Clientes[cliente]['SAs'])
#       print (Clientes[cliente]['NOMBRE'], Clientes[cliente]['SAs'], '\n')
        
        for servicio in servicios:
            if servicio in Clientes[cliente]['SAs']:
                if 0 in Clientes[cliente]['SAs'][servicio]:
                    Clientes[cliente]['SAs'][servicio]['FIJO']=0
                if 1 in Clientes[cliente]['SAs'][servicio]:
                    Clientes[cliente]['SAs'][servicio]['VARIABLE']=0
            
        for servicio in servicios:
            # Pasamos a extraer los costes
            if servicio in Clientes[cliente]['SAs']:
                if 0 in Clientes[cliente]['SAs'][servicio]:
                    for tipo in tipos_fijos:
                        # Extraemos primero para cada cliente los costes que se reparten al 50% entre fijo y variable.
                        Costes50pc=Costes50pcAkamai(bdCDS,cliente,tipo,servicio,anio,mes)
                        if Costes50pc!=0:
                            if servicio==55:
                                if 390 in Clientes[cliente]['SAs']:
                                    if 'FIJO' in Clientes[cliente]['SAs'][390]:
                                        Clientes[cliente]['SAs'][55]['FIJO']=float(Clientes[cliente]['SAs'][55]['FIJO'])+float(Costes50pc/2)
                                        Clientes[cliente]['SAs'][390]['FIJO']=float(Clientes[cliente]['SAs'][390]['FIJO'])+float(Costes50pc/2)
                                    else:
                                        Clientes[cliente]['SAs'][55]['FIJO']=float(Clientes[cliente]['SAs'][55]['FIJO'])+float(Costes50pc)
                                else:
                                    Clientes[cliente]['SAs'][55]['FIJO']=float(Clientes[cliente]['SAs'][55]['FIJO'])+float(Costes50pc)
                            else:
                                if 55 in Clientes[cliente]['SAs']:
                                    if 'FIJO' in Clientes[cliente]['SAs'][55]:
                                        Clientes[cliente]['SAs'][55]['FIJO']=float(Clientes[cliente]['SAs'][55]['FIJO'])+float(Costes50pc/2)
                                        Clientes[cliente]['SAs'][390]['FIJO']=float(Clientes[cliente]['SAs'][390]['FIJO'])+float(Costes50pc/2)
                                    else:
                                        Clientes[cliente]['SAs'][390]['FIJO']=float(Clientes[cliente]['SAs'][390]['FIJO'])+float(Costes50pc)
                                else:
                                    Clientes[cliente]['SAs'][390]['FIJO']=float(Clientes[cliente]['SAs'][390]['FIJO'])+float(Costes50pc)
                        # Aqui los costes normales.
                        Clientes[cliente]['SAs'][servicio]['FIJO']=float(Clientes[cliente]['SAs'][servicio]['FIJO'])+float(CostesAkamai(bdCDS,cliente,tipo,servicio,anio,mes))
                if 1 in Clientes[cliente]['SAs'][servicio]:
                    for tipo in tipos_variables:
                        # Extraemos primero para cada cliente los costes que se reparten al 50% entre fijo y variable.
                        Costes50pc=Costes50pcAkamai(bdCDS,cliente,tipo,servicio,anio,mes)
                        if Costes50pc!=0:
                            if servicio==55:
                                if 390 in Clientes[cliente]['SAs']:
                                    if 'VARIABLE' in Clientes[cliente]['SAs'][390]:
                                        Clientes[cliente]['SAs'][55]['VARIABLE']=float(Clientes[cliente]['SAs'][55]['VARIABLE'])+float(Costes50pc/2)
                                        Clientes[cliente]['SAs'][390]['VARIABLE']=float(Clientes[cliente]['SAs'][390]['VARIABLE'])+float(Costes50pc/2)
                                    else:
                                        Clientes[cliente]['SAs'][55]['VARIABLE']=float(Clientes[cliente]['SAs'][55]['VARIABLE'])+float(Costes50pc)
                                else:
                                    Clientes[cliente]['SAs'][55]['VARIABLE']=float(Clientes[cliente]['SAs'][55]['VARIABLE'])+float(Costes50pc)
                            else:
                                if 55 in Clientes[cliente]['SAs']:
                                    if 'VARIABLE' in Clientes[cliente]['SAs'][55]:
                                        Clientes[cliente]['SAs'][55]['VARIABLE']=float(Clientes[cliente]['SAs'][55]['VARIABLE'])+float(Costes50pc/2)
                                        Clientes[cliente]['SAs'][390]['VARIABLE']=float(Clientes[cliente]['SAs'][390]['VARIABLE'])+float(Costes50pc/2)
                                    else:
                                        Clientes[cliente]['SAs'][390]['VARIABLE']=float(Clientes[cliente]['SAs'][390]['VARIABLE'])+float(Costes50pc)
                                else:
                                    Clientes[cliente]['SAs'][390]['VARIABLE']=float(Clientes[cliente]['SAs'][390]['VARIABLE'])+float(Costes50pc)
                        # Aqui los costes normales.
                        Clientes[cliente]['SAs'][servicio]['VARIABLE']=float(Clientes[cliente]['SAs'][servicio]['VARIABLE'])+float(CostesAkamai(bdCDS,cliente,tipo,servicio,anio,mes))
#        print (cliente, Clientes[cliente]['NOMBRE'], Clientes[cliente]['SAs'], '\n')

    # Rellenamos el excel con los datos generados.
    for cliente in Clientes:
        print ("***** Cliente: ", cliente, "*****")
        for servicio in servicios:
            if servicio in Clientes[cliente]['SAs']:
                if 0 in Clientes[cliente]['SAs'][servicio]:
                    for subactividad in Clientes[cliente]['SAs'][servicio][0]:
                        print ("*****Subactividad ----->> ", subactividad, "*****")
                        if Clientes[cliente]['SAs'][servicio][0][subactividad]['SUBACTIVIDAD'] != 0:
                            print ("TODO en Fijo", Clientes[cliente])
#                            CODIGO_ACTIVIDAD = 4222551
                            CODIGO_ACTIVIDAD = subactividad
                            print ("DATO en Fijo", Clientes[cliente]['SAs'][servicio][0][subactividad]['SUBACTIVIDAD'])
                            FechaFinPasada = FechaFinPTTI(str(CODIGO_ACTIVIDAD), mes, anio)
                        lineas_excel.append([origen,Clientes[cliente]['NOMBRE'],Clientes[cliente]['SAs'][servicio][0][subactividad]['ACTIVIDAD_PRINCIPAL'],subactividad,servicio,naturaleza,Clientes[cliente]['SAs'][servicio]['FIJO']])
                if 1 in Clientes[cliente]['SAs'][servicio]:
                    for subactividad in Clientes[cliente]['SAs'][servicio][1]:
                        print ("*****Subactividad ----->> ", subactividad, "*****")
                        if Clientes[cliente]['SAs'][servicio][1][subactividad]['SUBACTIVIDAD'] != 0:
                            print ("TODO en Variable", Clientes[cliente])
#                            CODIGO_ACTIVIDAD = 4222551
                            CODIGO_ACTIVIDAD = subactividad
                            print ("DATO en Variable", Clientes[cliente]['SAs'][servicio][1][subactividad]['SUBACTIVIDAD'])
                            FechaFinPasada = FechaFinPTTI(str(CODIGO_ACTIVIDAD), mes, anio)
                        lineas_excel.append([origen,Clientes[cliente]['NOMBRE'],Clientes[cliente]['SAs'][servicio][1][subactividad]['ACTIVIDAD_PRINCIPAL'],subactividad,servicio,naturaleza,Clientes[cliente]['SAs'][servicio]['VARIABLE']])
                        
    # Creamos el excel con las lineas almacenadas en la generacion de costes.
    GenerarExcel(lineas_excel,mes,anio,"facturas_tsol",['ORIGEN','NOMBRE CLIENTE','AP','SA','SERVICIO','NATURALEZA','COSTE'])
    despedida()


main()
