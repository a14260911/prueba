from datetime import datetime
#from datetime import datetime, date, time, timedelta
# Asigna datetime de la fecha actual
hoy = datetime.now()

# Asigna datetime específica
fecha1 = datetime(hoy.year, hoy.month, hoy.day, 0, 0, 0)
fecha2 = datetime(2021, 4, 29, 0, 0, 0)
diferencia = fecha2 - fecha1
print("Hoy:", fecha1)
print("Fecha2:", fecha2)
print("Entre las 2 fechas hay ", diferencia.days, "días")
