#!/home/a14/Descargas/AkamaiAPIs_env/bin/python
import requests, json

url = input("Enter a website: ")
#www.el-tiempo.net/api/json/v2/home
r = requests.get ("http://"+url)
#print ("\n", type(r.status_code), r.status_code, "\n")
if r.status_code == 200:
    resultados = r.json()
#    print (type(resultados))
    resultadosDict = json.dumps(resultados, indent = 4)
#    print (type(resultadosDict), resultadosDict)
#    print (resultados['title'], "\n\n")
#     for provincia in resultados['provincias']:
#         print (provincia['NOMBRE_PROVINCIA'], "\n")
    for ciudad in resultados['ciudades']:
        print (ciudad['name'], ciudad['temperatures'], ciudad['stateSky'])
#     for resultado, value in resultados.items():
#         if resultado == "ciudades":
#             print ("**", resultado, "**", value[1], "**", "\n")
#             
#     print ("\n", type(r.headers), r.headers, "\n")
#     print ("\n", type(r.history), "\n", r.history)
#     print ("\n", type(r.url), r.url, "\n")
#     data = r.text
#     print (type(data), "\n", data)
